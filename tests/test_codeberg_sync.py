import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".github", "scripts")))
from codeberg_sync import (
    build_metadata,
    build_cb_metadata,
    extract_metadata,
    extract_cb_metadata,
    find_codeberg_pr,
    sync_pull_request_to_codeberg,
    sync_codeberg_to_github
)

class TestCodebergSync(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.repo_id = "12345678"

    def test_metadata_roundtrip(self):
        meta = build_metadata(self.repo_id, "pull_request", "14", {"html_url": "https://github.com/org/repo/pull/14"})
        self.assertIn("<!-- GH-METADATA:", meta)
        parsed = extract_metadata(meta)
        self.assertEqual(parsed["repo_id"], self.repo_id)
        self.assertEqual(parsed["type"], "pull_request")
        self.assertEqual(parsed["id"], "14")

    def test_find_codeberg_pr(self):
        meta = build_metadata(self.repo_id, "pull_request", "14")
        self.mock_client.paginate.return_value = [
            {"number": 1, "body": "unrelated"},
            {"number": 2, "body": f"Description\n{meta}"}
        ]
        found = find_codeberg_pr(self.mock_client, self.repo_id, 14)
        self.assertIsNotNone(found)
        self.assertEqual(found["number"], 2)

    def test_sync_pull_request_open(self):
        self.mock_client.reset_mock()
        self.mock_client.paginate.side_effect = [
            [], # find_codeberg_pr
            [{"name": "pr-14"}, {"name": "main"}] # branches
        ]
        self.mock_client.request.return_value = ({"number": 5}, {})

        event_data = {
            "pull_request": {
                "number": 14,
                "title": "New feature",
                "body": "PR test body",
                "state": "open",
                "head": {"ref": "Testing-Branch"},
                "base": {"ref": "main"},
                "html_url": "https://github.com/org/repo/pull/14",
                "user": {"login": "mukesh"}
            }
        }
        sync_pull_request_to_codeberg(self.mock_client, self.repo_id, event_data)
        self.mock_client.request.assert_called_once()
        args, kwargs = self.mock_client.request.call_args
        self.assertEqual(args[0], "pulls")
        self.assertEqual(kwargs["method"], "POST")
        self.assertEqual(kwargs["data"]["head"], "pr-14")
        self.assertEqual(kwargs["data"]["base"], "main")

    def test_sync_pull_request_close(self):
        self.mock_client.reset_mock()
        meta = build_metadata(self.repo_id, "pull_request", "14")
        self.mock_client.paginate.side_effect = [
            [{"name": "pr-14"}], # branches in sync_pull_request_to_codeberg
            [{"number": 5, "body": meta, "state": "open"}] # all_prs in find_codeberg_pr
        ]
        self.mock_client.request.return_value = ({"number": 5, "state": "closed"}, {})

        event_data = {
            "pull_request": {
                "number": 14,
                "title": "New feature",
                "body": "PR test body",
                "state": "closed",
                "head": {"ref": "Testing-Branch"},
                "base": {"ref": "main"},
                "html_url": "https://github.com/org/repo/pull/14",
                "user": {"login": "mukesh"}
            }
        }
        sync_pull_request_to_codeberg(self.mock_client, self.repo_id, event_data)
        self.mock_client.request.assert_called_once()
        args, kwargs = self.mock_client.request.call_args
        self.assertEqual(args[0], "pulls/5")
        self.assertEqual(kwargs["method"], "PATCH")
        self.assertEqual(kwargs["data"]["state"], "closed")

    def test_cb_metadata_serialization(self):
        meta = build_cb_metadata("mukeshv-tech", "taskrebulid", "comment", "123")
        self.assertIn("<!-- CB-METADATA:", meta)
        parsed = extract_cb_metadata(meta)
        self.assertEqual(parsed["repo"], "mukeshv-tech/taskrebulid")
        self.assertEqual(parsed["id"], "123")
        self.assertEqual(parsed["type"], "comment")

    def test_sync_codeberg_to_github_comment(self):
        mock_gh = MagicMock()
        mock_gh.repo = "mukeshv-tech/Taskrebulid"
        mock_gh.request.return_value = ({"state": "open"}, {})
        mock_gh.paginate.return_value = []

        self.mock_client.repo_owner = "mukeshv-tech"
        self.mock_client.repo_name = "taskrebulid"
        meta = build_metadata(self.repo_id, "pull_request", "88")
        self.mock_client.paginate.side_effect = [
            # pulls
            [{"number": 1, "body": f"PR description\n{meta}", "state": "open"}],
            # comments on PR 1
            [{"id": 404, "body": "Hello from Codeberg!", "user": {"login": "codeberg_dev"}}],
        ]

        sync_codeberg_to_github(self.mock_client, mock_gh, self.repo_id)

        post_calls = [call for call in mock_gh.request.call_args_list if call[1].get("method") == "POST"]
        self.assertEqual(len(post_calls), 1)
        self.assertEqual(post_calls[0][0][0], "issues/88/comments")
        self.assertIn('"id":"404"', post_calls[0][1]["data"]["body"])
        self.assertIn("@codeberg_dev", post_calls[0][1]["data"]["body"])
        self.assertIn("Hello from Codeberg!", post_calls[0][1]["data"]["body"])

    def test_sync_codeberg_to_github_loop_prevention(self):
        mock_gh = MagicMock()
        mock_gh.repo = "mukeshv-tech/Taskrebulid"
        mock_gh.request.return_value = ({"state": "open"}, {})

        self.mock_client.repo_owner = "mukeshv-tech"
        self.mock_client.repo_name = "taskrebulid"
        meta = build_metadata(self.repo_id, "pull_request", "88")
        self.mock_client.paginate.side_effect = [
            # pulls
            [{"number": 1, "body": f"PR description\n{meta}", "state": "open"}],
            # comments with metadata echo
            [
                {"id": 1, "body": "<!-- GH-METADATA: {\"id\": \"1\"} -->\nComment"},
                {"id": 2, "body": "<!-- CB-METADATA: {\"id\": \"2\"} -->\nEcho"},
                {"id": 3, "body": "Already mirrored", "user": {"login": "dev"}}
            ],
        ]
        # Already mirrored on GitHub
        mock_gh.paginate.return_value = [{"body": "<!-- CB-METADATA: {\"id\":\"3\"} -->\nDev comment"}]

        sync_codeberg_to_github(self.mock_client, mock_gh, self.repo_id)

        post_calls = [call for call in mock_gh.request.call_args_list if call[1].get("method") == "POST"]
        self.assertEqual(len(post_calls), 0)

if __name__ == "__main__":
    unittest.main()
