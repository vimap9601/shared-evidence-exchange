# Finish-Line Rule

The exchange is complete only after the evidence-coverage report is current and one of these conditions is met.

## 1. Consensus

All material claims and the resulting action plan are agreed, and the missing-claim gate is satisfied for every participant.

Consensus is where the shared-blind-spot risk peaks: no remaining disagreement forces anyone back into the evidence. If the gate cannot be satisfied, consensus may still close only with an explicit **Coverage limitations** section in `REVIEW_COMPLETE.md` listing each unsatisfied gate condition, and with the project state recording `evidence_coverage_status: complete_with_limitations`.

## 2. Documented deadlock

Remaining disagreements are explicit, each model has cited its strongest primary evidence, the missing-claim gate is satisfied, and no identified evidence path remains unreviewed.

## 3. Human decision required

The evidence cannot decide a contractual, commercial, legal, technical, policy, or authority question without an authorized person making a decision.

## Round cap

If the project state sets `max_rounds` and the exchange reaches it without meeting a completion condition, the exchange must close as a documented deadlock or escalate to a human decision. Indefinite `partially_agree` ping-pong is not a state this protocol permits.

## Completion marker

Create:

```text
40_RECONCILED_OUTPUT/REVIEW_COMPLETE.md
```

It must contain agreed facts, corrected project state, rejected or superseded claims, unresolved matters, required human decisions, recommended next actions, and the governing final files.
