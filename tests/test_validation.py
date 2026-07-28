from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import PROTOCOL_VERSION, validate_message


def valid_message() -> dict:
    return {
        "protocol": PROTOCOL_VERSION, "project_id": "TEST",
        "message_id": "EXCHANGE-0001", "in_reply_to": None,
        "sender": "MODEL_A", "recipient": "MODEL_B",
        "created_at": "2026-07-27T14:00:00Z",
        "message_type": "audit_challenge", "summary_markdown": "Test",
        "evidence_coverage": {
            "manifest_file": "EVIDENCE_MANIFEST.json", "reviewer": "MODEL_A",
            "inventory_complete": True,
            "files_total": 1, "files_opened": 1, "files_parsed": 1,
            "files_visually_inspected": 0, "files_not_opened": 0,
            "folders_not_recursively_reviewed": [], "unsupported_file_types": [],
            "archives_not_inspected": [], "known_connector_limitations": [],
            "missing_claim_gate_satisfied": True
        },
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

    def test_invalid_coverage_counts(self):
        message = valid_message(); message["evidence_coverage"]["files_not_opened"] = 1
        self.assertTrue(any("must equal files_total" in e for e in validate_message(message)))

    def test_reviewer_must_match_sender(self):
        message = valid_message()
        message["evidence_coverage"]["reviewer"] = "MODEL_B"
        self.assertTrue(any("reviewer must equal sender" in e for e in validate_message(message)))

    def test_reviewer_is_required(self):
        message = valid_message()
        del message["evidence_coverage"]["reviewer"]
        self.assertTrue(any("reviewer" in e for e in validate_message(message)))

    def test_agreement_requires_sources(self):
        message = valid_message()
        message["message_type"] = "response"
        message["in_reply_to"] = "EXCHANGE-0000"
        message["claims"][0]["position"] = "agree"
        errors = validate_message(message)
        self.assertTrue(any("requires at least one source" in e for e in errors))
        message["claims"][0]["sources"] = [{"file": "a.txt", "authority": "primary"}]
        self.assertEqual(validate_message(message), [])

    def test_partial_agreement_requires_sources(self):
        message = valid_message()
        message["claims"][0]["position"] = "partially_agree"
        self.assertTrue(any("requires at least one source" in e for e in validate_message(message)))

    def test_correction_requires_target(self):
        message = valid_message()
        message["message_type"] = "correction"
        self.assertTrue(any("corrects_message_id" in e for e in validate_message(message)))
        message["corrects_message_id"] = message["message_id"]
        self.assertTrue(any("cannot correct itself" in e for e in validate_message(message)))
        message["message_id"] = "EXCHANGE-0004"
        self.assertEqual(validate_message(message), [])

    def test_corrects_field_restricted_to_corrections(self):
        message = valid_message()
        message["corrects_message_id"] = "EXCHANGE-0000"
        self.assertTrue(any("only allowed on correction" in e for e in validate_message(message)))


if __name__ == "__main__":
    unittest.main()
