from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import (
    CLOSED_STATUSES,
    STATE_CLAIM_LIST_FIELDS,
    STATE_FILE_RE,
    discover_messages_with_errors,
    load_json,
    validate_state,
)


def discover_states(root: Path) -> tuple[list[tuple[Path, dict[str, Any], int]], list[str]]:
    # Like exchange messages, an unreadable state file must surface as an
    # error: a corrupt state can hide a required human decision.
    states: list[tuple[Path, dict[str, Any], int]] = []
    errors: list[str] = []
    for path in sorted(root.rglob("PROJECT_STATE_*.json")):
        match = STATE_FILE_RE.fullmatch(path.name)
        if not match:
            errors.append(f"{path}: state filename must match PROJECT_STATE_0000.json")
            continue
        try:
            data = load_json(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: state file could not be read as JSON: {exc}")
            continue
        states.append((path, data, int(match.group(1))))
    return states, errors


def validate_states(root: Path) -> list[str]:
    states, errors = discover_states(root)
    if not states and not errors:
        return ["no PROJECT_STATE_*.json state files found"]

    messages, message_errors = discover_messages_with_errors(root)
    # Cross-checks against a record with unreadable messages would be
    # misleading, so discovery errors fail state validation too.
    errors.extend(message_errors)

    message_ids = {m.get("message_id") for _, m in messages}
    claim_ids: set[str] = set()
    question_ids: set[str] = set()
    project_ids = {
        m.get("project_id") for _, m in messages if isinstance(m.get("project_id"), str)
    }
    for _, message in messages:
        for claim in message.get("claims", []) if isinstance(message.get("claims"), list) else []:
            if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str):
                claim_ids.add(claim["claim_id"])
        questions = message.get("open_questions")
        for question in questions if isinstance(questions, list) else []:
            if isinstance(question, dict) and isinstance(question.get("question_id"), str):
                question_ids.add(question["question_id"])

    versions_seen: dict[int, Path] = {}
    for path, state, file_number in states:
        errors.extend(f"{path}: {e}" for e in validate_state(state))

        version = state.get("state_version")
        if isinstance(version, int) and not isinstance(version, bool):
            if version != file_number:
                errors.append(
                    f"{path}: state_version {version} does not match the filename number {file_number:04d}"
                )
            if version in versions_seen:
                errors.append(
                    f"{path}: state_version {version} already used by {versions_seen[version]}"
                )
            else:
                versions_seen[version] = path

        if isinstance(state.get("project_id"), str):
            project_ids.add(state["project_id"])

        last = state.get("last_message_id")
        if isinstance(last, str) and last not in message_ids:
            errors.append(f"{path}: last_message_id {last} matches no message on record")

        references = [
            (field, item, "claim", claim_ids)
            for field in STATE_CLAIM_LIST_FIELDS
            if isinstance(state.get(field), list)
            for item in state[field]
            if isinstance(item, str)
        ] + [
            ("unresolved_questions", item, "open question", question_ids)
            for item in state.get("unresolved_questions", [])
            if isinstance(state.get("unresolved_questions"), list) and isinstance(item, str)
        ]
        for field, item, label, known in references:
            if item not in known:
                errors.append(
                    f"{path}: {field} references {label} {item}, which appears in no message on record"
                )

        manifest = state.get("evidence_manifest")
        if isinstance(manifest, str) and manifest and not (root / manifest).exists():
            errors.append(f"{path}: evidence_manifest {manifest} does not exist under {root}")

    if len(project_ids) > 1:
        errors.append(
            "project_id differs across state files and messages: " + ", ".join(sorted(project_ids))
        )

    # Finish-line checks apply to the newest state, which governs the exchange.
    if states:
        latest_path, latest_state, _ = max(states, key=lambda item: item[2])
        status = latest_state.get("status")
        max_rounds = latest_state.get("max_rounds")
        if (
            isinstance(max_rounds, int)
            and not isinstance(max_rounds, bool)
            and max_rounds >= 1
            and len(messages) >= max_rounds
            and status not in CLOSED_STATUSES
        ):
            errors.append(
                f"{latest_path}: {len(messages)} message(s) have reached max_rounds {max_rounds}, "
                f"but status is {status}; the exchange must close as a documented deadlock "
                "or escalate to a human decision (FINISH_LINE.md)"
            )
        if status == "complete" and not any(root.rglob("REVIEW_COMPLETE.md")):
            errors.append(
                f"{latest_path}: status is complete but no REVIEW_COMPLETE.md completion marker "
                f"exists under {root}"
            )
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate SEEP project-state files against the message record."
    )
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    errors = validate_states(args.root)
    if errors:
        print("State validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    states, _ = discover_states(args.root)
    print(f"State valid: {len(states)} state file(s)")
