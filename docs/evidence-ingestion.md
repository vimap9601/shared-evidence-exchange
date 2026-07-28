# Evidence Ingestion and Coverage

The strongest debate protocol cannot rescue an incomplete evidence set. Two models can confidently agree and still be wrong when both miss the same folder.

SEEP therefore treats evidence ingestion as **Phase 0**, not clerical setup.

## Required sequence

1. Recursively inventory the evidence root.
2. Record every directory and file.
3. Hash each file and identify exact duplicates.
4. Identify archives and nested containers.
5. Classify authority and source type.
6. Each participant confirms it can open every manifest path, then adds its ID to `access_attested_by`.
7. Track which participants opened, parsed, and visually inspected each file (`opened_by`, `parsed_by`, `visually_inspected_by`), and which files are unsupported.
8. Document connector and file-format limitations.
9. Generate a per-participant coverage report before making absence claims.

## Generate the manifest

```bash
python scripts/generate_manifest.py \
  ./my-review/50_PRIMARY_EVIDENCE \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json \
  --project-id MY-PROJECT
```

The generator recursively records directories, extensions, sizes, modification times, SHA-256 hashes, archive status, and duplicate groups. Review fields begin empty and are updated by each participant as it examines the evidence.

The generator attests only to what it did locally: `local_inventory_complete` is set, while `connector_limitations_documented` and `access_attested_by` start unset. A local filesystem walk cannot know what a Drive or SharePoint connector will actually serve to each model, so those controls are asserted by participants, never pre-checked by the tool.

## Check coverage

Coverage is per participant. Each participant reports its own coverage with its own ID:

```bash
python scripts/check_evidence_coverage.py \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json \
  --reviewer MODEL_B
```

The resulting report is what goes into that participant's `evidence_coverage` message block; its `reviewer` field must equal the message sender. Omitting `--reviewer` produces a corpus-level union report for the human dashboard — it is not valid coverage for any participant's message.

To fail a workflow when the missing-claim gate is not ready:

```bash
python scripts/check_evidence_coverage.py \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json \
  --reviewer MODEL_B \
  --require-missing-claim-gate
```

## The missing-claim gate

Do not write “missing,” “not provided,” or “absent” unless all of these are true for you:

- recursive inventory is complete;
- relevant filename and terminology variants were searched;
- archives and nested containers were inspected;
- connector limitations are documented;
- no relevant folder remains outside recursive review;
- you have attested your own access to every path in the manifest.

Until then, say:

> Not located in the evidence reviewed to date.

## Coverage is multidimensional

These are not interchangeable:

- **opened:** the file was accessed;
- **parsed:** machine-readable content was inspected;
- **visually inspected:** pages, diagrams, tables, screenshots, or drawings were rendered and reviewed;
- **reviewed:** the file received the level of review necessary for the claim at issue;
- **unsupported:** the available tooling could not inspect the content reliably.

A PDF can be parsed without its drawings being visually inspected. A native model file can be opened without its internal data being validated. The coverage report should preserve those distinctions.

## New evidence

When new primary evidence is added:

1. create a new manifest version;
2. identify changed hashes and new paths;
3. reopen every affected claim;
4. create a new numbered exchange message;
5. never silently edit the prior conclusion.
