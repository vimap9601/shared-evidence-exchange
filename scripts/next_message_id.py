from __future__ import annotations

import argparse
from pathlib import Path
from common import MESSAGE_ID_RE, discover_messages

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Suggest the next message ID.")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    numbers = []
    for _, message in discover_messages(args.root):
        match = MESSAGE_ID_RE.fullmatch(message.get("message_id", ""))
        if match:
            numbers.append(int(match.group(1)))
    print(f"EXCHANGE-{max(numbers, default=0) + 1:04d}")
