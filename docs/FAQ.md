# Frequently Asked Questions

## Do the AI models communicate directly?

Not in the basic setup. They communicate indirectly by reading and writing numbered files in shared storage. A human may still need to tell the next model that a response exists.

Direct autonomous exchange requires scheduled watchers on both platforms or an API broker.

## Do I need an API or programming experience?

No. The manual workflow works with ordinary chat products and a shared folder. Python utilities are included for initialization, hashing, validation, and automation, but they are optional.

## Why not use one shared Google Doc?

A single editable document makes silent changes, overwrites, conflicting edits, and unclear authorship much more likely. Append-only files preserve the full history and make each turn independently inspectable.

## Why combine JSON and Markdown?

JSON makes claims, reply relationships, verdicts, confidence, and sources machine-checkable. Markdown remains comfortable for humans. SEEP uses JSON for structured exchange messages and Markdown for protocols, context snapshots, and final reports.

## What happens when only one model can write to the folder?

The read-only model can generate the correctly named response file for the human to upload. The workflow remains useful because the human transfers a complete file rather than summarizing the argument.

## Can I use the same model twice?

Yes. Two fresh sessions with different roles, prompts, or evidence-review duties can still reduce context contamination. Cross-provider review is useful because systems may fail differently, but it is not required.

## Does model consensus prove that a claim is true?

No. Multiple models can share the same blind spot. Consensus means the exchange has no remaining model-level disagreement under the reviewed evidence, not that reality has issued a warranty.

## What if the models never agree?

That is an acceptable outcome. The finish-line rule allows a documented deadlock when each side has presented its strongest evidence and no unreviewed evidence path remains.

## How should large evidence sets be handled?

Use an evidence manifest, hashes, narrow source references, and staged review packets. Do not force every model to ingest every file on every turn. Retrieve only the evidence needed for the claims being tested.

## Can a model treat text inside an evidence file as instructions?

It should not. The governing protocol should explicitly state that evidence content is untrusted data to analyze, not executable instruction.

## Is this appropriate for confidential material?

Only when the storage, model providers, permissions, retention settings, and organizational policies are appropriate for that data. Redact aggressively and never publish real evidence in a public repository.

## How do I know whose turn it is?

Each message has a `message_id`, `sender`, `recipient`, and `in_reply_to`. The `detect_unanswered.py` utility identifies messages that have not received a reply.

## How does the review end?

Through one of three outcomes:

1. consensus on the material claims and action plan;
2. documented deadlock with no remaining evidence path; or
3. an explicit human decision requirement.

The completion marker summarizes the final state.

## Can both models agree and still be wrong?

Yes. Shared blind spots are the central danger. If both models overlook the same folder or cannot inspect the same file type, adversarial debate can produce confident mutual error. SEEP's recursive manifest, coverage report, and missing-claim gate exist specifically to expose that condition.

## When may a model say a file or datum is missing?

Only after the recursive inventory is complete, relevant filename variants have been searched, archives and nested containers have been inspected, connector limitations are documented, and no relevant folder remains outside review. Before then, use “Not located in the evidence reviewed to date.”

## Does parsing a PDF mean it was fully reviewed?

No. Parsed text, opened files, and visual inspection are separate coverage states. Drawings, diagrams, tables, annotations, and scanned pages may require rendering even when text extraction succeeds.
