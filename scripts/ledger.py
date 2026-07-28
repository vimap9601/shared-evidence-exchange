from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# The oracle core (experimental, SEEP v0.5 preview).
#
# An append-only claim ledger whose promotion gate is an oracle, not an
# agreement. A claim advances to `promoted` only when a red-green
# falsification record proves it — never because two models concur. See
# docs/design/v0.5-oracle-model.md for the reasoning.

LEDGER_VERSION = "0.1"

# Evidence tiers, mirrored from the review vocabulary so a finding's tag
# survives from prompt to ledger unchanged.
EVIDENCE_TIERS = {"EXECUTED", "SOURCE", "SPECULATIVE"}

# `open` is the entry state. The three terminals replace SEEP-0.4's
# agree / disagree / consensus. Convergence is deliberately NOT a terminal
# state: correlated models converge on shared error, so agreement is a signal,
# never a success condition.
TERMINAL_STATES = {"promoted", "killed", "unresolved"}

EVENT_TYPES = {
    "claim_opened",
    "evidence_added",
    "falsification_recorded",
    "conceded",
    "promoted",
    "killed",
    "unresolved",
}


class LedgerError(Exception):
    """Raised when the ledger violates an append-only or gate invariant."""


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise LedgerError(f"line {line_number}: not valid JSON: {exc}") from exc
            if not isinstance(event, dict):
                raise LedgerError(f"line {line_number}: event must be a JSON object")
            events.append(event)
    return events


def _satisfies_red_green(record: dict[str, Any] | None) -> bool:
    # The promote oracle: the assertion must fail on the buggy commit (red)
    # and pass after the fix (green), and it must have actually been executed.
    if not isinstance(record, dict):
        return False
    return (
        record.get("fails_at_base") is True
        and record.get("passes_at_fix") is True
        and record.get("evidence_tag") == "EXECUTED"
    )


def fold(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Replay events into the current state of each claim. Raises on the first
    invariant violation, so a folded ledger is a verified ledger."""
    claims: dict[str, dict[str, Any]] = {}
    for index, event in enumerate(events):
        etype = event.get("event")
        claim_id = event.get("claim_id")
        where = f"event {index} ({etype})"
        if etype not in EVENT_TYPES:
            raise LedgerError(f"{where}: unknown event type")
        if not isinstance(claim_id, str) or not claim_id:
            raise LedgerError(f"{where}: claim_id is required")

        if etype == "claim_opened":
            if claim_id in claims:
                raise LedgerError(f"{where}: claim {claim_id} opened twice")
            statement = event.get("statement")
            if not isinstance(statement, str) or not statement:
                raise LedgerError(f"{where}: claim_opened requires a statement")
            tag = event.get("evidence_tag")
            if tag not in EVIDENCE_TIERS:
                raise LedgerError(
                    f"{where}: evidence_tag must be one of {sorted(EVIDENCE_TIERS)}"
                )
            claims[claim_id] = {
                "statement": statement,
                "evidence_tag": tag,
                "opened_by": event.get("author"),
                "opening_evidence_id": event.get("evidence_id"),
                "evidence_ids": set(),
                "falsification": None,
                "state": "open",
            }
            continue

        # Every other event targets an existing, non-terminal claim.
        claim = claims.get(claim_id)
        if claim is None:
            raise LedgerError(f"{where}: claim {claim_id} referenced before it was opened")
        if claim["state"] in TERMINAL_STATES:
            raise LedgerError(
                f"{where}: claim {claim_id} is already {claim['state']}; "
                "the ledger is append-only and terminal states are final"
            )

        if etype == "evidence_added":
            evidence_id = event.get("evidence_id")
            if not isinstance(evidence_id, str) or not evidence_id:
                raise LedgerError(f"{where}: evidence_added requires an evidence_id")
            claim["evidence_ids"].add(evidence_id)

        elif etype == "falsification_recorded":
            record = event.get("record")
            if not isinstance(record, dict):
                raise LedgerError(f"{where}: falsification_recorded requires a record object")
            claim["falsification"] = record
            evidence_id = event.get("evidence_id")
            if isinstance(evidence_id, str) and evidence_id:
                claim["evidence_ids"].add(evidence_id)

        elif etype == "conceded":
            # Rule 8, extended to concessions: a change of position toward
            # agreement is only valid if it cites NEW evidence the original
            # claim did not carry. A bare concession is capitulation, and the
            # ledger refuses it. (Necessary, not sufficient — a model can still
            # manufacture the evidence; see the design note.)
            new_evidence_id = event.get("new_evidence_id")
            if not isinstance(new_evidence_id, str) or not new_evidence_id:
                raise LedgerError(
                    f"{where}: a concession must cite new_evidence_id "
                    "(agreement without new evidence remains unresolved)"
                )
            if new_evidence_id == claim["opening_evidence_id"]:
                raise LedgerError(
                    f"{where}: concession cites the claim's own opening evidence; "
                    "it must cite evidence added after the claim opened"
                )
            if new_evidence_id not in claim["evidence_ids"]:
                raise LedgerError(
                    f"{where}: concession cites {new_evidence_id}, which is not "
                    "recorded evidence on this claim"
                )

        elif etype == "promoted":
            if not _satisfies_red_green(claim["falsification"]):
                raise LedgerError(
                    f"{where}: claim {claim_id} cannot be promoted without a "
                    "falsification record that fails at base and passes at fix "
                    "(EXECUTED). Only killed or unresolved are reachable."
                )
            claim["state"] = "promoted"

        elif etype in {"killed", "unresolved"}:
            if not isinstance(event.get("reason"), str) or not event["reason"]:
                raise LedgerError(f"{where}: {etype} requires a reason")
            claim["state"] = etype

    return claims


def verify_ledger(path: Path) -> list[str]:
    try:
        events = load_events(path)
        if not events:
            return ["ledger is empty"]
        fold(events)
    except LedgerError as exc:
        return [str(exc)]
    return []


def _print_fold(claims: dict[str, dict[str, Any]]) -> None:
    if not claims:
        print("(no claims)")
        return
    width = max(len(cid) for cid in claims)
    for claim_id, claim in claims.items():
        gate = "red-green" if _satisfies_red_green(claim["falsification"]) else "no-oracle"
        print(
            f"{claim_id:<{width}}  {claim['state']:<10}  "
            f"[{claim['evidence_tag']:<11}] {gate:<9}  {claim['statement']}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SEEP oracle-core claim ledger.")
    sub = parser.add_subparsers(dest="command", required=True)
    fold_parser = sub.add_parser("fold", help="Show the current state of every claim.")
    fold_parser.add_argument("ledger", type=Path)
    verify_parser = sub.add_parser("verify", help="Check append-only and gate invariants.")
    verify_parser.add_argument("ledger", type=Path)
    args = parser.parse_args()

    if args.command == "verify":
        errors = verify_ledger(args.ledger)
        if errors:
            print("Ledger invalid:")
            for error in errors:
                print(f"- {error}")
            raise SystemExit(1)
        print("Ledger valid.")
    else:
        _print_fold(fold(load_events(args.ledger)))
