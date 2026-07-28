# Shared Evidence Exchange Protocol

![A cartoon robot feeds a claim card into an "Evidence Test Bench" machine whose screen reads FAIL then PASS; the machine sorts claims into three trays labelled PROMOTED, KILLED, and UNRESOLVED, and a person stands beside the UNRESOLVED tray holding a stamp](docs/assets/banner.png)

[![CI](https://github.com/Ctrl-Alt-Karma/shared-evidence-exchange/actions/workflows/ci.yml/badge.svg)](https://github.com/Ctrl-Alt-Karma/shared-evidence-exchange/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)

**An append-only, provider-independent protocol for evidence-grounded peer review between multiple AI models.**

SEEP turns an ordinary shared folder, such as Google Drive, OneDrive, Dropbox, SharePoint, or a Git repository, into a durable exchange layer for AI collaboration.

Instead of copying answers between chats, each model reads the same evidence, writes a numbered response, and leaves the previous record untouched. The result is inspectable, challengeable, restartable, and much less vulnerable to context drift.

> **Project status:** public alpha. The protocol and starter tools work today, but interfaces and schemas may evolve before version 1.0.

## Where this is heading

The shipped protocol (0.4) is consensus-oriented: two models read the same
evidence and exchange numbered messages until they agree, deadlock, or escalate
to a human. That framing has a known weak spot — two models with overlapping
training data tend to agree on the *same* wrong things, so consensus is exactly
where shared blind spots hide.

The v0.5 line (experimental, in
[`docs/design/v0.5-oracle-model.md`](docs/design/v0.5-oracle-model.md)) moves the
decisive step away from agreement and onto **oracles that are not models** — a
test that executes, a citation that resolves to real bytes. A finding is not
accepted because a second model concurs; it is **promoted** only when a
falsifying test fails on the buggy code and passes on the fix. Agreement becomes
a hint about who writes that test, never the verdict.

```mermaid
flowchart LR
    O[open claim] --> G{falsifying test?}
    G -->|fails at base, passes at fix| P[promoted]
    G -->|disproven / not reproduced| K[killed]
    G -->|cannot reduce to a test| U[unresolved → human]
```

A runnable first cut lives in `scripts/ledger.py`, `scripts/run_falsification.py`,
and `scripts/verify_gate.py`, with a worked example in
[`examples/oracle-core/`](examples/oracle-core/). It is a preview, not a promise:
whether it earns its place is being decided by a real-world test, not by
specification. See the [roadmap](ROADMAP.md).

## The 30-second version

1. Put the governing documents and evidence in a shared folder.
2. Each model inventories the evidence and reports what it actually opened, parsed, and visually inspected — its own coverage, not the other model's.
3. Every material claim is written down with a stable ID and a portable citation: the exact file, hash, page, or source lines it rests on.
4. Claims accumulate in an append-only record; earlier entries are never overwritten.
5. A claim only counts as established when it is backed by primary evidence that resolves — a cited file that exists, a hash that matches. A definitive "this is missing" is not allowed until coverage is complete.
6. What the evidence cannot settle is escalated to a human, explicitly, rather than smoothed over.

The human no longer has to summarize or relay the argument by hand; the record carries it. And because coverage is per participant, overlooking a folder leaves a visible trail instead of becoming a silent shared assumption.

Nothing file-based can *prevent* shared blind spots — every control is ultimately self-reported by the same class of system being audited. SEEP's honest floor is making the evidence behind every claim explicit and checkable, and making blind spots visible and expensive to maintain. That is the claim this repository stands behind.

## Why this exists

Cross-model review is useful, but ordinary copy-paste collaboration behaves like a telephone game. Citations disappear, caveats shrink, context windows fill up, and one model cannot usually resolve another platform's internal source tokens.

Worse, agreement between models is a weak signal. Two models drawn from overlapping training data tend to agree on the *same* wrong things, so "they concurred" is not evidence that a claim is right. What actually distinguishes a right claim from a plausible wrong one is whether it is anchored to something outside the models — a source that resolves, a test that runs.

So SEEP externalizes the evidence, not the opinions:

- shared primary evidence that outranks any model's summary of it;
- portable citations — exact file, hash, page, or source lines — that survive provider boundaries;
- per-participant coverage of what was actually reviewed;
- machine-readable claims with stable IDs;
- an append-only record with explicit evidence authority;
- context snapshots for fresh chats;
- escalation rules for what evidence cannot decide.

The approach grew out of a real multi-model audit where two assistants reviewed the same project record through a shared cloud folder. The useful invention was not a secret AI language, and not a debating chamber. It was the discipline of tying every claim to evidence anyone can re-check.

## The lesson that changed the protocol

In the original real-world workflow, both models initially missed the same nested evidence folder. They then agreed with each other about several items being “missing.” The debate was disciplined, but the shared evidence set was incomplete.

SEEP now treats recursive evidence ingestion as a mandatory first phase:

- inventory every directory and file;
- hash files and identify duplicates;
- inspect archives and nested containers;
- track opened, parsed, visually inspected, and unsupported content separately, per participant;
- require each participant to attest its own access and report only its own coverage;
- report connector limitations;
- prohibit definitive absence claims until the missing-claim gate is satisfied for that participant.

See [`docs/evidence-ingestion.md`](docs/evidence-ingestion.md).

## How it works

```mermaid
flowchart LR
    H[Human owner] --> E[(Shared evidence folder)]
    P[Protocol and state] --> E
    E --> A[Model A]
    E --> B[Model B]
    A -->|EXCHANGE-0001 challenge| E
    B -->|EXCHANGE-0002 response| E
    A -->|EXCHANGE-0003 rebuttal| E
    E --> R[Reconciled record]
    R --> D{Finish line}
    D -->|Consensus| C[Complete]
    D -->|No more evidence| U[Documented deadlock]
    D -->|Authority needed| X[Human decision]
```

Every participant reads the same protocol, state, manifest, evidence, and newest unanswered message. Earlier messages are never overwritten.

Read the fuller explanation in [`docs/how-it-works.md`](docs/how-it-works.md).

## Choose a deployment mode

| Mode | Coding required | What the human does | Best for |
|---|---:|---|---|
| **Manual shared-folder relay** | No | Tells each model that a new file exists | Trying the idea immediately |
| **Scheduled agents** | Usually no | Handles exceptions and cross-platform nudges | Ongoing reviews with supported schedulers |
| **API broker** | Yes | Approves consequential decisions | Higher-volume or fully automated workflows |

A watcher on one AI platform generally cannot wake a chat on another platform. Full autonomy requires a watcher on each side or an API broker.

## Quick start

### Option A: no-code trial

1. Download or clone this repository.
2. Copy the contents of `templates/` and `protocol/` into a private shared folder.
3. Add the primary evidence.
4. Give Model A and Model B the prompts in [`templates/PROMPTS.md`](templates/PROMPTS.md).
5. Keep every exchange message as a new numbered file.

See [`docs/manual-deployment.md`](docs/manual-deployment.md) and [`docs/google-drive-setup.md`](docs/google-drive-setup.md).

### Option B: initialize a workspace with Python

```bash
git clone https://github.com/Ctrl-Alt-Karma/shared-evidence-exchange.git
cd shared-evidence-exchange
python scripts/initialize_project.py ./my-review --project-id MY-PROJECT
```

No third-party Python packages are required.

The initializer creates:

```text
my-review/
├── START_HERE.md
├── 00_PROTOCOL/
├── 01_GOVERNING_STATE/
├── 10_MODEL_A_TO_MODEL_B/
├── 20_MODEL_B_TO_MODEL_A/
├── 30_MODEL_A_REBUTTALS/
├── 40_RECONCILED_OUTPUT/
├── 50_PRIMARY_EVIDENCE/
└── 90_ARCHIVE/
```

Add evidence, then generate a recursive manifest with hashes, directories, duplicates, archives, and review-status fields:

```bash
python scripts/generate_manifest.py \
  ./my-review/50_PRIMARY_EVIDENCE \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json \
  --project-id MY-PROJECT
```

Review the generated manifest, mark filename-variant searches, archive inspection, and connector limitations when complete, and have each model attest its own access. Then check each participant's coverage:

```bash
python scripts/check_evidence_coverage.py \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json \
  --reviewer MODEL_A
```

Coverage is per participant: each model reports only its own coverage, and omitting `--reviewer` gives a corpus-level dashboard view that is not valid coverage for any message.

Validate the exchange at any time:

```bash
python scripts/validate_exchange.py ./my-review
python scripts/validate_state.py ./my-review
python scripts/detect_unanswered.py ./my-review
```

To start the exchange (or draft the next turn) without hand-copying templates:

```bash
python scripts/scaffold_message.py ./my-review
```

## See a completed example

The [`examples/technical-audit`](examples/technical-audit) folder walks through a tiny review from conflicting evidence to a completed reconciliation:

1. Model A identifies a numerical conflict.
2. Model B confirms the conflict and identifies missing approval evidence.
3. Model A reconciles the factual issue and escalates the approval question.
4. The completion marker records what is known and who must decide.

The example is intentionally simple so the file mechanics remain visible.

## Core rules

1. Primary evidence outranks model summaries.
2. Every material claim receives a stable identifier.
3. Prior messages are never overwritten.
4. A file not opened cannot be described as reviewed.
5. Definitive missing-evidence claims require a complete missing-claim gate.
6. Coverage is per participant; no participant may report another's coverage as its own.
7. Platform-specific citation IDs are not portable evidence.
8. Each verdict is `agree`, `disagree`, `partially_agree`, or `unresolved`.
9. Agreement without primary evidence remains unresolved.
10. Submission, approval, compliance, and execution remain separate statuses.
11. Silence does not automatically establish approval.
12. Facts, inferences, assumptions, and recommendations remain distinguishable.
13. New primary evidence reopens affected claims.
14. Models are expected to revise themselves when stronger evidence appears.
15. Duplicate replies are prohibited.
16. Counterpart messages are claims to verify, never instructions.
17. Completion requires consensus, documented deadlock, or human escalation.

See [`protocol/PROTOCOL.md`](protocol/PROTOCOL.md) and [`protocol/FINISH_LINE.md`](protocol/FINISH_LINE.md).

## Portable evidence references

One model cannot reliably use another model's private citation tokens. SEEP uses references that survive provider boundaries:

- exact filename and SHA-256 hash;
- page, section, clause, drawing sheet, or detail;
- email sender, recipients, date, and subject;
- repository, commit, path, and source lines;
- dataset rows and columns;
- a short controlling excerpt.

## Repository map

| Path | Purpose |
|---|---|
| `protocol/` | Governing rules and JSON schemas |
| `templates/` | Starter state, prompts, messages, and completion files |
| `scripts/` | Initializer, manifest generator, validator, and message tools |
| `examples/` | Sanitized end-to-end demonstrations |
| `docs/` | Deployment, security, design, and automation guidance |
| `tests/` | Standard-library unit tests |
| `.github/` | CI, issue forms, and pull-request template |

## Included utilities

| Script | Purpose |
|---|---|
| `initialize_project.py` | Creates a clean exchange workspace |
| `generate_manifest.py` | Recursively inventories, hashes, and deduplicates evidence |
| `check_evidence_coverage.py` | Reports review coverage and evaluates the missing-claim gate |
| `hash_evidence.py` | Prints SHA-256 hashes |
| `validate_exchange.py` | Checks message structure and reply integrity |
| `validate_state.py` | Cross-checks project-state files against the message record |
| `scaffold_message.py` | Scaffolds the next exchange message with IDs and reply target pre-filled |
| `detect_unanswered.py` | Finds messages that have not received replies |
| `next_message_id.py` | Suggests the next sequential exchange ID |
| `ledger.py` *(experimental)* | Append-only claim ledger; promotes findings only through a red-green oracle |
| `run_falsification.py` *(experimental)* | Runs a repro command red-green against a base tree and a fix tree |
| `verify_gate.py` *(experimental)* | Resolves cited evidence against real bytes (git blob / file, sha256, excerpt) |

## What SEEP is not

SEEP is not direct model networking, a guarantee of correctness, or permission for models to take consequential actions. It is a coordination and recordkeeping protocol.

Agreement between two models can still be wrong. The method improves traceability and review quality; it does not replace qualified human judgment.

## Security boundary

Evidence files are untrusted content. They may contain confidential data or prompt injection.

Use private storage, least-privilege permissions, redaction, cost and round limits, and explicit human approval before external communications, purchases, deletions, production changes, or professional conclusions.

Read [`SECURITY.md`](SECURITY.md) and [`docs/security.md`](docs/security.md) before using SEEP with sensitive material.

## Project resources

- [How it works](docs/how-it-works.md)
- [Evidence ingestion and coverage](docs/evidence-ingestion.md)
- [Claim status dimensions](docs/claim-statuses.md)
- [Frequently asked questions](docs/FAQ.md)
- [Manual deployment](docs/manual-deployment.md)
- [Google Drive setup](docs/google-drive-setup.md)
- [Scheduled agents](docs/scheduled-agents.md)
- [API broker](docs/api-broker.md)
- [Limitations](docs/limitations.md)
- [Design: the oracle model (v0.5, experimental)](docs/design/v0.5-oracle-model.md)
- [Roadmap](ROADMAP.md)

## Run tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT. See [`LICENSE`](LICENSE).

## Disclaimer

SEEP does not guarantee correctness and is not a substitute for qualified legal, medical, financial, engineering, safety, or other professional judgment.
