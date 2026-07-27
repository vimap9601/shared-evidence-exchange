from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from detect_unanswered import find_unanswered
from generate_manifest import generate_manifest
from initialize_project import initialize


def message(message_id: str, in_reply_to: str | None) -> dict:
    return {
        "protocol": "SEEP-1.0", "project_id": "TEST",
        "message_id": message_id, "in_reply_to": in_reply_to,
        "sender": "MODEL_A" if in_reply_to is None else "MODEL_B",
        "recipient": "MODEL_B" if in_reply_to is None else "MODEL_A",
        "created_at": "2026-07-27T14:00:00Z",
        "message_type": "audit_challenge" if in_reply_to is None else "response",
        "summary_markdown": "Test", "claims": [],
        "open_questions": [], "required_response": {}
    }


class ExchangeToolTests(unittest.TestCase):
    def test_initialize(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "exchange"
            initialize(destination, "TEST")
            self.assertTrue((destination / "START_HERE.md").exists())
            state = json.loads((destination / "01_GOVERNING_STATE/PROJECT_STATE_0001.json").read_text())
            self.assertEqual(state["project_id"], "TEST")

    def test_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "a.txt").write_text("hello")
            manifest = generate_manifest(evidence, "TEST")
            self.assertEqual(len(manifest["files"]), 1)
            self.assertEqual(len(manifest["files"][0]["sha256"]), 64)

    def test_unanswered_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text(json.dumps(message("EXCHANGE-0002", "EXCHANGE-0001")))
            pending = find_unanswered(root)
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0][1]["message_id"], "EXCHANGE-0002")


if __name__ == "__main__":
    unittest.main()
