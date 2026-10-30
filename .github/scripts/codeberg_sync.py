#!/usr/bin/env python3
"""
Codeberg / Forgejo Pull Request Synchronization Engine
Synchronizes GitHub Pull Requests to Codeberg (create, update title/desc, open/close).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("codeberg_sync")

METADATA_HEADER = "<!-- GH-METADATA: {payload} -->"


class CodebergSyncError(Exception):
    pass


class CodebergClient:
    def __init__(self, token: str, repo_owner: str, repo_name: str, base_url: str = "https://codeberg.org/api/v1"):
        self.token = token.strip()
        self.repo_owner = repo_owner.strip()
        self.repo_name = repo_name.strip()
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "TaskRebuild-GitHubSync/2.0"
        }

    def request(self, endpoint: str, data: dict = None, method: str = "GET", max_retries: int = 3):
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/{endpoint.lstrip('/')}"
        encoded_data = None
        if data is not None:
            encoded_data = json.dumps(data).encode("utf-8")

        for attempt in range(1, max_retries + 1):
            req = urllib.request.Request(url, data=encoded_data, headers=self.headers, method=method)
            try:
                with urllib.request.urlopen(req) as resp:
                    resp_body = resp.read().decode("utf-8")
                    headers = dict(resp.info())
                    parsed = json.loads(resp_body) if resp_body.strip() else {}
                    return parsed, headers
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    retry_after = 2 ** attempt
                    logger.warning(f"Codeberg API returned {e.code}. Retrying in {retry_after}s... (Attempt {attempt}/{max_retries})")
                    time.sleep(retry_after)
                    continue
                logger.error(f"Codeberg API Error [{method} {endpoint}]: HTTP {e.code} -> {err_body}")
                raise CodebergSyncError(f"Codeberg API failed with HTTP {e.code}: {err_body}")
            except urllib.error.URLError as e:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"Network error connecting to Codeberg: {e.reason}")
                raise CodebergSyncError(f"Network error: {e.reason}")

        raise CodebergSyncError(f"Failed {method} {endpoint} after {max_retries} retries")

    def paginate(self, endpoint: str, params: dict = None, max_pages: int = 20) -> list:
        results = []
        page = 1
        query_params = dict(params or {})
        query_params["limit"] = 50

        while page <= max_pages:
            query_params["page"] = page
            qs = urllib.parse.urlencode(query_params)
            sep = "&" if "?" in endpoint else "?"
            full_endpoint = f"{endpoint}{sep}{qs}"

            data, headers = self.request(full_endpoint, method="GET")
            if not isinstance(data, list) or not data:
                break

            results.extend(data)
            if len(data) < query_params["limit"]:
                break
            page += 1

        return results


def build_metadata(repo_id: str, item_type: str, item_id: str, extra: dict = None) -> str:
    payload = {
        "repo_id": str(repo_id),
        "type": item_type,
        "id": str(item_id),
        "version": 1
    }
    if extra:
        payload.update(extra)
    return METADATA_HEADER.format(payload=json.dumps(payload, separators=(',', ':')))


def extract_metadata(text: str) -> dict:
    if not text:
        return {}
    import re
    match = re.search(r"<!-- GH-METADATA: (.*?) -->", text)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except Exception:
        return {}


def find_codeberg_pr(client: CodebergClient, repo_id: str, pr_number: int) -> dict:
    target_needle = f'"id":"{pr_number}"'
    all_prs = client.paginate("pulls", {"state": "all"})
    for pr in all_prs:
        body = pr.get("body", "")
        if target_needle in body:
            meta = extract_metadata(body)
            if meta.get("repo_id") == str(repo_id) and meta.get("type") == "pull_request" and str(meta.get("id")) == str(pr_number):
                return pr
    return None


def sync_pull_request_to_codeberg(client: CodebergClient, repo_id: str, event_data: dict):
    pr = event_data.get("pull_request", {})
    pr_number = pr.get("number")
    pr_title = pr.get("title", "")
    pr_body = pr.get("body", "") or "*No description provided.*"
    pr_state = pr.get("state", "open")
    merged = pr.get("merged", False)
    head_branch = pr.get("head", {}).get("ref", f"pr-{pr_number}")
    base_branch = pr.get("base", {}).get("ref", "main")
    html_url = pr.get("html_url", "")
    user = pr.get("user", {}).get("login", "unknown")

    meta_header = build_metadata(repo_id, "pull_request", str(pr_number), {"html_url": html_url})
    pr_dedicated_branch = f"pr-{pr_number}"

    # Verify head branch in Codeberg
    codeberg_source_branch = pr_dedicated_branch
    try:
        branches = client.paginate("branches")
        branch_names = [b.get("name") for b in branches if isinstance(b, dict)]
        if pr_dedicated_branch in branch_names:
            codeberg_source_branch = pr_dedicated_branch
        elif head_branch in branch_names:
            codeberg_source_branch = head_branch
    except Exception as e:
        logger.warning(f"Could not query Codeberg branches: {e}")

    full_title = f"[GH-PR-{pr_number}] {pr_title}"
    full_desc = (
        f"{meta_header}\n\n"
        f"**Mirrored from GitHub Pull Request [#{pr_number}]({html_url})** by @{user}\n\n"
        f"- **Head Branch**: `{codeberg_source_branch}`\n"
        f"- **Base Branch**: `{base_branch}`\n"
        f"- **Status**: `{'Merged' if merged else pr_state.title()}`\n\n"
        f"---\n\n"
        f"{pr_body}"
    )

    existing = find_codeberg_pr(client, repo_id, pr_number)
    if existing:
        index = existing.get("number") or existing.get("id")
        logger.info(f"Updating existing Codeberg PR #{index} for GitHub PR #{pr_number}")
        patch_data = {
            "title": full_title,
            "body": full_desc,
        }
        # Manage open/closed state
        if pr_state == "closed":
            patch_data["state"] = "closed"
        elif pr_state == "open" and existing.get("state") == "closed":
            patch_data["state"] = "open"

        client.request(f"pulls/{index}", data=patch_data, method="PATCH")
    else:
        logger.info(f"Creating new Codeberg Pull Request for GitHub PR #{pr_number}")
        create_data = {
            "title": full_title,
            "body": full_desc,
            "head": codeberg_source_branch,
            "base": base_branch
        }
        try:
            created, _ = client.request("pulls", data=create_data, method="POST")
            index = created.get("number") or created.get("id")
            if pr_state == "closed" and index:
                client.request(f"pulls/{index}", data={"state": "closed"}, method="PATCH")
        except CodebergSyncError as e:
            logger.warning(f"Could not open Codeberg PR (branches may be identical or syncing): {e}")


def main():
    token = os.environ.get("CODEBERG_TOKEN")
    repo = os.environ.get("CODEBERG_REPO", "mukeshv-tech/taskrebulid")
    event_name = os.environ.get("EVENT_NAME")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repo_id = os.environ.get("GITHUB_REPOSITORY_ID") or os.environ.get("GITHUB_REPOSITORY", "unknown_repo")

    if not token:
        logger.info("CODEBERG_TOKEN not configured. Skipping Codeberg PR sync.")
        return

    if not event_path or not os.path.exists(event_path):
        logger.error(f"Event payload file not found: {event_path}")
        sys.exit(1)

    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)

    if event_name != "pull_request":
        logger.info(f"Event '{event_name}' is not a pull request event. Skipping Codeberg PR sync.")
        return

    parts = repo.split("/")
    owner, repo_name = parts[0], parts[1]
    client = CodebergClient(token=token, repo_owner=owner, repo_name=repo_name)

    logger.info(f"Executing Codeberg PR sync for GitHub PR event...")
    sync_pull_request_to_codeberg(client, repo_id, event_data)
    logger.info("Codeberg PR synchronization completed successfully.")


if __name__ == "__main__":
    main()
