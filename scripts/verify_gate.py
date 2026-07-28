from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

# Citation-resolution oracle (experimental, SEEP v0.5 preview).
#
# A model claiming "file F at commit C contains bytes B" is a belief until an
# oracle resolves it. This resolves each cited evidence unit against the actual
# repository or filesystem and reports match / mismatch / unresolved. No model
# is consulted. See docs/design/v0.5-oracle-model.md.


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_git_blob(repo: Path, commit: str, path: str) -> bytes | None:
    # `git show C:path` is the oracle for a claim pinned to a commit; a missing
    # object or path resolves to None (unresolved), never an exception.
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"{commit}:{path}"],
            capture_output=True,
            check=False,
        )
    except (OSError, ValueError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def resolve_evidence(evidence: dict[str, Any], repo: Path | None) -> dict[str, Any]:
    """Resolve one evidence unit to a verdict. Verdicts are oracle facts:
    `match`, `hash_mismatch`, `excerpt_absent`, or `unresolved`."""
    evidence_id = evidence.get("evidence_id", "?")
    path = evidence.get("file")
    if not isinstance(path, str) or not path:
        return {"evidence_id": evidence_id, "verdict": "unresolved", "detail": "no file reference"}

    commit = evidence.get("commit")
    data: bytes | None
    if commit:
        if repo is None:
            return {
                "evidence_id": evidence_id,
                "verdict": "unresolved",
                "detail": "commit-pinned evidence but no --repo given",
            }
        data = read_git_blob(repo, str(commit), path)
    else:
        base = repo if repo is not None else Path.cwd()
        target = base / path
        data = target.read_bytes() if target.is_file() else None

    if data is None:
        return {
            "evidence_id": evidence_id,
            "verdict": "unresolved",
            "detail": f"could not resolve {path}" + (f"@{commit}" if commit else ""),
        }

    cited_hash = evidence.get("sha256")
    if isinstance(cited_hash, str) and cited_hash:
        actual = _sha256_bytes(data)
        if actual.lower() != cited_hash.lower():
            return {
                "evidence_id": evidence_id,
                "verdict": "hash_mismatch",
                "detail": f"cited {cited_hash}, resolved {actual}",
            }

    excerpt = evidence.get("excerpt")
    if isinstance(excerpt, str) and excerpt:
        try:
            text = data.decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover - decode with replace does not raise
            text = ""
        if excerpt not in text:
            return {
                "evidence_id": evidence_id,
                "verdict": "excerpt_absent",
                "detail": "cited excerpt not found in resolved bytes",
            }

    return {"evidence_id": evidence_id, "verdict": "match", "detail": ""}


def verify_citations(evidence_units: list[dict[str, Any]], repo: Path | None) -> list[dict[str, Any]]:
    return [resolve_evidence(unit, repo) for unit in evidence_units]


def load_evidence(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("evidence"), list):
        return data["evidence"]
    if isinstance(data, list):
        return data
    raise ValueError(f"{path}: expected a list of evidence units or an object with an 'evidence' array")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Resolve cited evidence against real bytes (git blob or file + sha256)."
    )
    parser.add_argument("evidence", type=Path, help="JSON list of evidence units, or {'evidence': [...]}.")
    parser.add_argument("--repo", type=Path, help="Repository root for commit-pinned or relative citations.")
    args = parser.parse_args()

    results = verify_citations(load_evidence(args.evidence), args.repo)
    bad = [r for r in results if r["verdict"] != "match"]
    for result in results:
        line = f"{result['verdict']:<14} {result['evidence_id']}"
        if result["detail"]:
            line += f"  ({result['detail']})"
        print(line)
    if bad:
        print(f"\n{len(bad)} of {len(results)} citation(s) did not resolve to a match.")
        raise SystemExit(1)
    print(f"\nAll {len(results)} citation(s) resolved.")
