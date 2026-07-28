# Roadmap

SEEP is an early public protocol. The roadmap favors boring reliability over theatrical autonomy.

## Decisions

- **The directional message folders (`10_MODEL_A_TO_MODEL_B/`, `20_MODEL_B_TO_MODEL_A/`, `30_MODEL_A_REBUTTALS/`) will collapse into a single `10_EXCHANGE/` folder in v0.5.0** (decided 2026-07-28, review finding 12). Message headers already carry sender, recipient, and reply target, so the directional split adds filing overhead without adding information. The initializer, scaffolder, examples, and docs will migrate together; the other numbered folders keep their roles.

## Implemented since v0.4.1

- `validate_state.py` cross-checks of state files against the message record, including finish-line enforcement for `max_rounds`, escalation, and completion markers.
- A command that scaffolds the next exchange message (`scaffold_message.py`).
- Tests for deadlock and human-escalation flows.

## Implemented in v0.4.0

- Per-participant coverage, access attestation, and a per-participant missing-claim gate.
- Correction messages with explicit targets that coexist with the one-reply rule.
- Claim-source validation against the evidence manifest, including hash checks.
- Source requirements for agreement verdicts.

## Implemented in v0.3.0

- Recursive directory and file manifests.
- Duplicate and archive detection.
- Evidence coverage reports and missing-claim gate checks.
- Separate opened, parsed, visually inspected, and unsupported states.
- Claim fields for evidence basis, status dimensions, supersession, and reopening.

## Near term

- Expand the completed example library.
- Add automatic claim-reopening checks when new evidence lands.
- Collapse the directional message folders into `10_EXCHANGE/` (see Decisions).
- Improve Windows and no-code setup documentation.

## Reference implementation

- File-system storage adapter.
- Google Drive and OneDrive adapter examples.
- Provider-neutral broker interfaces.
- Idempotent polling and duplicate-response prevention.
- Round, token, and cost limits.
- Human approval gates.
- Structured run logs and resumable state.

## Possible later work

- Lightweight local dashboard.
- Schema migration tools.
- Evidence packet generation.
- Visual claim and source graph.
- Signed message manifests.
- Release packages for nontechnical users.

## Explicitly not a goal

SEEP is not intended to remove human authority from consequential decisions. Automation should make the record clearer and the handoffs easier, not quietly grant models permission to act.

Contributions and use-case reports are welcome through GitHub Issues.
