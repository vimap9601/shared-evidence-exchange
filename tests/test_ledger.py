from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ledger import LedgerError, fold, verify_ledger
from run_falsification import evaluate, recommend, run_falsification
from verify_gate import resolve_evidence, verify_citations


def opened(claim_id: str, tag: str = "SOURCE", evidence_id: str | None = None) -> dict:
    event = {
        "event": "claim_opened",
        "claim_id": claim_id,
        "statement": f"{claim_id} says something falsifiable",
        "evidence_tag": tag,
        "author": "agent-a",
    }
    if evidence_id is not None:
        event["evidence_id"] = evidence_id
    return event


def red_green(claim_id: str, fails_at_base=True, passes_at_fix=True, tag="EXECUTED") -> dict:
    return {
        "event": "falsification_recorded",
        "claim_id": claim_id,
        "record": {
            "fails_at_base": fails_at_base,
            "passes_at_fix": passes_at_fix,
            "evidence_tag": tag,
        },
    }


def write_ledger(events: list[dict]) -> Path:
    tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for event in events:
        tmp.write(json.dumps(event) + "\n")
    tmp.close()
    return Path(tmp.name)


class PromoteGateTests(unittest.TestCase):
    def test_promotion_requires_red_green(self):
        events = [opened("F-1"), {"event": "promoted", "claim_id": "F-1"}]
        with self.assertRaises(LedgerError) as ctx:
            fold(events)
        self.assertIn("cannot be promoted", str(ctx.exception))

    def test_red_green_promotion_succeeds(self):
        events = [opened("F-1", tag="EXECUTED"), red_green("F-1"), {"event": "promoted", "claim_id": "F-1"}]
        claims = fold(events)
        self.assertEqual(claims["F-1"]["state"], "promoted")

    def test_green_without_red_cannot_promote(self):
        # Test passes at the fix but never failed at base: the bug was never
        # demonstrated, so the finding is not proven.
        events = [
            opened("F-1", tag="EXECUTED"),
            red_green("F-1", fails_at_base=False),
            {"event": "promoted", "claim_id": "F-1"},
        ]
        with self.assertRaises(LedgerError):
            fold(events)

    def test_unexecuted_record_cannot_promote(self):
        events = [
            opened("F-1", tag="EXECUTED"),
            red_green("F-1", tag="SOURCE"),
            {"event": "promoted", "claim_id": "F-1"},
        ]
        with self.assertRaises(LedgerError):
            fold(events)

    def test_unresolved_and_killed_need_reason(self):
        for terminal in ["killed", "unresolved"]:
            events = [opened("F-1"), {"event": terminal, "claim_id": "F-1"}]
            with self.assertRaises(LedgerError):
                fold(events)
        ok = [opened("F-1"), {"event": "unresolved", "claim_id": "F-1", "reason": "cannot reduce to a test"}]
        self.assertEqual(fold(ok)["F-1"]["state"], "unresolved")


class AppendOnlyTests(unittest.TestCase):
    def test_no_events_after_terminal(self):
        events = [
            opened("F-1"),
            {"event": "killed", "claim_id": "F-1", "reason": "refuted"},
            {"event": "evidence_added", "claim_id": "F-1", "evidence_id": "E-9"},
        ]
        with self.assertRaises(LedgerError) as ctx:
            fold(events)
        self.assertIn("append-only", str(ctx.exception))

    def test_claim_cannot_open_twice(self):
        with self.assertRaises(LedgerError):
            fold([opened("F-1"), opened("F-1")])

    def test_event_before_open_is_rejected(self):
        with self.assertRaises(LedgerError):
            fold([{"event": "evidence_added", "claim_id": "F-1", "evidence_id": "E-1"}])


class ConcessionRuleTests(unittest.TestCase):
    def test_bare_concession_rejected(self):
        events = [opened("F-1"), {"event": "conceded", "claim_id": "F-1", "author": "agent-b"}]
        with self.assertRaises(LedgerError) as ctx:
            fold(events)
        self.assertIn("new_evidence_id", str(ctx.exception))

    def test_concession_citing_new_evidence_accepted(self):
        events = [
            opened("F-1"),
            {"event": "evidence_added", "claim_id": "F-1", "evidence_id": "E-new"},
            {"event": "conceded", "claim_id": "F-1", "author": "agent-b", "new_evidence_id": "E-new"},
        ]
        self.assertEqual(fold(events)["F-1"]["state"], "open")

    def test_concession_cannot_reuse_opening_evidence(self):
        events = [
            opened("F-1", evidence_id="E-open"),
            {"event": "conceded", "claim_id": "F-1", "author": "agent-b", "new_evidence_id": "E-open"},
        ]
        with self.assertRaises(LedgerError) as ctx:
            fold(events)
        self.assertIn("opening evidence", str(ctx.exception))

    def test_concession_to_unrecorded_evidence_rejected(self):
        events = [
            opened("F-1"),
            {"event": "conceded", "claim_id": "F-1", "author": "agent-b", "new_evidence_id": "E-ghost"},
        ]
        with self.assertRaises(LedgerError):
            fold(events)


class LedgerFileTests(unittest.TestCase):
    def test_verify_clean_ledger(self):
        path = write_ledger([
            opened("F-1", tag="EXECUTED"),
            red_green("F-1"),
            {"event": "promoted", "claim_id": "F-1"},
        ])
        self.assertEqual(verify_ledger(path), [])

    def test_verify_reports_gate_violation(self):
        path = write_ledger([opened("F-1"), {"event": "promoted", "claim_id": "F-1"}])
        errors = verify_ledger(path)
        self.assertTrue(errors and "cannot be promoted" in errors[0])

    def test_empty_ledger_is_flagged(self):
        path = write_ledger([])
        self.assertEqual(verify_ledger(path), ["ledger is empty"])


class RedGreenRunnerTests(unittest.TestCase):
    def test_evaluate_maps_exit_codes(self):
        self.assertEqual(evaluate(1, 0), {"fails_at_base": True, "passes_at_fix": True})
        self.assertEqual(evaluate(0, 0), {"fails_at_base": False, "passes_at_fix": True})

    def test_recommend_from_record(self):
        self.assertEqual(recommend({"fails_at_base": True, "passes_at_fix": True}), "promoted")
        self.assertEqual(recommend({"fails_at_base": False, "passes_at_fix": True}), "killed")
        self.assertEqual(recommend({"fails_at_base": True, "passes_at_fix": False}), "unresolved")

    def test_runner_produces_promotable_record(self):
        # A synthetic bug: the tree's marker file decides whether the assertion
        # passes. base fails, fix passes -> red-green -> promotable end to end.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "base"
            fix = Path(tmp) / "fix"
            base.mkdir()
            fix.mkdir()
            (base / "value.txt").write_text("wrong")
            (fix / "value.txt").write_text("right")
            repro = "test \"$(cat value.txt)\" = right"
            event = run_falsification("F-1", repro, base, fix)
            record = event["record"]
            self.assertTrue(record["fails_at_base"])
            self.assertTrue(record["passes_at_fix"])
            promoted = fold([
                opened("F-1", tag="EXECUTED"),
                event,
                {"event": "promoted", "claim_id": "F-1"},
            ])
            self.assertEqual(promoted["F-1"]["state"], "promoted")


class CitationOracleTests(unittest.TestCase):
    def test_match_on_correct_hash_and_excerpt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("hello world")
            import hashlib
            digest = hashlib.sha256(b"hello world").hexdigest()
            result = resolve_evidence(
                {"evidence_id": "E-1", "file": "a.txt", "sha256": digest, "excerpt": "hello"},
                root,
            )
            self.assertEqual(result["verdict"], "match")

    def test_hash_mismatch_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("hello world")
            result = resolve_evidence(
                {"evidence_id": "E-1", "file": "a.txt", "sha256": "0" * 64},
                root,
            )
            self.assertEqual(result["verdict"], "hash_mismatch")

    def test_absent_excerpt_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("hello world")
            result = resolve_evidence(
                {"evidence_id": "E-1", "file": "a.txt", "excerpt": "goodbye"},
                root,
            )
            self.assertEqual(result["verdict"], "excerpt_absent")

    def test_missing_file_is_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = resolve_evidence({"evidence_id": "E-1", "file": "ghost.txt"}, Path(tmp))
            self.assertEqual(result["verdict"], "unresolved")

    def test_verify_citations_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("x")
            results = verify_citations(
                [{"evidence_id": "E-1", "file": "a.txt"}, {"evidence_id": "E-2", "file": "missing"}],
                root,
            )
            self.assertEqual([r["verdict"] for r in results], ["match", "unresolved"])


if __name__ == "__main__":
    unittest.main()
