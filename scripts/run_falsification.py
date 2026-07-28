from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Red-green falsification oracle (experimental, SEEP v0.5 preview).
#
# This is the mechanism that escapes the debate martingale. A finding is not
# promoted because a second model agrees; it is promoted because the same
# assertion FAILS on the buggy tree and PASSES on the fixed tree. The test's
# exit code is not a belief, so this step is not model-to-model. See
# docs/design/v0.5-oracle-model.md.


def _run(repro: str, cwd: Path, timeout: float) -> tuple[int, str]:
    # `repro` is the author's own test command run against their own trees, so
    # a shell is the expected interface. Output is captured, not streamed.
    completed = subprocess.run(
        repro,
        shell=True,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def evaluate(base_returncode: int, fix_returncode: int) -> dict[str, bool]:
    # Red: the assertion detects the bug (nonzero) on the base tree.
    # Green: the assertion passes (zero) on the fixed tree.
    return {
        "fails_at_base": base_returncode != 0,
        "passes_at_fix": fix_returncode == 0,
    }


def run_falsification(
    claim_id: str,
    repro: str,
    base_dir: Path,
    fix_dir: Path,
    author: str = "oracle",
    timeout: float = 300.0,
) -> dict[str, Any]:
    base_rc, base_out = _run(repro, base_dir, timeout)
    fix_rc, fix_out = _run(repro, fix_dir, timeout)
    verdict = evaluate(base_rc, fix_rc)
    record = {
        "repro": repro,
        "base_dir": str(base_dir),
        "fix_dir": str(fix_dir),
        "base_exit": base_rc,
        "fix_exit": fix_rc,
        "base_output_sha256": hashlib.sha256(base_out.encode("utf-8")).hexdigest(),
        "fix_output_sha256": hashlib.sha256(fix_out.encode("utf-8")).hexdigest(),
        "evidence_tag": "EXECUTED",
        **verdict,
    }
    return {
        "event": "falsification_recorded",
        "claim_id": claim_id,
        "author": author,
        "at": datetime.now(timezone.utc).isoformat(),
        "evidence_id": f"{claim_id}-falsification",
        "record": record,
    }


def recommend(record: dict[str, Any]) -> str:
    if record["fails_at_base"] and record["passes_at_fix"]:
        return "promoted"
    if not record["fails_at_base"]:
        # The assertion did not detect a bug on the base tree: either the bug
        # is not real or the test does not exercise it. Either way, not proven.
        return "killed"
    return "unresolved"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a repro command red-green against a base tree and a fix tree."
    )
    parser.add_argument("claim_id")
    parser.add_argument("--repro", required=True, help="Shell command that asserts the finding.")
    parser.add_argument("--base-dir", type=Path, required=True, help="Buggy tree (expect failure).")
    parser.add_argument("--fix-dir", type=Path, required=True, help="Fixed tree (expect pass).")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--append", type=Path, help="Ledger file to append the event to.")
    args = parser.parse_args()

    event = run_falsification(
        args.claim_id, args.repro, args.base_dir, args.fix_dir, timeout=args.timeout
    )
    record = event["record"]
    print(json.dumps(event, indent=2))
    print(
        f"\nbase exit {record['base_exit']} (red={record['fails_at_base']}), "
        f"fix exit {record['fix_exit']} (green={record['passes_at_fix']})"
    )
    print(f"recommended next event: {recommend(record)}")
    if args.append is not None:
        with args.append.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")
        print(f"appended falsification_recorded to {args.append}")
