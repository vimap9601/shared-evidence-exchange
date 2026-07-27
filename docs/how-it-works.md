# How SEEP Works

The Shared Evidence Exchange Protocol lets otherwise isolated AI systems collaborate through ordinary shared storage.

## The problem it solves

When a person manually copies answers between AI chats, important qualifications, citations, uncertainty, and context gradually disappear. Large chats also become expensive and fragile, and one model cannot usually resolve another platform's internal citation tokens.

SEEP externalizes the collaboration into files that both models and the human can inspect.

## Phase 0: prove the corpus

Before either model reviews the substance, SEEP recursively inventories the evidence, hashes files, identifies duplicates and archives, and records review coverage. This prevents two models from reinforcing the same error because both overlooked the same folder.

Definitive absence claims are blocked until the missing-claim gate is satisfied. See [`evidence-ingestion.md`](evidence-ingestion.md).

## The exchange model

Each participant reads:

- the same protocol;
- the same project state;
- the same evidence manifest;
- the same primary evidence;
- the newest unanswered message.

Each participant writes a new numbered JSON file. Earlier messages are never overwritten.

A typical sequence is:

```text
EXCHANGE-0001_MODEL_A_CHALLENGE.json
EXCHANGE-0002_MODEL_B_RESPONSE.json
EXCHANGE-0003_MODEL_A_REBUTTAL.json
EXCHANGE-0004_MODEL_B_FINAL_RESPONSE.json
```

## Why JSON and Markdown are combined

JSON makes claims, verdicts, reply relationships, confidence, and sources machine-checkable. Markdown remains readable for humans and can be embedded in summary fields or used for context snapshots and final reports.

## Portable evidence

One model's private citation ID is meaningless to another. SEEP instead uses portable evidence references such as exact filename, hash, page, clause, drawing sheet, email date and subject, repository commit, source lines, dataset rows, and a short excerpt.

## Fresh chats without amnesia

When a chat becomes too large or reaches a usage limit, the model's latest meaningful position can be saved as a non-governing context snapshot. A fresh chat reads the snapshot but must verify every material conclusion against primary evidence.

## Human-in-the-loop mode

No programming is required. The human only announces that a new response file exists. The human does not relay or summarize the substantive argument.

## Scheduled-agent mode

A scheduled task can periodically check for new messages. Each AI platform generally needs its own watcher because one platform cannot automatically wake another platform's chat session.

## API-broker mode

A broker can poll the folder, call multiple model APIs, validate responses, enforce budgets, prevent duplicate replies, and stop when the finish-line rule is satisfied.

## What completion means

The exchange ends through consensus, documented deadlock, or an explicit human-decision requirement. A completion marker summarizes the agreed facts, corrected state, unresolved questions, and the people who must decide what remains.

The goal is not to make models agree. The goal is to make their claims inspectable, challengeable, and traceable to evidence.
