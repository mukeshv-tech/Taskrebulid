import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".github", "scripts")))
from codeberg_sync import (
    build_metadata,
    extract_metadata,
    find_codeberg_pr,
    sync_pull_request_to_codeberg
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

if __name__ == "__main__":
    unittest.main()
