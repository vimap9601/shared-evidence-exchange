from __future__ import annotations

import argparse
from pathlib import Path
from common import discover_messages_with_errors


def find_unanswered(root: Path) -> tuple[list[tuple[Path, dict]], list[str]]:
    # An unreadable file may hold the reply to a pending message, so errors
    # travel with the result: acting on the list alone risks a duplicate reply.
    messages, errors = discover_messages_with_errors(root)
    answered = {m.get("in_reply_to") for _, m in messages if m.get("in_reply_to")}
    pending = [
        (path, message) for path, message in messages
        if message.get("message_id") not in answered
        and message.get("message_type") not in {"reconciliation", "escalation"}
    ]
    return pending, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find unanswered SEEP messages.")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    pending, errors = find_unanswered(args.root)
    for error in errors:
        print(f"WARNING  {error}")
    if not pending:
        print("No unanswered messages.")
    for path, message in pending:
        print(f"{message['message_id']} {message.get('sender')} -> {message.get('recipient')} {path}")
