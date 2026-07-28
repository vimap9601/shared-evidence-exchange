from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_json


def build_coverage_report(
    manifest: dict,
    manifest_file: str = "EVIDENCE_MANIFEST.json",
    reviewer: str | None = None,
) -> dict:
    files = manifest.get("files", [])
    controls = manifest.get("coverage_controls", {})

    def covered(item: dict, key: str) -> bool:
        participants = item.get(key, [])
        if not isinstance(participants, list):
            return False
        if reviewer is None:
            return bool(participants)
        return reviewer in participants

    files_total = len(files)
    files_opened = sum(covered(item, "opened_by") for item in files)
    files_parsed = sum(covered(item, "parsed_by") for item in files)
    files_visually_inspected = sum(covered(item, "visually_inspected_by") for item in files)
    unsupported_file_types = sorted({
        item.get("extension", "") or "[no extension]"
        for item in files
        if item.get("review_status") == "unsupported"
    })
    archives_not_inspected = [
        item.get("path", "")
        for item in files
        if item.get("is_archive") and not item.get("archive_inspected")
    ]
    folders_not_reviewed = list(controls.get("folders_not_recursively_reviewed", []))
    connector_limitations = list(controls.get("known_connector_limitations", []))
    access_attested_by = list(controls.get("access_attested_by", []))
    access_attested = reviewer in access_attested_by if reviewer is not None else bool(access_attested_by)

    gate_conditions = [
        bool(manifest.get("inventory_complete")),
        bool(controls.get("local_inventory_complete")),
        bool(controls.get("relevant_filename_variants_searched")),
        bool(controls.get("archives_and_nested_containers_inspected")),
        bool(controls.get("connector_limitations_documented")),
        not folders_not_reviewed,
        not archives_not_inspected,
    ]
    if reviewer is not None:
        # The gate is per participant: a reviewer who has not attested
        # access to every manifest path may not claim evidence is absent.
        gate_conditions.append(access_attested)
    missing_claim_gate_satisfied = all(gate_conditions)

    return {
        "manifest_file": manifest_file,
        "reviewer": reviewer,
        "inventory_complete": bool(manifest.get("inventory_complete")),
        "files_total": files_total,
        "files_opened": files_opened,
        "files_parsed": files_parsed,
        "files_visually_inspected": files_visually_inspected,
        "files_not_opened": files_total - files_opened,
        "folders_not_recursively_reviewed": folders_not_reviewed,
        "unsupported_file_types": unsupported_file_types,
        "archives_not_inspected": archives_not_inspected,
        "known_connector_limitations": connector_limitations,
        "access_attested_by": access_attested_by,
        "access_attested": access_attested,
        "missing_claim_gate_satisfied": missing_claim_gate_satisfied,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize evidence coverage and evaluate the missing-evidence claim gate.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--reviewer", help="Report one participant's own coverage. A message's evidence_coverage block must be generated with the sender's ID here.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-missing-claim-gate", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    manifest = load_json(args.manifest)
    report = build_coverage_report(manifest, args.manifest.as_posix(), args.reviewer)
    rendered = json.dumps(report, indent=2) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote coverage report to {args.output}")
    else:
        print(rendered, end="")

    if args.require_missing_claim_gate and not report["missing_claim_gate_satisfied"]:
        raise SystemExit(2)
