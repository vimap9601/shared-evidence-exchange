# Roadmap

SEEP is an early public protocol. The roadmap favors boring reliability over theatrical autonomy.

## Implemented in v0.3.0

- Recursive directory and file manifests.
- Duplicate and archive detection.
- Evidence coverage reports and missing-claim gate checks.
- Separate opened, parsed, visually inspected, and unsupported states.
- Claim fields for evidence basis, status dimensions, supersession, and reopening.

## Near term

- Expand the completed example library.
- Add stronger cross-message claim validation and automatic reopening checks.
- Add a command that scaffolds a complete first exchange packet.
- Improve Windows and no-code setup documentation.
- Add tests for corrections, deadlocks, and human-escalation flows.

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
