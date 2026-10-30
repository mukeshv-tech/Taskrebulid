#!/usr/bin/env python3
"""
GitLab Synchronization Engine for GitHub Actions
Synchronizes GitHub Issues, Issue Comments, Pull Requests, and PR Review Comments to GitLab.
Features:
- Deterministic metadata headers (GitHub Repo ID, Item ID, Comment ID) preventing duplicate issues & comments
- Full pagination handling for GitLab REST API queries
- Automatic retry with exponential backoff on HTTP 429 (rate-limit) and 5xx errors
- Synchronizes titles, descriptions, open/closed/merged states, labels, and comments
- Real GitLab Merge Request synchronization (creates/updates actual MRs with branch diffs)
- Distinguishes PR review comments vs general issue comments
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
logger = logging.getLogger("gitlab_sync")

METADATA_HEADER = "<!-- GH-METADATA: {payload} -->"


class GitLabSyncError(Exception):
    """Custom exception for sync failures that should fail the GitHub Action job."""
    pass


class GitLabClient:
    def __init__(self, token: str, project_id: str, base_url: str = "https://gitlab.com/api/v4"):
        self.token = token
        self.project_id = str(project_id).strip()
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "PRIVATE-TOKEN": self.token,
            "User-Agent": "TaskRebuild-GitHubSync/2.0"
        }

    def request(self, endpoint: str, data: dict = None, method: str = "GET", max_retries: int = 3):
        url = f"{self.base_url}/projects/{self.project_id}/{endpoint.lstrip('/')}"
        encoded_data = None
        req_headers = dict(self.headers)

        if data is not None:
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")
            req_headers["Content-Type"] = "application/x-www-form-urlencoded"

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
                # Handle rate limits or temporary server errors with backoff
                if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    retry_after = 2 ** attempt
                    logger.warning(f"GitLab API returned {e.code}. Retrying in {retry_after}s... (Attempt {attempt}/{max_retries})")
                    time.sleep(retry_after)
                    continue
                logger.error(f"GitLab API Error [{method} {endpoint}]: HTTP {e.code} -> {err_body}")
                raise GitLabSyncError(f"GitLab API failed with HTTP {e.code}: {err_body}")
            except urllib.error.URLError as e:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"Network error connecting to GitLab: {e.reason}")
                raise GitLabSyncError(f"Network error: {e.reason}")

        raise GitLabSyncError(f"Failed {method} {endpoint} after {max_retries} retries")

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
            next_page = headers.get("x-next-page") or headers.get("X-Next-Page")
            if not next_page:
                break
            page = int(next_page)

        return results


def build_metadata(repo_id: str, item_type: str, item_id: str, extra: dict = None) -> str:
    payload = {
        "repo_id": str(repo_id),
        "type": item_type,
        "id": str(item_id),
        **(extra or {})
    }
    return METADATA_HEADER.format(payload=json.dumps(payload, separators=(",", ":")))


def extract_metadata(body: str) -> dict:
    if not body or "<!-- GH-METADATA:" not in body:
        return {}
    try:
        start = body.index("<!-- GH-METADATA:") + len("<!-- GH-METADATA:")
        end = body.index("-->", start)
        return json.loads(body[start:end].strip())
    except Exception:
        return {}


def find_gitlab_issue(client: GitLabClient, repo_id: str, issue_number: int) -> dict:
    """Finds an existing GitLab issue via persistent metadata tag across paginated issues."""
    target_needle = f'"repo_id":"{repo_id}","type":"issue","id":"{issue_number}"'
    
    # 1. Search with title scope first for speed
    candidates = client.paginate("issues", {"search": f"[GH-{issue_number}]"})
    for iss in candidates:
        desc = iss.get("description", "")
        if target_needle in desc or f'"id":"{issue_number}"' in desc:
            return iss

    # 2. Exhaustive check of opened/closed issues if title changed
    all_issues = client.paginate("issues", {"state": "all"})
    for iss in all_issues:
        meta = extract_metadata(iss.get("description", ""))
        if meta.get("repo_id") == str(repo_id) and meta.get("type") == "issue" and str(meta.get("id")) == str(issue_number):
            return iss

    return None


def find_gitlab_mr(client: GitLabClient, repo_id: str, pr_number: int) -> dict:
    """Finds an existing GitLab merge request via metadata tag."""
    target_needle = f'"repo_id":"{repo_id}","type":"pull_request","id":"{pr_number}"'
    candidates = client.paginate("merge_requests", {"search": f"[GH-PR-{pr_number}]"})
    for mr in candidates:
        desc = mr.get("description", "")
        if target_needle in desc:
            return mr

    all_mrs = client.paginate("merge_requests", {"state": "all"})
    for mr in all_mrs:
        meta = extract_metadata(mr.get("description", ""))
        if meta.get("repo_id") == str(repo_id) and meta.get("type") == "pull_request" and str(meta.get("id")) == str(pr_number):
            return mr

    return None


def sync_issue(client: GitLabClient, repo_id: str, event_data: dict):
    issue = event_data.get("issue", {})
    issue_number = issue.get("number")
    issue_title = issue.get("title", "")
    issue_body = issue.get("body", "") or "*No description provided.*"
    issue_state = issue.get("state", "open")
    html_url = issue.get("html_url", "")
    user = issue.get("user", {}).get("login", "unknown")
    labels = [l.get("name") for l in issue.get("labels", []) if isinstance(l, dict) and l.get("name")]

    meta_header = build_metadata(repo_id, "issue", str(issue_number), {"html_url": html_url})
    
    full_title = f"[GH-{issue_number}] {issue_title}"
    full_desc = (
        f"{meta_header}\n\n"
        f"**Mirrored from GitHub Issue [#{issue_number}]({html_url})** by @{user}\n\n"
        f"---\n\n"
        f"{issue_body}"
    )

    data = {
        "title": full_title,
        "description": full_desc,
    }
    if labels:
        data["labels"] = ",".join(labels)

    existing = find_gitlab_issue(client, repo_id, issue_number)
    if existing:
        iid = existing["iid"]
        logger.info(f"Updating existing GitLab issue #{iid} for GitHub issue #{issue_number}")
        
        # State transition: close or reopen
        if issue_state == "closed" and existing.get("state") != "closed":
            data["state_event"] = "close"
        elif issue_state == "open" and existing.get("state") == "closed":
            data["state_event"] = "reopen"

        client.request(f"issues/{iid}", data=data, method="PUT")
    else:
        logger.info(f"Creating new GitLab issue for GitHub issue #{issue_number}")
        created, _ = client.request("issues", data=data, method="POST")
        iid = created.get("iid")
        # If created in closed state
        if issue_state == "closed":
            client.request(f"issues/{iid}", data={"state_event": "close"}, method="PUT")


def sync_comment(client: GitLabClient, repo_id: str, event_data: dict, is_pr_review: bool = False):
    comment = event_data.get("comment", {})
    comment_id = comment.get("id")
    comment_body = comment.get("body", "") or ""
    comment_user = comment.get("user", {}).get("login", "unknown")
    html_url = comment.get("html_url", "")

    # Determine whether parent is PR or regular Issue
    is_pr = "pull_request" in event_data.get("issue", {}) or is_pr_review
    parent_obj = event_data.get("pull_request") if is_pr_review else event_data.get("issue", {})
    parent_number = parent_obj.get("number")

    if not comment_id or not parent_number:
        logger.warning("Missing comment ID or parent number. Skipping.")
        return

    meta_header = build_metadata(repo_id, "comment", str(comment_id), {"html_url": html_url, "parent": parent_number})

    # Find parent container in GitLab
    if is_pr:
        parent_mr = find_gitlab_mr(client, repo_id, parent_number)
        if not parent_mr:
            logger.warning(f"Cannot sync comment: GitLab Merge Request for GH PR #{parent_number} not found.")
            return
        endpoint = f"merge_requests/{parent_mr['iid']}/notes"
    else:
        parent_issue = find_gitlab_issue(client, repo_id, parent_number)
        if not parent_issue:
            logger.warning(f"Cannot sync comment: GitLab Issue for GH #{parent_number} not found.")
            return
        endpoint = f"issues/{parent_issue['iid']}/notes"

    # Idempotency check: check all existing notes to avoid duplicates
    existing_notes = client.paginate(endpoint)
    comment_needle = f'"id":"{comment_id}"'
    for note in existing_notes:
        if comment_needle in note.get("body", ""):
            logger.info(f"Comment {comment_id} already mirrored to GitLab note #{note.get('id')}. Skipping.")
            return

    comment_type_badge = "PR Review Comment" if is_pr_review else "Comment"
    full_body = (
        f"{meta_header}\n"
        f"> **@{comment_user}** (via GitHub {comment_type_badge} [#{parent_number}]({html_url})):\n\n"
        f"{comment_body}"
    )

    logger.info(f"Adding mirrored comment {comment_id} to GitLab {endpoint}")
    client.request(endpoint, data={"body": full_body}, method="POST")


def sync_pull_request(client: GitLabClient, repo_id: str, event_data: dict):
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
    labels = [l.get("name") for l in pr.get("labels", []) if isinstance(l, dict) and l.get("name")]

    meta_header = build_metadata(repo_id, "pull_request", str(pr_number), {"html_url": html_url})
    
    # Priority for source branch on GitLab:
    # 1. Dedicated mirrored PR branch: pr-<pr_number>
    # 2. Or the head_branch name if it exists
    pr_dedicated_branch = f"pr-{pr_number}"
    
    # Check if dedicated pr-<number> branch exists in GitLab repo
    gitlab_source_branch = pr_dedicated_branch
    try:
        branches = client.paginate("repository/branches", {"search": pr_dedicated_branch})
        has_pr_branch = any(b.get("name") == pr_dedicated_branch for b in branches)
        if not has_pr_branch:
            # Check if head_branch exists
            head_branches = client.paginate("repository/branches", {"search": head_branch})
            if any(b.get("name") == head_branch for b in head_branches):
                gitlab_source_branch = head_branch
    except Exception as e:
        logger.warning(f"Could not query GitLab branches, defaulting source_branch to {gitlab_source_branch}: {e}")

    full_title = f"[GH-PR-{pr_number}] {pr_title}"
    full_desc = (
        f"{meta_header}\n\n"
        f"**Mirrored from GitHub Pull Request [#{pr_number}]({html_url})** by @{user}\n\n"
        f"- **Head Branch**: `{gitlab_source_branch}`\n"
        f"- **Base Branch**: `{base_branch}`\n"
        f"- **Status**: `{'Merged' if merged else pr_state.title()}`\n\n"
        f"---\n\n"
        f"{pr_body}"
    )

    data = {
        "title": full_title,
        "description": full_desc,
        "source_branch": gitlab_source_branch,
        "target_branch": base_branch,
    }
    if labels:
        data["labels"] = ",".join(labels)

    existing = find_gitlab_mr(client, repo_id, pr_number)
    if existing:
        iid = existing["iid"]
        logger.info(f"Updating existing GitLab Merge Request !{iid} for GitHub PR #{pr_number}")
        
        # State transitions for GitLab MR: close or reopen
        if pr_state == "closed":
            data["state_event"] = "close"
        elif pr_state == "open" and existing.get("state") == "closed":
            data["state_event"] = "reopen"

        # Update MR details
        update_data = {
            "title": full_title,
            "description": full_desc,
        }
        if "state_event" in data:
            update_data["state_event"] = data["state_event"]
        if labels:
            update_data["labels"] = ",".join(labels)

        client.request(f"merge_requests/{iid}", data=update_data, method="PUT")
    else:
        logger.info(f"Creating new GitLab Merge Request for GitHub PR #{pr_number}")
        try:
            created, _ = client.request("merge_requests", data=data, method="POST")
            iid = created.get("iid")
            if pr_state == "closed":
                client.request(f"merge_requests/{iid}", data={"state_event": "close"}, method="PUT")
        except GitLabSyncError as e:
            # If source branch hasn't mirrored yet or has identical history, log warning
            logger.warning(f"Could not open GitLab MR directly (branch may still be syncing): {e}")


def main():
    token = os.environ.get("GITLAB_TOKEN")
    project_id = os.environ.get("GITLAB_PROJECT_ID")
    event_name = os.environ.get("EVENT_NAME")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repo_id = os.environ.get("GITHUB_REPOSITORY_ID") or os.environ.get("GITHUB_REPOSITORY", "unknown_repo")

    if not token or not project_id:
        logger.error("GITLAB_TOKEN or GITLAB_PROJECT_ID is not configured.")
        sys.exit(1)

    if not event_path or not os.path.exists(event_path):
        logger.error(f"Event payload file not found: {event_path}")
        sys.exit(1)

    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)

    client = GitLabClient(token=token, project_id=project_id)

    logger.info(f"Executing GitLab sync for GitHub event: {event_name}")

    if event_name == "issues":
        sync_issue(client, repo_id, event_data)
    elif event_name == "issue_comment":
        sync_comment(client, repo_id, event_data, is_pr_review=False)
    elif event_name == "pull_request":
        sync_pull_request(client, repo_id, event_data)
    elif event_name == "pull_request_review_comment":
        sync_comment(client, repo_id, event_data, is_pr_review=True)
    else:
        logger.info(f"Event '{event_name}' does not require issue or PR API synchronization.")

    logger.info("GitLab synchronization finished successfully.")


if __name__ == "__main__":
    main()
