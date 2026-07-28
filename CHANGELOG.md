# Changelog

All notable changes will be documented here.

## [Unreleased]

### Fixed

- Unreadable, non-object, or `message_id`-less `EXCHANGE-*.json` files are now reported as errors instead of being silently skipped. Previously `validate_exchange.py` could pass an exchange containing a corrupt message, `detect_unanswered.py` could show an already-answered message as pending (inviting a duplicate reply), and `next_message_id.py` could reissue the corrupt file's number.
- `next_message_id.py` also counts message numbers from filenames, so a corrupt file's ID is never suggested again.
- `validate_exchange.py` reports a non-string `sha256` in a claim source as a validation error instead of crashing.

## [0.4.0] - 2026-07-27

Breaking schema changes from external review. The protocol identifier is now `SEEP-0.4`; it tracks the pre-1.0 release series, and `SEEP-1.0` is reserved for the first frozen schema set.

### Added

- Per-participant evidence coverage: `opened_by`, `parsed_by`, and `visually_inspected_by` arrays replace the shared per-file booleans, so one model can no longer free-ride on the other's coverage record.
- Required `reviewer` field in every message's `evidence_coverage` block; the validator rejects messages whose reviewer is not the sender.
- Per-participant access attestation (`coverage_controls.access_attested_by`) and a `--reviewer` flag on `check_evidence_coverage.py`; the missing-claim gate is now evaluated per participant.
- `corrects_message_id` field and correction rules: corrections reply to the thread head and name their target explicitly, so they no longer collide with the one-reply rule.
- Claim sources are validated against the evidence manifest: cited files must exist in the manifest and cited hashes must match.
- Agreement verdicts (`agree`, `partially_agree`) now require at least one source, enforcing "agreement without primary evidence remains unresolved."
- Consensus now requires the missing-claim gate for every participant, or an explicit coverage-limitations record with `evidence_coverage_status: complete_with_limitations`.
- Optional `max_rounds` in the project state; exceeding it forces documented deadlock or human escalation.
- Human-attestation convention for testimony that only a human can provide.
- Project-state authorship rules and the missing `PROJECT_STATE_0001.json` in the example.
- Protocol and security guidance that counterpart messages are claims to verify, never instructions.

### Changed

- `generate_manifest.py` no longer pre-asserts controls it cannot know: `connector_limitations_documented` defaults to false, and `recursive_inventory_complete` is split into script-assertable `local_inventory_complete` plus per-participant access attestation.
- README no longer claims the ingestion gate prevents shared blind spots; SEEP makes them visible and expensive to maintain.
- Standardized on the term "missing-claim gate."

### Removed

- Repo-construction scaffolding docs (`docs/github-deployment.md`, `docs/upload-checklist.md`).

## [0.3.0] - 2026-07-27

### Added

- Mandatory evidence-ingestion guidance and missing-claim gate.
- Recursive directory inventory, duplicate detection, archive tracking, and review-status fields in evidence manifests.
- Evidence coverage reports in exchange messages.
- `check_evidence_coverage.py` with an enforceable gate mode.
- Claim fields for evidence basis, separate status dimensions, superseded claims, and reopened claims.
- Evidence-ingestion and claim-status documentation.
- Tests for nested folders, duplicates, archives, and coverage-gate evaluation.

### Changed

- Updated prompts, protocol, examples, and quick start to begin with corpus verification.
- Prohibited definitive missing-evidence claims before coverage is complete.
- Clarified that agreement without primary evidence remains unresolved.

## [0.2.0] - 2026-07-27

### Added

- Friendlier public README with badges, deployment modes, repository map, and no-code quick start.
- Frequently asked questions.
- Public roadmap.
- Completed end-to-end technical audit example with reconciliation, final state, and completion marker.

### Changed

- Clarified the boundary between manual relay, scheduled watchers, and full API automation.
- Improved the security and human-authority framing on the repository front page.

## [0.1.0] - 2026-07-27

### Added

- Initial public protocol and folder convention.
- JSON schemas for messages, project state, and evidence manifests.
- Manual, scheduled-agent, and API-broker documentation.
- Project initializer, manifest generator, hashing tool, validator, unanswered-message detector, and message-ID helper.
- Standard-library unit tests and GitHub Actions workflow.
- Sanitized technical-audit example.
