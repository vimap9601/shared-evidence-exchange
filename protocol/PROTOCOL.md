# Shared Evidence Exchange Protocol

Protocol version: `SEEP-1.0`

## 1. Governing principles

1. Primary evidence outranks model-generated summaries.
2. Each material proposition receives a stable `claim_id`.
3. Exchange messages are append-only.
4. A prior message may be corrected only by a new numbered message.
5. Each response must address the exact proposition presented.
6. Silence, repeated appearance, or lack of comment does not automatically establish approval.
7. Facts, interpretations, assumptions, and recommendations must remain distinguishable.
8. Inferences must identify the evidence from which they were inferred.
9. Models are expected to revise prior conclusions when stronger evidence appears.
10. The purpose is a defensible record, not agreement for its own sake.

## 2. Default evidence hierarchy

1. Applicable law, regulation, or executed agreement
2. Formally issued or approved governing document
3. Written decision from an authorized decision-maker
4. Returned review, formal comment, or approved change record
5. Vendor or specialist documentation
6. Internal correspondence or notes
7. Model-generated summaries
8. Human recollection

Projects should customize this hierarchy.

## 3. Message naming

```text
EXCHANGE-0001_MODEL_A_CHALLENGE.json
EXCHANGE-0002_MODEL_B_RESPONSE.json
EXCHANGE-0003_MODEL_A_REBUTTAL.json
```

Context snapshots may use a suffix:

```text
EXCHANGE-0001A_MODEL_B_CONTEXT_SNAPSHOT.md
```

## 4. Required verdicts

Each disputed claim receives exactly one verdict:

- `agree`
- `disagree`
- `partially_agree`
- `unresolved`

## 5. Portable citations

Do not depend on model-platform citation tokens. Use exact filenames, SHA-256 hashes, pages, drawing sheets, clauses, email metadata, commit IDs, dataset rows, and short excerpts.

## 6. Context snapshots

A context snapshot must say:

> Non-governing prior model output. Context only. Every material conclusion must be independently verified against primary evidence.

## 7. Duplicate prevention

Before responding, check whether another message already contains `in_reply_to` equal to the target message's `message_id`.

## 8. Corrections

A correction identifies the prior message, affected claim, old position, revised position, reason for the change, and new evidence.

## 9. Human authority

Models may review, compare, recommend, and document. Humans retain authority for consequential decisions and external actions.

## 10. Completion

Completion is governed by `FINISH_LINE.md`.
