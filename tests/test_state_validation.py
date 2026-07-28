from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import (
    COVERAGE_STATUSES,
    PROTOCOL_VERSION,
    STATE_REQUIRED_FIELDS,
    STATE_STATUSES,
    validate_state,
)
from detect_unanswered import find_unanswered
from validate_state import validate_states


def state(**overrides) -> dict:
    data = {
        "protocol": PROTOCOL_VERSION,
        "project_id": "TEST",
        "state_version": 1,
        "last_message_id": None,
        "agreed_claims": [],
        "disputed_claims": [],
        "unresolved_questions": [],
        "required_human_decisions": [],
        "next_actor": "MODEL_A",
        "status": "peer_review_open",
        "reopened_claims": [],
        "evidence_manifest": None,
        "evidence_coverage_status": "complete",
    }
    data.update(overrides)
    return data


def message(message_id: str, in_reply_to: str | None, **overrides) -> dict:
    sender = "MODEL_A" if in_reply_to is None else "MODEL_B"
    data = {
        "project_id": "TEST",
        "message_id": message_id,
        "in_reply_to": in_reply_to,
        "sender": sender,
        "recipient": "MODEL_B" if sender == "MODEL_A" else "MODEL_A",
        "message_type": "audit_challenge" if in_reply_to is None else "response",
        "claims": [],
        "open_questions": [],
    }
    data.update(overrides)
    return data


def write_workspace(root: Path, states: list[dict], messages: list[dict]) -> None:
    for entry in states:
        name = f"PROJECT_STATE_{entry['state_version']:04d}.json"
        (root / name).write_text(json.dumps(entry))
    for entry in messages:
        (root / f"{entry['message_id']}_TEST.json").write_text(json.dumps(entry))


class StateValidationTests(unittest.TestCase):
    def test_valid_state(self):
        self.assertEqual(validate_state(state()), [])

    def test_template_state_is_valid(self):
        template = json.loads((ROOT / "templates/PROJECT_STATE_0001.json").read_text())
        self.assertEqual(validate_state(template), [])

    def test_missing_field(self):
        data = state()
        del data["status"]
        errors = validate_state(data)
        self.assertTrue(any("missing required fields" in e for e in errors))

    def test_unknown_status(self):
        errors = validate_state(state(status="paused"))
        self.assertTrue(any("status must be one of" in e for e in errors))

    def test_unknown_coverage_status(self):
        errors = validate_state(state(evidence_coverage_status="done"))
        self.assertTrue(any("evidence_coverage_status" in e for e in errors))

    def test_state_version_must_be_positive_integer(self):
        for bad in [0, -1, "1", True, None]:
            errors = validate_state(state(state_version=bad))
            self.assertTrue(any("state_version" in e for e in errors), bad)

    def test_claim_lists_must_hold_nonempty_strings(self):
        errors = validate_state(state(agreed_claims=["", 3]))
        self.assertTrue(any("agreed_claims" in e for e in errors))

    def test_max_rounds_must_be_positive_integer(self):
        for bad in [0, "6", True]:
            errors = validate_state(state(max_rounds=bad))
            self.assertTrue(any("max_rounds" in e for e in errors), bad)

    def test_human_decision_status_requires_a_decision(self):
        errors = validate_state(state(status="human_decision_required"))
        self.assertTrue(any("required_human_decisions" in e for e in errors))
        ok = state(
            status="human_decision_required",
            required_human_decisions=["Approve or reject the submission."],
        )
        self.assertEqual(validate_state(ok), [])

    def test_complete_requires_complete_coverage(self):
        errors = validate_state(state(status="complete", evidence_coverage_status="incomplete"))
        self.assertTrue(any("complete_with_limitations" in e for e in errors))


class StateCrossCheckTests(unittest.TestCase):
    def test_no_state_files_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = validate_states(Path(tmp))
            self.assertEqual(errors, ["no PROJECT_STATE_*.json state files found"])

    def test_version_must_match_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PROJECT_STATE_0002.json").write_text(json.dumps(state(state_version=1)))
            errors = validate_states(root)
            self.assertTrue(any("does not match the filename number" in e for e in errors))

    def test_badly_named_state_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PROJECT_STATE_0001_FINAL.json").write_text(json.dumps(state()))
            errors = validate_states(root)
            self.assertTrue(any("filename must match" in e for e in errors))

    def test_corrupt_state_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PROJECT_STATE_0001.json").write_text("{ not valid json")
            errors = validate_states(root)
            self.assertTrue(any("could not be read as JSON" in e for e in errors))

    def test_last_message_id_must_exist_on_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(last_message_id="EXCHANGE-0002")],
                [message("EXCHANGE-0001", None)],
            )
            errors = validate_states(root)
            self.assertTrue(any("matches no message on record" in e for e in errors))

    def test_agreed_claim_must_exist_on_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(agreed_claims=["CLAIM-404"])],
                [message("EXCHANGE-0001", None, claims=[{"claim_id": "CLAIM-001"}])],
            )
            errors = validate_states(root)
            self.assertTrue(any("CLAIM-404" in e and "no message on record" in e for e in errors))

    def test_unresolved_question_must_exist_on_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(unresolved_questions=["Q-404"])],
                [message("EXCHANGE-0001", None, open_questions=[{"question_id": "Q-001"}])],
            )
            errors = validate_states(root)
            self.assertTrue(any("Q-404" in e for e in errors))

    def test_referenced_ids_resolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(
                    last_message_id="EXCHANGE-0001",
                    agreed_claims=["CLAIM-001"],
                    unresolved_questions=["Q-001"],
                )],
                [message(
                    "EXCHANGE-0001", None,
                    claims=[{"claim_id": "CLAIM-001"}],
                    open_questions=[{"question_id": "Q-001"}],
                )],
            )
            self.assertEqual(validate_states(root), [])

    def test_missing_manifest_path_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(root, [state(evidence_manifest="GONE/MANIFEST.json")], [])
            errors = validate_states(root)
            self.assertTrue(any("does not exist under" in e for e in errors))

    def test_project_id_must_be_consistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state()],
                [message("EXCHANGE-0001", None, project_id="OTHER")],
            )
            errors = validate_states(root)
            self.assertTrue(any("project_id differs" in e for e in errors))

    def test_unreadable_message_fails_state_validation(self):
        # Cross-checks against a record with unreadable messages are
        # unreliable, so the corrupt file is an error here too.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(root, [state()], [])
            (root / "EXCHANGE-0001_BAD.json").write_text("{ not valid json")
            errors = validate_states(root)
            self.assertTrue(any("could not be read as JSON" in e for e in errors))

    def test_example_workspace_validates(self):
        self.assertEqual(validate_states(ROOT / "examples/technical-audit"), [])


class FinishLineTests(unittest.TestCase):
    def exchange(self, rounds: int) -> list[dict]:
        messages = [message("EXCHANGE-0001", None)]
        for index in range(2, rounds + 1):
            messages.append(message(f"EXCHANGE-{index:04d}", f"EXCHANGE-{index - 1:04d}"))
        return messages

    def test_reaching_max_rounds_with_open_status_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(max_rounds=2, last_message_id="EXCHANGE-0002")],
                self.exchange(2),
            )
            errors = validate_states(root)
            self.assertTrue(any("max_rounds" in e and "FINISH_LINE" in e for e in errors))

    def test_under_max_rounds_is_fine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(max_rounds=3, last_message_id="EXCHANGE-0002")],
                self.exchange(2),
            )
            self.assertEqual(validate_states(root), [])

    def test_max_rounds_closed_by_human_escalation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(
                    max_rounds=2,
                    last_message_id="EXCHANGE-0002",
                    status="human_decision_required",
                    required_human_decisions=["Decide the disputed approval."],
                )],
                self.exchange(2),
            )
            self.assertEqual(validate_states(root), [])

    def test_max_rounds_closed_by_documented_deadlock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [state(max_rounds=2, last_message_id="EXCHANGE-0002", status="complete")],
                self.exchange(2),
            )
            (root / "REVIEW_COMPLETE.md").write_text("# Documented deadlock\n")
            self.assertEqual(validate_states(root), [])

    def test_complete_without_completion_marker_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(root, [state(status="complete")], [])
            errors = validate_states(root)
            self.assertTrue(any("REVIEW_COMPLETE.md" in e for e in errors))

    def test_finish_line_reads_the_newest_state_only(self):
        # An early open state must not trigger finish-line errors once a
        # later state closes the exchange.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [
                    state(max_rounds=2, last_message_id="EXCHANGE-0001"),
                    state(
                        state_version=2,
                        max_rounds=2,
                        last_message_id="EXCHANGE-0002",
                        status="human_decision_required",
                        required_human_decisions=["Decide the disputed approval."],
                    ),
                ],
                self.exchange(2),
            )
            self.assertEqual(validate_states(root), [])

    def test_escalation_message_requires_no_reply(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workspace(
                root,
                [],
                [
                    message("EXCHANGE-0001", None),
                    message("EXCHANGE-0002", "EXCHANGE-0001", message_type="escalation"),
                ],
            )
            pending, errors = find_unanswered(root)
            self.assertEqual(errors, [])
            self.assertEqual(pending, [])


class StateSchemaAgreementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "protocol/STATE_SCHEMA.json").read_text())

    def test_required_fields_match(self):
        self.assertEqual(STATE_REQUIRED_FIELDS, set(self.schema["required"]))

    def test_statuses_match(self):
        self.assertEqual(STATE_STATUSES, set(self.schema["properties"]["status"]["enum"]))

    def test_coverage_statuses_match(self):
        self.assertEqual(
            COVERAGE_STATUSES,
            set(self.schema["properties"]["evidence_coverage_status"]["enum"]),
        )

    def test_protocol_constant_matches(self):
        self.assertEqual(PROTOCOL_VERSION, self.schema["properties"]["protocol"]["const"])


if __name__ == "__main__":
    unittest.main()
