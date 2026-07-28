from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import (
    AGREEMENT_POSITIONS, CLAIM_MATERIALITY, CLAIM_POSITIONS, MESSAGE_TYPES,
    PROTOCOL_VERSION, REQUIRED_CLAIM_FIELDS, REQUIRED_COVERAGE_FIELDS,
    REQUIRED_FIELDS, REQUIRED_OPEN_QUESTION_FIELDS, validate_message,
)


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

    def test_unknown_message_type(self):
        message = valid_message(); message["message_type"] = "banana"
        self.assertTrue(any("message_type must be one of" in e for e in validate_message(message)))

    def test_unknown_position(self):
        message = valid_message(); message["claims"][0]["position"] = "banana"
        self.assertTrue(any("position must be one of" in e for e in validate_message(message)))

    def test_unknown_materiality(self):
        message = valid_message(); message["claims"][0]["materiality"] = "extreme"
        self.assertTrue(any("materiality must be one of" in e for e in validate_message(message)))

    def test_claim_requires_statement(self):
        message = valid_message(); del message["claims"][0]["statement"]
        self.assertTrue(any("missing required fields: statement" in e for e in validate_message(message)))

    def test_empty_sender_rejected(self):
        message = valid_message(); message["sender"] = ""
        self.assertTrue(any("sender must be a nonempty string" in e for e in validate_message(message)))

    def test_source_requires_file_and_authority(self):
        message = valid_message()
        message["claims"][0]["sources"] = [{"file": "a.txt"}]
        self.assertTrue(any("authority must be a nonempty string" in e for e in validate_message(message)))

    def test_source_hash_must_be_hex(self):
        message = valid_message()
        message["claims"][0]["sources"] = [{"file": "a.txt", "authority": "primary", "sha256": "xyz"}]
        self.assertTrue(any("64 hexadecimal characters" in e for e in validate_message(message)))
        message["claims"][0]["sources"][0]["sha256"] = "a" * 64
        self.assertEqual(validate_message(message), [])

    def test_counterevidence_entries_are_validated(self):
        message = valid_message()
        message["claims"][0]["counterevidence"] = [{"file": ""}]
        errors = validate_message(message)
        self.assertTrue(any("counterevidence[0].file must be a nonempty string" in e for e in errors))

    def test_open_question_requires_fields(self):
        message = valid_message()
        message["open_questions"] = [{"question": "What?"}]
        errors = validate_message(message)
        self.assertTrue(any(
            "open_questions[0] missing required fields: evidence_needed, question_id" in e
            for e in errors
        ))


class SchemaAgreementTests(unittest.TestCase):
    # The stdlib validator deliberately duplicates constants from
    # RESPONSE_SCHEMA.json so workspaces need no third-party packages;
    # these tests fail loudly if the schema and the validator drift apart.
    @classmethod
    def setUpClass(cls):
        schema_path = ROOT / "protocol" / "RESPONSE_SCHEMA.json"
        cls.schema = json.loads(schema_path.read_text(encoding="utf-8"))
        cls.defs = cls.schema["$defs"]

    def test_required_fields_match(self):
        self.assertEqual(set(self.schema["required"]), REQUIRED_FIELDS)

    def test_message_types_match(self):
        self.assertEqual(set(self.schema["properties"]["message_type"]["enum"]), MESSAGE_TYPES)

    def test_claim_constraints_match(self):
        claim = self.defs["claim"]
        self.assertEqual(set(claim["required"]), REQUIRED_CLAIM_FIELDS)
        self.assertEqual(set(claim["properties"]["position"]["enum"]), CLAIM_POSITIONS)
        self.assertEqual(set(claim["properties"]["materiality"]["enum"]), CLAIM_MATERIALITY)

    def test_coverage_fields_match(self):
        self.assertEqual(set(self.defs["evidence_coverage"]["required"]), REQUIRED_COVERAGE_FIELDS)

    def test_open_question_fields_match(self):
        self.assertEqual(set(self.defs["open_question"]["required"]), REQUIRED_OPEN_QUESTION_FIELDS)

    def test_agreement_positions_are_valid_positions(self):
        self.assertTrue(AGREEMENT_POSITIONS <= CLAIM_POSITIONS)


if __name__ == "__main__":
    unittest.main()
