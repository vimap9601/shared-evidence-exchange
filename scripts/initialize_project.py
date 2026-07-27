from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

FOLDERS = [
    "00_PROTOCOL", "01_GOVERNING_STATE", "10_MODEL_A_TO_MODEL_B",
    "20_MODEL_B_TO_MODEL_A", "30_MODEL_A_REBUTTALS",
    "40_RECONCILED_OUTPUT", "50_PRIMARY_EVIDENCE", "90_ARCHIVE",
]


def initialize(destination: Path, project_id: str, force: bool = False) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if destination.exists() and any(destination.iterdir()) and not force:
        raise SystemExit(f"{destination} is not empty. Use --force to add missing files.")
    destination.mkdir(parents=True, exist_ok=True)
    for folder in FOLDERS:
        (destination / folder).mkdir(exist_ok=True)

    mapping = [
        (repo_root / "templates/START_HERE.md", destination / "START_HERE.md"),
        (repo_root / "protocol/PROTOCOL.md", destination / "00_PROTOCOL/PROTOCOL.md"),
        (repo_root / "protocol/FINISH_LINE.md", destination / "00_PROTOCOL/FINISH_LINE.md"),
        (repo_root / "protocol/RESPONSE_SCHEMA.json", destination / "00_PROTOCOL/RESPONSE_SCHEMA.json"),
        (repo_root / "protocol/STATE_SCHEMA.json", destination / "00_PROTOCOL/STATE_SCHEMA.json"),
        (repo_root / "protocol/EVIDENCE_MANIFEST_SCHEMA.json", destination / "00_PROTOCOL/EVIDENCE_MANIFEST_SCHEMA.json"),
    ]
    for source, target in mapping:
        if not target.exists():
            shutil.copy2(source, target)

    state = json.loads((repo_root / "templates/PROJECT_STATE_0001.json").read_text())
    state["project_id"] = project_id
    state_path = destination / "01_GOVERNING_STATE/PROJECT_STATE_0001.json"
    if not state_path.exists():
        state_path.write_text(json.dumps(state, indent=2) + "\n")

    manifest = json.loads((repo_root / "templates/EVIDENCE_MANIFEST.json").read_text())
    manifest["project_id"] = project_id
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
    manifest_path = destination / "01_GOVERNING_STATE/EVIDENCE_MANIFEST.json"
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Initialized SEEP workspace: {destination.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a SEEP workspace.")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--project-id", default="REPLACE-ME")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    initialize(args.destination, args.project_id, args.force)
