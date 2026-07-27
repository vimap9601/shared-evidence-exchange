from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_evidence_coverage import build_coverage_report
from detect_unanswered import find_unanswered
from generate_manifest import generate_manifest
from initialize_project import initialize


def coverage() -> dict:
    return {
        "manifest_file": "EVIDENCE_MANIFEST.json",
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


def message(message_id: str, in_reply_to: str | None) -> dict:
    return {
        "protocol": "SEEP-1.0", "project_id": "TEST",
        "message_id": message_id, "in_reply_to": in_reply_to,
        "sender": "MODEL_A" if in_reply_to is None else "MODEL_B",
        "recipient": "MODEL_B" if in_reply_to is None else "MODEL_A",
        "created_at": "2026-07-27T14:00:00Z",
        "message_type": "audit_challenge" if in_reply_to is None else "response",
        "summary_markdown": "Test", "evidence_coverage": coverage(), "claims": [],
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

    def test_archive_blocks_missing_claim_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "package.zip").write_bytes(b"not-a-real-zip")
            manifest = generate_manifest(evidence, "TEST")
            manifest["coverage_controls"]["relevant_filename_variants_searched"] = True
            report = build_coverage_report(manifest)
            self.assertFalse(report["missing_claim_gate_satisfied"])
            self.assertEqual(report["archives_not_inspected"], ["package.zip"])

    def test_coverage_gate_can_be_satisfied(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"; evidence.mkdir()
            (evidence / "a.txt").write_text("hello")
            manifest = generate_manifest(evidence, "TEST")
            manifest["coverage_controls"]["relevant_filename_variants_searched"] = True
            manifest["files"][0]["opened"] = True
            manifest["files"][0]["parsed"] = True
            report = build_coverage_report(manifest)
            self.assertTrue(report["missing_claim_gate_satisfied"])
            self.assertEqual(report["files_not_opened"], 0)

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
