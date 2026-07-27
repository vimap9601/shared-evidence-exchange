from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from common import sha256_file

ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".bz2", ".xz"}


def generate_manifest(evidence_root: Path, project_id: str) -> dict:
    if not evidence_root.is_dir():
        raise ValueError(f"Evidence root is not a directory: {evidence_root}")

    paths = sorted(p for p in evidence_root.rglob("*") if p.is_file())
    directories = sorted(
        p.relative_to(evidence_root).as_posix()
        for p in evidence_root.rglob("*")
        if p.is_dir()
    )

    raw_records: list[dict] = []
    hashes: defaultdict[str, list[str]] = defaultdict(list)
    extension_counts: Counter[str] = Counter()
    directory_counts: Counter[str] = Counter()
    archive_files: list[str] = []

    for path in paths:
        relative = path.relative_to(evidence_root).as_posix()
        directory = path.parent.relative_to(evidence_root).as_posix()
        if directory == ".":
            directory = ""
        extension = path.suffix.lower()
        digest = sha256_file(path)
        stat = path.stat()
        is_archive = extension in ARCHIVE_EXTENSIONS

        hashes[digest].append(relative)
        extension_counts[extension or "[no extension]"] += 1
        directory_counts[directory or "[root]"] += 1
        if is_archive:
            archive_files.append(relative)

        raw_records.append({
            "path": relative,
            "directory": directory,
            "extension": extension,
            "size_bytes": stat.st_size,
            "sha256": digest,
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "is_archive": is_archive,
            "archive_inspected": not is_archive,
            "review_status": "unreviewed",
            "opened": False,
            "parsed": False,
            "visually_inspected": False,
            "assigned_reviewer": None,
            "reviewed_by": [],
            "authority": "unclassified",
            "source_class": "unclassified",
            "duplicate_of": None,
            "notes": "",
        })

    canonical_by_hash = {digest: paths[0] for digest, paths in hashes.items()}
    for record in raw_records:
        canonical = canonical_by_hash[record["sha256"]]
        if record["path"] != canonical:
            record["duplicate_of"] = canonical

    duplicate_groups = [
        {"sha256": digest, "paths": grouped_paths}
        for digest, grouped_paths in sorted(hashes.items())
        if len(grouped_paths) > 1
    ]

    return {
        "protocol": "SEEP-1.0",
        "project_id": project_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": evidence_root.as_posix(),
        "inventory_complete": True,
        "directories": directories,
        "summary": {
            "files_total": len(raw_records),
            "bytes_total": sum(record["size_bytes"] for record in raw_records),
            "files_by_extension": dict(sorted(extension_counts.items())),
            "files_by_directory": dict(sorted(directory_counts.items())),
            "duplicate_groups": duplicate_groups,
            "archive_files": archive_files,
        },
        "coverage_controls": {
            "recursive_inventory_complete": True,
            "relevant_filename_variants_searched": False,
            "archives_and_nested_containers_inspected": not archive_files,
            "connector_limitations_documented": True,
            "known_connector_limitations": [],
            "folders_not_recursively_reviewed": [],
        },
        "files": raw_records,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a recursive SEEP evidence manifest.")
    parser.add_argument("evidence_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--project-id", default="REPLACE-ME")
    args = parser.parse_args()

    manifest = generate_manifest(args.evidence_root, args.project_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {manifest['summary']['files_total']} evidence records, "
        f"{len(manifest['directories'])} directories, and "
        f"{len(manifest['summary']['duplicate_groups'])} duplicate groups to {args.output}"
    )
