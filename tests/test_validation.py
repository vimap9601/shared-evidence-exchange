from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import validate_message


def valid_message() -> dict:
    return {
        "protocol": "SEEP-1.0", "project_id": "TEST",
        "message_id": "EXCHANGE-0001", "in_reply_to": None,
        "sender": "MODEL_A", "recipient": "MODEL_B",
        "created_at": "2026-07-27T14:00:00Z",
        "message_type": "audit_challenge", "summary_markdown": "Test",
        "claims": [{"claim_id": "C-1", "statement": "Test claim",
                    "position": "supported", "confidence": 0.8,
                    "materiality": "high", "reasoning_summary": "Test",
                    "sources": []}],
        "open_questions": [], "required_response": {}
    }


class ValidationTests(unittest.TestCase):
    def test_valid_message(self):
        self.assertEqual(validate_message(valid_message()), [])

    def test_missing_field(self):
        message = valid_message(); del message["recipient"]
        self.assertTrue(any("recipient" in e for e in validate_message(message)))

    def test_self_reply(self):
        message = valid_message(); message["in_reply_to"] = message["message_id"]
        self.assertTrue(any("reply to itself" in e for e in validate_message(message)))

    def test_invalid_confidence(self):
        message = valid_message(); message["claims"][0]["confidence"] = 2
        self.assertTrue(any("between 0 and 1" in e for e in validate_message(message)))


if __name__ == "__main__":
    unittest.main()
