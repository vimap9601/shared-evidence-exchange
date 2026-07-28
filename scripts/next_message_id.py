from __future__ import annotations

import argparse
from pathlib import Path
from common import MESSAGE_ID_RE, discover_messages


def suggest_next_id(root: Path) -> str:
    numbers = []
    # Filenames count even when a file is unreadable, so a corrupt message's
    # number is never reissued to a new message.
    for path in root.rglob("EXCHANGE-*.json"):
        match = MESSAGE_ID_RE.fullmatch(path.stem.split("_")[0])
        if match:
            numbers.append(int(match.group(1)))
    for _, message in discover_messages(root):
        match = MESSAGE_ID_RE.fullmatch(str(message.get("message_id", "")))
        if match:
            numbers.append(int(match.group(1)))
    return f"EXCHANGE-{max(numbers, default=0) + 1:04d}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Suggest the next message ID.")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(suggest_next_id(args.root))
