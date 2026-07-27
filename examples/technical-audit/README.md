# Technical Audit Example

This sanitized example demonstrates a simple numerical conflict:

- the governing requirement states 70 C maximum;
- the vendor submission states 82 C maximum;
- Model A raises the conflict;
- Model B agrees on the numerical issue but leaves deviation approval unresolved.

Run from the repository root:

```bash
python scripts/validate_exchange.py examples/technical-audit
python scripts/detect_unanswered.py examples/technical-audit
```
