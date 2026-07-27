# Evidence Ingestion and Coverage

The strongest debate protocol cannot rescue an incomplete evidence set. Two models can confidently agree and still be wrong when both miss the same folder.

SEEP therefore treats evidence ingestion as **Phase 0**, not clerical setup.

## Required sequence

1. Recursively inventory the evidence root.
2. Record every directory and file.
3. Hash each file and identify exact duplicates.
4. Identify archives and nested containers.
5. Classify authority and source type.
6. Track whether each file was opened, parsed, visually inspected, or unsupported.
7. Document connector and file-format limitations.
8. Generate a coverage report before making absence claims.

## Generate the manifest

```bash
python scripts/generate_manifest.py \
  ./my-review/50_PRIMARY_EVIDENCE \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json \
  --project-id MY-PROJECT
```

The generator recursively records directories, extensions, sizes, modification times, SHA-256 hashes, archive status, and duplicate groups. Review fields begin as `unreviewed` and should be updated as the evidence is examined.

## Check coverage

```bash
python scripts/check_evidence_coverage.py \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json
```

To fail a workflow when the missing-claim gate is not ready:

```bash
python scripts/check_evidence_coverage.py \
  ./my-review/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json \
  --require-missing-claim-gate
```

## The missing-claim gate

Do not write “missing,” “not provided,” or “absent” unless all of these are true:

- recursive inventory is complete;
- relevant filename and terminology variants were searched;
- archives and nested containers were inspected;
- connector limitations are documented;
- no relevant folder remains outside recursive review.

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
