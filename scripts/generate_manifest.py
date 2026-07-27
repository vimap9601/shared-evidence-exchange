from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from common import sha256_file


def generate_manifest(evidence_root: Path, project_id: str) -> dict:
    if not evidence_root.is_dir():
        raise ValueError(f"Evidence root is not a directory: {evidence_root}")
    records = []
    for path in sorted(p for p in evidence_root.rglob("*") if p.is_file()):
        stat = path.stat()
        records.append({
            "path": path.relative_to(evidence_root).as_posix(),
            "size_bytes": stat.st_size,
            "sha256": sha256_file(path),
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "authority": "unclassified", "notes": "",
        })
    return {
        "protocol": "SEEP-1.0", "project_id": project_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": evidence_root.as_posix(), "files": records,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an evidence manifest.")
    parser.add_argument("evidence_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--project-id", default="REPLACE-ME")
    args = parser.parse_args()
    manifest = generate_manifest(args.evidence_root, args.project_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(manifest['files'])} evidence records to {args.output}")
