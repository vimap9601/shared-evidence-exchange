# Oracle-core worked example (experimental, SEEP v0.5 preview)

This is a tiny end-to-end run of the oracle core described in
[`docs/design/v0.5-oracle-model.md`](../../docs/design/v0.5-oracle-model.md).
The findings are illustrative MoSeq2-flavored claims; the point is the
*lifecycle*, not the specific bugs.

`ledger.jsonl` is an append-only event log. Replay it:

```bash
python scripts/ledger.py fold examples/oracle-core/ledger.jsonl
python scripts/ledger.py verify examples/oracle-core/ledger.jsonl
```

It shows all three terminal states and why each was reached:

| Claim | Terminal | Why |
|---|---|---|
| F-001 | **promoted** | A red-green record proved it: the assertion failed on the buggy tree and passed on the fix. |
| F-002 | **killed** | The assertion passed at base too — the bug was never reproduced, so agreement about it would have been wrong. |
| F-003 | **unresolved** | A modeling judgment that cannot be reduced to a failing assertion; escalated to a human. |
| F-004 | **promoted** | An agent conceded, but only on *new evidence it found itself* (rule 8 for concessions), and the oracle then confirmed red-green. |

The load-bearing fact: **no claim was promoted because two models agreed.**
Every promotion went through the red-green oracle. F-002 is the case that
matters most — a plausible finding both models might have "agreed" on, killed
because the oracle could not reproduce it.

## The pieces

- `scripts/ledger.py` — the append-only ledger and its promote gate. A claim
  cannot reach `promoted` without a falsification record that fails at base and
  passes at fix.
- `scripts/run_falsification.py` — runs a repro command red-green against a
  base tree and a fix tree, and emits the `falsification_recorded` event.
- `scripts/verify_gate.py` — resolves cited evidence (git blob or file +
  sha256 + excerpt) against real bytes, so a citation is an oracle fact, not a
  model's claim.

## Trying the red-green runner yourself

```bash
# base tree fails the assertion, fix tree passes it -> promotable
python scripts/run_falsification.py F-001 \
  --repro "python -m pytest tests/test_area.py -q" \
  --base-dir /path/to/upstream-checkout \
  --fix-dir  /path/to/fork-checkout \
  --append my-ledger.jsonl
```
