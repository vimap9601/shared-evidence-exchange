# Changelog

All notable changes will be documented here.

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
