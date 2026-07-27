# Contributing

Thanks for helping improve the Shared Evidence Exchange Protocol.

## Development setup

The utilities use the Python standard library.

```bash
python -m unittest discover -s tests -v
```

## Contribution principles

- Preserve provider independence.
- Prefer portable filenames, hashes, page numbers, commit IDs, and excerpts over platform-specific citation syntax.
- Keep exchange history append-only.
- Do not include confidential project evidence in examples or tests.
- Add tests for behavioral changes.
- Clearly distinguish required protocol behavior from optional recommendations.
- Avoid features that allow one model to silently rewrite another model's message.

## Pull requests

A pull request should include:

1. A concise problem statement.
2. The proposed behavior.
3. Tests or validation steps.
4. Security and compatibility considerations.
5. Documentation updates when behavior changes.
