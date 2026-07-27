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

## 2. Mandatory evidence-ingestion phase

Substantive review begins only after a recursive evidence manifest is created.

The manifest must identify every accessible folder and file, hashes, duplicates, archive status, review status, evidence authority, source class, and known connector limitations. Each exchange message must include an `evidence_coverage` report.

A model must not say evidence is **missing**, **not provided**, or **absent** until the missing-claim gate is satisfied:

1. recursive inventory is complete;
2. relevant filename and terminology variants were searched;
3. archives and nested containers were inspected;
4. connector limitations are documented;
5. no relevant folder remains outside recursive review.

Before that gate, use: **“Not located in the evidence reviewed to date.”**

A file that was not opened must never be described as reviewed. Parsed text and visual inspection are separate coverage states.

## 3. Default evidence hierarchy

1. Applicable law, regulation, or executed agreement
2. Formally issued or approved governing document
3. Written decision from an authorized decision-maker
4. Returned review, formal comment, or approved change record
5. Vendor or specialist documentation
6. Native model inputs and raw datasets
7. Internal correspondence or notes
8. Model-generated summaries
9. Human recollection

Projects should customize this hierarchy.

## 4. Claim and status discipline

Claims are reconciled individually. Agreement without primary evidence remains unresolved.

Do not collapse distinct status dimensions. For example, **submitted**, **approved**, **compliant**, and **released for execution** describe different facts and must be recorded separately.

Evidence basis should be labeled as one or more of:

- measured;
- manufacturer-calculated;
- independently modeled;
- document-reported;
- inferred;
- assumed.

New primary evidence reopens every affected claim. The new message must identify the reopened or superseded claim IDs rather than silently replacing the old conclusion.

## 5. Message naming

```text
EXCHANGE-0001_MODEL_A_CHALLENGE.json
EXCHANGE-0002_MODEL_B_RESPONSE.json
EXCHANGE-0003_MODEL_A_REBUTTAL.json
```

Context snapshots may use a suffix:

```text
EXCHANGE-0001A_MODEL_B_CONTEXT_SNAPSHOT.md
```

## 6. Required verdicts

Each disputed claim receives exactly one verdict:

- `agree`
- `disagree`
- `partially_agree`
- `unresolved`

## 7. Portable citations

Do not depend on model-platform citation tokens. Use exact filenames, SHA-256 hashes, pages, drawing sheets, clauses, email metadata, commit IDs, dataset rows, and short excerpts.

## 8. Context snapshots

A context snapshot must say:

> Non-governing prior model output. Context only. Every material conclusion must be independently verified against primary evidence.

## 9. Duplicate prevention

Before responding, check whether another message already contains `in_reply_to` equal to the target message's `message_id`.

## 10. Corrections

A correction identifies the prior message, affected claim, old position, revised position, reason for the change, and new evidence.

## 11. Human authority

Models may review, compare, recommend, and document. Humans retain authority for consequential decisions and external actions.

## 12. Completion

Completion is governed by `FINISH_LINE.md`. A final record must include both conclusions and remaining uncertainty.
