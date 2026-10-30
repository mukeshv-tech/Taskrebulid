import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".github", "scripts")))
from gitlab_sync import (
    build_metadata,
    extract_metadata,
    find_gitlab_issue,
    sync_issue,
    sync_comment,
    sync_pull_request
)

class TestGitLabSync(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.repo_id = "12345678"

    def test_metadata_serialization(self):
        meta = build_metadata("repo_1", "issue", "42", {"test": "val"})
        self.assertIn("<!-- GH-METADATA:", meta)
        parsed = extract_metadata(meta)
        self.assertEqual(parsed["repo_id"], "repo_1")
        self.assertEqual(parsed["type"], "issue")
        self.assertEqual(parsed["id"], "42")
        self.assertEqual(parsed["test"], "val")

    def test_find_gitlab_issue_pagination_and_match(self):
        # Mock paginate returning candidate with metadata
        meta = build_metadata(self.repo_id, "issue", "99")
        self.mock_client.paginate.return_value = [
            {"iid": 1, "description": "Unrelated issue"},
            {"iid": 2, "description": f"Some text\n{meta}\nMore text"}
        ]
        found = find_gitlab_issue(self.mock_client, self.repo_id, 99)
        self.assertIsNotNone(found)
        self.assertEqual(found["iid"], 2)

    def test_sync_issue_update_existing_no_duplicate(self):
        # Issue already exists in GitLab -> should PUT, not POST
        meta = build_metadata(self.repo_id, "issue", "15")
        self.mock_client.paginate.return_value = [{"iid": 5, "description": meta, "state": "opened"}]
        
        event_data = {
            "issue": {
                "number": 15,
                "title": "Renamed Title",
                "body": "Updated content",
                "state": "closed",
                "html_url": "https://github.com/org/repo/issues/15",
                "user": {"login": "mukesh"}
            }
        }
        sync_issue(self.mock_client, self.repo_id, event_data)
        
        # Verify PUT was called with state_event = close
        self.mock_client.request.assert_called_once()
        args, kwargs = self.mock_client.request.call_args
        self.assertEqual(args[0], "issues/5")
        self.assertEqual(kwargs["method"], "PUT")
        self.assertEqual(kwargs["data"]["state_event"], "close")

    def test_sync_comment_idempotency(self):
        # Parent issue exists
        meta_issue = build_metadata(self.repo_id, "issue", "20")
        meta_comment = build_metadata(self.repo_id, "comment", "999")

        # Mock issue exists
        self.mock_client.paginate.side_effect = [
            [{"iid": 10, "description": meta_issue}],  # find_gitlab_issue
            [{"id": 101, "body": f"Comment text\n{meta_comment}"}]  # existing notes
        ]

        event_data = {
            "issue": {"number": 20},
            "comment": {
                "id": 999,
                "body": "Duplicate comment trigger",
                "user": {"login": "mukesh"},
                "html_url": "https://github.com/org/repo/issues/20#issuecomment-999"
            }
        }

        sync_comment(self.mock_client, self.repo_id, event_data, is_pr_review=False)
        # Should not POST a new note since note already contains comment ID 999
        self.mock_client.request.assert_not_called()

    def test_sync_pull_request_creation(self):
        # PR does not exist yet -> should POST merge_request
        self.mock_client.paginate.return_value = []
        self.mock_client.request.return_value = ({"iid": 7}, {})

        event_data = {
            "pull_request": {
                "number": 3,
                "title": "Feature branch",
                "body": "PR description",
                "state": "open",
                "merged": False,
                "head": {"ref": "feature-x", "repo": {"fork": False}},
                "base": {"ref": "main"},
                "html_url": "https://github.com/org/repo/pull/3",
                "user": {"login": "mukesh"}
            }
        }

        sync_pull_request(self.mock_client, self.repo_id, event_data)
        self.mock_client.request.assert_called_once()
        args, kwargs = self.mock_client.request.call_args
        self.assertEqual(args[0], "merge_requests")
        self.assertEqual(kwargs["method"], "POST")
        self.assertEqual(kwargs["data"]["source_branch"], "pr-3")
        self.assertEqual(kwargs["data"]["target_branch"], "main")

if __name__ == "__main__":
    unittest.main()
