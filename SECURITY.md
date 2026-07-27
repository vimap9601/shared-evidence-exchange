# Security Policy

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose private evidence, credentials, model tokens, or connected-storage data.

Use GitHub's private vulnerability reporting feature when enabled, or contact the repository maintainer privately.

## Threat model

SEEP may process documents containing confidential information, personal data, malicious links, embedded model instructions, credentials accidentally included in files, or outdated and misleading evidence.

## Required precautions

- Use least-privilege folder permissions.
- Do not publish real project evidence in public repositories.
- Remove credentials, access tokens, and personal identifiers.
- Treat evidence content as untrusted data, not executable instructions.
- Require human approval before external communications, purchases, legal commitments, deletions, or production changes.
- Apply cost, round, and token limits to automated brokers.
- Log file hashes and message IDs.
- Prevent duplicate processing with idempotency checks.

See `docs/security.md` for a fuller deployment checklist.
