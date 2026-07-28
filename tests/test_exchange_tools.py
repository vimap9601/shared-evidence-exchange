from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_evidence_coverage import build_coverage_report
from common import PROTOCOL_VERSION
from detect_unanswered import find_unanswered
from generate_manifest import generate_manifest
from initialize_project import initialize
from next_message_id import suggest_next_id
from scaffold_message import scaffold_message
from validate_exchange import validate_exchange


def coverage(reviewer: str) -> dict:
    return {
        "manifest_file": "EVIDENCE_MANIFEST.json",
        "reviewer": reviewer,
        "inventory_complete": True,
        "files_total": 0,
        "files_opened": 0,
        "files_parsed": 0,
        "files_visually_inspected": 0,
        "files_not_opened": 0,
        "folders_not_recursively_reviewed": [],
        "unsupported_file_types": [],
        "archives_not_inspected": [],
        "known_connector_limitations": [],
        "missing_claim_gate_satisfied": True,
    }


def message(
    message_id: str,
    in_reply_to: str | None,
    sender: str | None = None,
    message_type: str | None = None,
    corrects: str | None = None,
    claims: list | None = None,
) -> dict:
    if sender is None:
        sender = "MODEL_A" if in_reply_to is None else "MODEL_B"
    recipient = "MODEL_B" if sender == "MODEL_A" else "MODEL_A"
    if message_type is None:
        message_type = "audit_challenge" if in_reply_to is None else "response"
    data = {
        "protocol": PROTOCOL_VERSION, "project_id": "TEST",
        "message_id": message_id, "in_reply_to": in_reply_to,
        "sender": sender, "recipient": recipient,
        "created_at": "2026-07-27T14:00:00Z",
        "message_type": message_type,
        "summary_markdown": "Test", "evidence_coverage": coverage(sender),
        "claims": claims or [],
        "open_questions": [], "required_response": {}
    }
    if corrects is not None:
        data["corrects_message_id"] = corrects
    return data


class ExchangeToolTests(unittest.TestCase):
    def test_initialize(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "exchange"
            initialize(destination, "TEST")
            self.assertTrue((destination / "START_HERE.md").exists())
            state = json.loads((destination / "01_GOVERNING_STATE/PROJECT_STATE_0001.json").read_text())
            self.assertEqual(state["project_id"], "TEST")
            self.assertEqual(state["status"], "evidence_ingestion")

    def test_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "a.txt").write_text("hello")
            manifest = generate_manifest(evidence, "TEST")
            self.assertEqual(manifest["summary"]["files_total"], 1)
            self.assertEqual(len(manifest["files"][0]["sha256"]), 64)
            self.assertTrue(manifest["inventory_complete"])

    def test_manifest_is_recursive(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"
            nested = evidence / "deep" / "v1"
            nested.mkdir(parents=True)
            (nested / "record.dat").write_text("important")
            manifest = generate_manifest(evidence, "TEST")
            self.assertIn("deep/v1", manifest["directories"])
            self.assertEqual(manifest["files"][0]["path"], "deep/v1/record.dat")

    def test_manifest_detects_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "a.txt").write_text("same")
            (evidence / "b.txt").write_text("same")
            manifest = generate_manifest(evidence, "TEST")
            self.assertEqual(len(manifest["summary"]["duplicate_groups"]), 1)
            duplicate_records = [item for item in manifest["files"] if item["duplicate_of"]]
            self.assertEqual(len(duplicate_records), 1)

    def test_manifest_does_not_preassert_participant_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "a.txt").write_text("hello")
            controls = generate_manifest(evidence, "TEST")["coverage_controls"]
            self.assertTrue(controls["local_inventory_complete"])
            self.assertFalse(controls["connector_limitations_documented"])
            self.assertEqual(controls["access_attested_by"], [])

    def test_archive_blocks_missing_claim_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "package.zip").write_bytes(b"not-a-real-zip")
            manifest = generate_manifest(evidence, "TEST")
            manifest["coverage_controls"]["relevant_filename_variants_searched"] = True
            manifest["coverage_controls"]["connector_limitations_documented"] = True
            report = build_coverage_report(manifest)
            self.assertFalse(report["missing_claim_gate_satisfied"])
            self.assertEqual(report["archives_not_inspected"], ["package.zip"])

    def test_coverage_gate_can_be_satisfied_per_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "a.txt").write_text("hello")
            manifest = generate_manifest(evidence, "TEST")
            manifest["coverage_controls"]["relevant_filename_variants_searched"] = True
            manifest["coverage_controls"]["connector_limitations_documented"] = True
            manifest["coverage_controls"]["access_attested_by"] = ["MODEL_A"]
            manifest["files"][0]["opened_by"] = ["MODEL_A"]
            manifest["files"][0]["parsed_by"] = ["MODEL_A"]
            report = build_coverage_report(manifest, reviewer="MODEL_A")
            self.assertTrue(report["missing_claim_gate_satisfied"])
            self.assertEqual(report["files_not_opened"], 0)

    def test_coverage_is_per_reviewer_not_shared(self):
        # The original shared-blind-spot regression: Model A opens everything,
        # Model B opens nothing. Model B must not inherit Model A's coverage.
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "a.txt").write_text("hello")
            manifest = generate_manifest(evidence, "TEST")
            manifest["coverage_controls"]["relevant_filename_variants_searched"] = True
            manifest["coverage_controls"]["connector_limitations_documented"] = True
            manifest["coverage_controls"]["access_attested_by"] = ["MODEL_A"]
            manifest["files"][0]["opened_by"] = ["MODEL_A"]
            manifest["files"][0]["parsed_by"] = ["MODEL_A"]
            report_b = build_coverage_report(manifest, reviewer="MODEL_B")
            self.assertEqual(report_b["files_opened"], 0)
            self.assertEqual(report_b["files_not_opened"], 1)
            self.assertFalse(report_b["access_attested"])
            self.assertFalse(report_b["missing_claim_gate_satisfied"])

    def test_unanswered_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text(json.dumps(message("EXCHANGE-0002", "EXCHANGE-0001")))
            pending, errors = find_unanswered(root)
            self.assertEqual(errors, [])
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0][1]["message_id"], "EXCHANGE-0002")

    def test_unreadable_message_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text("{ not valid json")
            errors = validate_exchange(root)
            self.assertTrue(any("could not be read as JSON" in e for e in errors))
            self.assertNotIn("no EXCHANGE-*.json messages found", errors)

    def test_unreadable_message_does_not_hide_among_valid_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text("{ not valid json")
            errors = validate_exchange(root)
            self.assertTrue(any("EXCHANGE-0002_B.json" in e for e in errors))

    def test_non_object_message_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text("[]")
            errors = validate_exchange(root)
            self.assertTrue(any("expected a JSON object" in e for e in errors))

    def test_message_without_message_id_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text("{}")
            errors = validate_exchange(root)
            self.assertTrue(any("has no message_id" in e for e in errors))

    def test_unanswered_reports_unreadable_reply(self):
        # If the reply file is corrupt, EXCHANGE-0001 looks unanswered; the
        # errors channel is what stops a participant from replying twice.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text("{ not valid json")
            pending, errors = find_unanswered(root)
            self.assertEqual([m["message_id"] for _, m in pending], ["EXCHANGE-0001"])
            self.assertTrue(any("EXCHANGE-0002_B.json" in e for e in errors))

    def test_next_id_skips_past_unreadable_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text("{ not valid json")
            self.assertEqual(suggest_next_id(root), "EXCHANGE-0003")

    def test_correction_flow_validates(self):
        # A challenges, B responds, A rebuts, then B corrects its own 0002.
        # The correction replies to the thread head (0003) and names 0002
        # via corrects_message_id, so the one-reply rule is preserved.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text(json.dumps(message("EXCHANGE-0002", "EXCHANGE-0001")))
            (root / "EXCHANGE-0003_A.json").write_text(json.dumps(
                message("EXCHANGE-0003", "EXCHANGE-0002", sender="MODEL_A", message_type="rebuttal")))
            (root / "EXCHANGE-0004_B.json").write_text(json.dumps(
                message("EXCHANGE-0004", "EXCHANGE-0003", sender="MODEL_B",
                        message_type="correction", corrects="EXCHANGE-0002")))
            self.assertEqual(validate_exchange(root), [])

    def test_correction_cannot_target_counterpart_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text(json.dumps(
                message("EXCHANGE-0002", "EXCHANGE-0001", sender="MODEL_B",
                        message_type="correction", corrects="EXCHANGE-0001")))
            errors = validate_exchange(root)
            self.assertTrue(any("corrects only its own messages" in e for e in errors))

    def test_correction_target_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text(json.dumps(
                message("EXCHANGE-0002", "EXCHANGE-0001", sender="MODEL_B",
                        message_type="correction", corrects="EXCHANGE-0009")))
            errors = validate_exchange(root)
            self.assertTrue(any("references missing message EXCHANGE-0009" in e for e in errors))

    def test_sources_must_resolve_to_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "files": [
                    {"path": "a.txt", "sha256": "a" * 64},
                ]
            }
            (root / "EVIDENCE_MANIFEST.json").write_text(json.dumps(manifest))
            claims = [{
                "claim_id": "C-1", "statement": "Test", "position": "supported",
                "confidence": 0.9, "materiality": "high", "reasoning_summary": "Test",
                "sources": [{"file": "ghost_file.pdf", "authority": "primary"}],
            }]
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(
                message("EXCHANGE-0001", None, claims=claims)))
            errors = validate_exchange(root)
            self.assertTrue(any("ghost_file.pdf" in e and "not in the evidence manifest" in e for e in errors))

    def test_non_string_source_hash_is_an_error_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "files": [
                    {"path": "a.txt", "sha256": "a" * 64},
                ]
            }
            (root / "EVIDENCE_MANIFEST.json").write_text(json.dumps(manifest))
            claims = [{
                "claim_id": "C-1", "statement": "Test", "position": "supported",
                "confidence": 0.9, "materiality": "high", "reasoning_summary": "Test",
                "sources": [{"file": "a.txt", "authority": "primary", "sha256": 12345}],
            }]
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(
                message("EXCHANGE-0001", None, claims=claims)))
            errors = validate_exchange(root)
            self.assertTrue(any("non-string sha256" in e for e in errors))

    def test_source_hash_must_match_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "files": [
                    {"path": "a.txt", "sha256": "a" * 64},
                ]
            }
            (root / "EVIDENCE_MANIFEST.json").write_text(json.dumps(manifest))
            good = [{
                "claim_id": "C-1", "statement": "Test", "position": "supported",
                "confidence": 0.9, "materiality": "high", "reasoning_summary": "Test",
                "sources": [{"file": "a.txt", "authority": "primary", "sha256": "a" * 64}],
            }]
            bad = [{
                "claim_id": "C-2", "statement": "Test", "position": "supported",
                "confidence": 0.9, "materiality": "high", "reasoning_summary": "Test",
                "sources": [{"file": "a.txt", "authority": "primary", "sha256": "b" * 64}],
            }]
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(
                message("EXCHANGE-0001", None, claims=good)))
            self.assertEqual(validate_exchange(root), [])
            (root / "EXCHANGE-0002_B.json").write_text(json.dumps(
                message("EXCHANGE-0002", "EXCHANGE-0001", claims=bad)))
            errors = validate_exchange(root)
            self.assertTrue(any("but the manifest records" in e for e in errors))


class ScaffoldMessageTests(unittest.TestCase):
    def test_scaffolds_first_challenge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "exchange"
            initialize(root, "SCAFFOLD-TEST")
            path = scaffold_message(root)
            self.assertEqual(path.parent.name, "10_MODEL_A_TO_MODEL_B")
            data = json.loads(path.read_text())
            self.assertEqual(data["message_id"], "EXCHANGE-0001")
            self.assertEqual(data["project_id"], "SCAFFOLD-TEST")
            self.assertEqual(data["sender"], "MODEL_A")
            self.assertIsNone(data["in_reply_to"])
            self.assertEqual(data["evidence_coverage"]["reviewer"], "MODEL_A")

    def test_scaffolds_reply_with_sender_flipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "exchange"
            initialize(root, "SCAFFOLD-TEST")
            first = scaffold_message(root)
            path = scaffold_message(root)
            self.assertEqual(path.parent.name, "20_MODEL_B_TO_MODEL_A")
            data = json.loads(path.read_text())
            self.assertEqual(data["message_id"], "EXCHANGE-0002")
            self.assertEqual(data["in_reply_to"], "EXCHANGE-0001")
            self.assertEqual(data["sender"], json.loads(first.read_text())["recipient"])
            self.assertEqual(data["evidence_coverage"]["reviewer"], data["sender"])

    def test_refuses_to_scaffold_on_a_corrupt_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text("{ not valid json")
            with self.assertRaises(SystemExit):
                scaffold_message(root)

    def test_refuses_when_no_message_is_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EXCHANGE-0001_A.json").write_text(json.dumps(message("EXCHANGE-0001", None)))
            (root / "EXCHANGE-0002_B.json").write_text(json.dumps(
                message("EXCHANGE-0002", "EXCHANGE-0001", message_type="escalation")))
            with self.assertRaises(SystemExit):
                scaffold_message(root)


if __name__ == "__main__":
    unittest.main()
