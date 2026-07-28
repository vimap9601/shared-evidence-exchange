# Roadmap

SEEP is an early public protocol. The roadmap favors boring reliability over theatrical autonomy.

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
- Add automatic claim-reopening checks and a `validate_state.py` cross-check of state files against the message record.
- Add a command that scaffolds a complete first exchange packet.
- Improve Windows and no-code setup documentation.
- Add tests for deadlocks and human-escalation flows.
- Decide whether to collapse the directional message folders into a single `10_EXCHANGE/` folder before 1.0.

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
