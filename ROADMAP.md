# Roadmap

SEEP is an early public protocol. The roadmap favors boring reliability over theatrical autonomy.

## Direction: the oracle model (v0.5, experimental)

The v0.5 line is being reframed around a single principle: **maximize non-model
oracles, minimize model-to-model adjudication.** Debate between two models given
identical inputs provably does not improve correctness, and treating their
consensus as success rewards correlated blind spots. The value that survives is
the part decided by an oracle rather than a model — a red-green test, a citation
that resolves to real bytes. The reasoning is in
[`docs/design/v0.5-oracle-model.md`](docs/design/v0.5-oracle-model.md).

A runnable first cut of the oracle core is in `scripts/` now
(`ledger.py`, `run_falsification.py`, `verify_gate.py`) with a worked example in
[`examples/oracle-core/`](examples/oracle-core/):

- an append-only claim ledger with terminals **promoted / killed / unresolved**
  (consensus is no longer a terminal state);
- a **promote gate** that refuses to advance a claim without a falsification
  record that fails at base and passes at fix;
- **rule 8 extended to concessions**: a change of position toward agreement must
  cite new evidence, or the ledger rejects it;
- **citation resolution** against git blobs / files by sha256 and excerpt.

Open, on purpose: **one agent or two.** v1 is one agent + the falsifiability
gate. The adversarial second agent (finder writes the failing test, the other
writes the fix without seeing it) is a *hypothesis with a test attached*, not a
committed premise — see below.

### The acceptance test

Run the oracle core against the five MoSeq2 forks (upstream = base tree, fork =
fix tree). **Does an oracle-gated review promote at least one real numerical
defect that a single unstructured pass missed?** If yes, SEEP is justified and
the caught bug is the artifact. If no, its value is thinner than hoped — worth
knowing cheaply. Either outcome is published, failures included.

### Deferred (was the old v0.5 headline)

- Collapsing the directional message folders into `10_EXCHANGE/`. Still
  reasonable, but a deck chair next to the oracle question; it is deferred, not
  scheduled, until the acceptance test above has run.

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

- Run the oracle-core acceptance test on the MoSeq2 forks (see Direction).
- If v1 earns it: add the adversarial second agent (finder writes the failing test, the other writes the fix without seeing it) and measure whether it kills findings the single-agent pass promoted.
- Expand the completed example library.
- Add automatic claim-reopening checks when new evidence lands.
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
