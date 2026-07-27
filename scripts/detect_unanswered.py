from __future__ import annotations

import argparse
from pathlib import Path
from common import discover_messages


def find_unanswered(root: Path) -> list[tuple[Path, dict]]:
    messages = discover_messages(root)
    answered = {m.get("in_reply_to") for _, m in messages if m.get("in_reply_to")}
    return [
        (path, message) for path, message in messages
        if message.get("message_id") not in answered
        and message.get("message_type") not in {"reconciliation", "escalation"}
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find unanswered SEEP messages.")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    pending = find_unanswered(args.root)
    if not pending:
        print("No unanswered messages.")
    for path, message in pending:
        print(f"{message['message_id']} {message.get('sender')} -> {message.get('recipient')} {path}")
