#!/usr/bin/env python3
"""
Codeberg / Forgejo Pull Request Synchronization Engine
Synchronizes GitHub Pull Requests to Codeberg (create, update title/desc, open/close).
"""

import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("codeberg_sync")

METADATA_HEADER = "<!-- GH-METADATA: {payload} -->"
CB_METADATA_HEADER = "<!-- CB-METADATA: {payload} -->"


class CodebergSyncError(Exception):
    pass


class GitHubClient:
    def __init__(self, token: str, repo: str, base_url: str = "https://api.github.com"):
        self.token = token
        self.repo = repo.strip()
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "TaskRebuild-CodebergSync/2.0"
        }

    def request(self, endpoint: str, data: dict = None, method: str = "GET", max_retries: int = 3):
        url = f"{self.base_url}/repos/{self.repo}/{endpoint.lstrip('/')}"
        encoded_data = None
        req_headers = dict(self.headers)

        if data is not None:
            encoded_data = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"

        for attempt in range(1, max_retries + 1):
            req = urllib.request.Request(url, data=encoded_data, headers=req_headers, method=method)
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
                    time.sleep(retry_after)
                    continue
                logger.error(f"GitHub API Error [{method} {endpoint}]: HTTP {e.code} -> {err_body}")
                raise CodebergSyncError(f"GitHub API failed with HTTP {e.code}: {err_body}")
            except urllib.error.URLError as e:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise CodebergSyncError(f"Network error: {e.reason}")

        raise CodebergSyncError(f"Failed {method} {endpoint} after {max_retries} retries")

    def paginate(self, endpoint: str, params: dict = None, max_pages: int = 20) -> list:
        results = []
        page = 1
        query_params = dict(params or {})
        query_params["per_page"] = 100

        while page <= max_pages:
            query_params["page"] = page
            qs = urllib.parse.urlencode(query_params)
            sep = "&" if "?" in endpoint else "?"
            full_endpoint = f"{endpoint}{sep}{qs}"

            data, headers = self.request(full_endpoint, method="GET")
            if not isinstance(data, list) or not data:
                break

            results.extend(data)
            link_header = headers.get("link") or headers.get("Link")
            if not link_header or 'rel="next"' not in link_header:
                break
            page += 1

        return results


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


def build_cb_metadata(owner: str, repo: str, item_type: str, item_id: str, extra: dict = None) -> str:
    payload = {
        "repo": f"{owner}/{repo}",
        "type": item_type,
        "id": str(item_id),
        "version": 1
    }
    if extra:
        payload.update(extra)
    return CB_METADATA_HEADER.format(payload=json.dumps(payload, separators=(',', ':')))


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


def extract_cb_metadata(text: str) -> dict:
    if not text:
        return {}
    import re
    match = re.search(r"<!-- CB-METADATA: (.*?) -->", text)
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


def sync_codeberg_to_github(cb_client: CodebergClient, gh_client: GitHubClient, repo_id: str):
    """
    Bidirectional synchronization from Codeberg to GitHub:
    1. Synchronize comments from Codeberg PRs back to GitHub PRs
    2. Synchronize state transitions (closed / reopened) from Codeberg to GitHub
    Prevents infinite loops by:
    - Checking for GH-METADATA and CB-METADATA
    - Ignoring already synced comments
    """
    logger.info("Executing reverse sync: Codeberg -> GitHub (comments & state)...")

    try:
        cb_prs = cb_client.paginate("pulls", {"state": "all"})
    except Exception as e:
        logger.warning(f"Failed to fetch Codeberg PRs: {e}")
        cb_prs = []

    for pr in cb_prs:
        body = pr.get("body", "") or ""
        meta = extract_metadata(body)
        if not meta or meta.get("type") != "pull_request" or not meta.get("id"):
            continue
        if meta.get("repo_id") and str(meta.get("repo_id")) != str(repo_id):
            continue

        gh_pr_number = int(meta["id"])
        cb_pr_number = pr.get("number")
        cb_state = pr.get("state")  # "open" or "closed"

        # A. State sync
        try:
            gh_pr, _ = gh_client.request(f"pulls/{gh_pr_number}")
            gh_state = gh_pr.get("state")
            if cb_state == "closed" and gh_state == "open":
                logger.info(f"Syncing state: Closing GitHub PR #{gh_pr_number} (Codeberg PR #{cb_pr_number} is closed)")
                gh_client.request(f"pulls/{gh_pr_number}", data={"state": "closed"}, method="PATCH")
            elif cb_state == "open" and gh_state == "closed":
                logger.info(f"Syncing state: Reopening GitHub PR #{gh_pr_number} (Codeberg PR #{cb_pr_number} is open)")
                gh_client.request(f"pulls/{gh_pr_number}", data={"state": "open"}, method="PATCH")
        except Exception as e:
            logger.warning(f"Failed to inspect/sync state for GitHub PR #{gh_pr_number} from Codeberg: {e}")

        # B. Comment sync
        try:
            cb_comments = cb_client.paginate(f"issues/{cb_pr_number}/comments")
        except Exception as e:
            logger.warning(f"Failed to fetch comments for Codeberg PR #{cb_pr_number}: {e}")
            continue

        try:
            gh_comments = gh_client.paginate(f"issues/{gh_pr_number}/comments")
        except Exception as e:
            logger.warning(f"Failed to fetch comments for GitHub PR #{gh_pr_number}: {e}")
            continue

        for comment in cb_comments:
            c_body = comment.get("body", "") or ""
            if "<!-- GH-METADATA:" in c_body or "<!-- CB-METADATA:" in c_body:
                continue

            comment_id = str(comment.get("id"))
            comment_user = comment.get("user", {}).get("login", "unknown")
            comment_url = comment.get("html_url") or f"https://codeberg.org/{cb_client.repo_owner}/{cb_client.repo_name}/pulls/{cb_pr_number}#issuecomment-{comment_id}"

            needle = f'"id":"{comment_id}"'
            already_synced = any(needle in (c.get("body") or "") for c in gh_comments)
            if already_synced:
                continue

            cb_meta = build_cb_metadata(cb_client.repo_owner, cb_client.repo_name, "comment", comment_id, {"cb_pr": cb_pr_number})
            comment_payload = {
                "body": (
                    f"{cb_meta}\n"
                    f"> **@{comment_user}** (via [Codeberg PR #{cb_pr_number}]({comment_url})):\n\n"
                    f"{c_body}"
                )
            }
            logger.info(f"Syncing Codeberg comment {comment_id} to GitHub PR #{gh_pr_number}")
            try:
                gh_client.request(f"issues/{gh_pr_number}/comments", data=comment_payload, method="POST")
            except Exception as e:
                logger.error(f"Failed to post comment to GitHub PR #{gh_pr_number} from Codeberg: {e}")


def main():
    token = os.environ.get("CODEBERG_TOKEN")
    repo = os.environ.get("CODEBERG_REPO", "mukeshv-tech/taskrebulid")
    gh_token = os.environ.get("GITHUB_TOKEN")
    gh_repo = os.environ.get("GITHUB_REPOSITORY", "mukeshv-tech/Taskrebulid")
    event_name = os.environ.get("EVENT_NAME", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repo_id = os.environ.get("GITHUB_REPOSITORY_ID") or gh_repo

    if not token:
        logger.info("CODEBERG_TOKEN not configured. Skipping Codeberg sync.")
        return

    parts = repo.split("/")
    owner, repo_name = parts[0], parts[1]
    cb_client = CodebergClient(token=token, repo_owner=owner, repo_name=repo_name)
    gh_client = GitHubClient(token=gh_token, repo=gh_repo) if gh_token else None

    # Forward sync (GitHub -> Codeberg)
    if event_name == "pull_request" and event_path and os.path.exists(event_path):
        with open(event_path, "r", encoding="utf-8") as f:
            event_data = json.load(f)
        logger.info("Executing Codeberg PR sync for GitHub PR event...")
        sync_pull_request_to_codeberg(cb_client, repo_id, event_data)

    # Reverse sync (Codeberg -> GitHub)
    if gh_client:
        sync_codeberg_to_github(cb_client, gh_client, repo_id)
    else:
        logger.warning("GITHUB_TOKEN not available; skipping reverse Codeberg -> GitHub synchronization.")

    logger.info("Codeberg synchronization completed successfully.")


if __name__ == "__main__":
    main()
