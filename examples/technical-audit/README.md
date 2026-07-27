# Completed Technical Audit Example

This sanitized example demonstrates the full SEEP lifecycle using a deliberately simple numerical conflict.

## Evidence ingestion

The example includes a recursive manifest and a complete evidence-coverage gate before the first claim is made.

## Evidence

- The governing requirement states a 70 C maximum.
- The vendor submission states an 82 C maximum.

## Exchange

1. `EXCHANGE-0001`: Model A identifies the conflict and asks whether a deviation was approved.
2. `EXCHANGE-0002`: Model B independently confirms the conflict and finds no approval record.
3. `EXCHANGE-0003`: Model A reconciles the agreed facts and closes the model review under the human-decision-required finish line.
4. `REVIEW_COMPLETE.md`: The final marker states what is known, what remains undecided, and who must act.

## Validate it

From the repository root:

```bash
python scripts/check_evidence_coverage.py examples/technical-audit/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json --require-missing-claim-gate
python scripts/validate_exchange.py examples/technical-audit
python scripts/detect_unanswered.py examples/technical-audit
```

The validator should pass, and the unanswered-message tool should report no pending model response because the final message is a reconciliation.
