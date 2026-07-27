from __future__ import annotations

import argparse
from pathlib import Path
from common import sha256_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print SHA-256 hashes.")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        if not path.is_file():
            print(f"ERROR  {path} is not a file")
            failed = True
        else:
            print(f"{sha256_file(path)}  {path}")
    raise SystemExit(1 if failed else 0)
