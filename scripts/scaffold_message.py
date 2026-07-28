from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import MESSAGE_ID_RE, load_json
from detect_unanswered import find_unanswered
from next_message_id import suggest_next_id
from validate_state import discover_states

CHALLENGE_TEMPLATE = "templates/MODEL_A_CHALLENGE.json"
RESPONSE_TEMPLATE = "templates/MODEL_B_RESPONSE.json"


def folder_for(root: Path, sender: str, is_reply: bool) -> Path:
    # Route into the standard directional folders when they exist; a custom
    # layout gets the file at the workspace root, which every tool scans
    # recursively anyway.
    if sender == "MODEL_A":
        name = "30_MODEL_A_REBUTTALS" if is_reply else "10_MODEL_A_TO_MODEL_B"
    elif sender == "MODEL_B":
        name = "20_MODEL_B_TO_MODEL_A"
    else:
        return root
    return root / name if (root / name).is_dir() else root


def latest_state(root: Path) -> dict[str, Any] | None:
    states, _ = discover_states(root)
    if not states:
        return None
    return max(states, key=lambda item: item[2])[1]


def scaffold_message(
    root: Path,
    sender: str | None = None,
    recipient: str | None = None,
) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    pending, errors = find_unanswered(root)
    if errors:
        raise SystemExit(
            "Refusing to scaffold on a record with unreadable message files "
            "(the pending reply may be hiding in one):\n"
            + "\n".join(f"- {error}" for error in errors)
        )

    state = latest_state(root)
    message_id = suggest_next_id(root)
    is_reply = message_id != "EXCHANGE-0001"

    if not is_reply:
        template = load_json(repo_root / CHALLENGE_TEMPLATE)
        template["sender"] = sender or "MODEL_A"
        template["recipient"] = recipient or "MODEL_B"
        template["in_reply_to"] = None
    else:
        if not pending:
            raise SystemExit(
                "No unanswered message to reply to. If the exchange is finished, "
                "write the completion marker instead of a new message."
            )
        # Reply to the newest pending message; older pending messages belong
        # to the counterpart and are not this sender's to answer.
        target_path, target = max(
            pending,
            key=lambda item: MESSAGE_ID_RE.fullmatch(item[1]["message_id"]).group(1),
        )
        template = load_json(repo_root / RESPONSE_TEMPLATE)
        template["sender"] = target.get("recipient")
        template["recipient"] = target.get("sender")
        template["in_reply_to"] = target["message_id"]
        print(f"Replying to {target['message_id']} ({target_path})")

    template["message_id"] = message_id
    template["created_at"] = datetime.now(timezone.utc).isoformat()
    if state is not None:
        if isinstance(state.get("project_id"), str):
            template["project_id"] = state["project_id"]
        if isinstance(state.get("evidence_manifest"), str):
            template["evidence_coverage"]["manifest_file"] = state["evidence_manifest"]
    template["evidence_coverage"]["reviewer"] = template["sender"]

    suffix = "CHALLENGE" if not is_reply else "RESPONSE"
    destination = folder_for(root, template["sender"], is_reply)
    path = destination / f"{message_id}_{template['sender']}_{suffix}.json"
    if path.exists():
        raise SystemExit(f"{path} already exists; refusing to overwrite (append-only record)")
    path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Scaffold the next exchange message: the first challenge in a fresh "
            "workspace, or a reply to the newest unanswered message. Placeholders "
            "in the scaffold must be filled in before the message is sent."
        )
    )
    parser.add_argument("root", type=Path)
    parser.add_argument("--sender", help="Sender for the first message (default MODEL_A).")
    parser.add_argument("--recipient", help="Recipient for the first message (default MODEL_B).")
    args = parser.parse_args()
    path = scaffold_message(args.root, args.sender, args.recipient)
    print(f"Scaffolded {path}")
    print("Fill in the placeholders, coverage counts, and claims before sending.")
