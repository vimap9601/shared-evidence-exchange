from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from common import discover_messages, validate_message


def validate_exchange(root: Path) -> list[str]:
    errors: list[str] = []
    messages = discover_messages(root)
    if not messages:
        return ["no EXCHANGE-*.json messages found"]
    ids = [m["message_id"] for _, m in messages]
    for message_id, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate message_id {message_id} appears {count} times")
    id_set = set(ids)
    replies: Counter[str] = Counter()
    for path, message in messages:
        errors.extend(f"{path}: {e}" for e in validate_message(message))
        target = message.get("in_reply_to")
        if target:
            replies[target] += 1
            if target not in id_set:
                errors.append(f"{path}: in_reply_to references missing message {target}")
    for target, count in replies.items():
        if count > 1:
            errors.append(f"message {target} has {count} replies; expected at most one")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a SEEP exchange.")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    errors = validate_exchange(args.root)
    if errors:
        print("Exchange validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"Exchange valid: {len(discover_messages(args.root))} message(s)")
