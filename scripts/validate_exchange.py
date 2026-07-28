from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from common import discover_messages, load_json, validate_message


def find_manifest(root: Path) -> Path | None:
    candidates = sorted(root.rglob("EVIDENCE_MANIFEST.json"))
    return candidates[0] if candidates else None


def validate_sources_against_manifest(path: Path, message: dict, manifest: dict) -> list[str]:
    errors: list[str] = []
    records = {
        item.get("path"): item
        for item in manifest.get("files", [])
        if isinstance(item, dict)
    }
    for claim in message.get("claims", []):
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("claim_id", "?")
        cited = claim.get("sources", [])
        if isinstance(claim.get("counterevidence"), list):
            cited = list(cited) + claim["counterevidence"]
        if not isinstance(cited, list):
            continue
        for source in cited:
            if not isinstance(source, dict):
                continue
            file_ref = source.get("file")
            if not isinstance(file_ref, str) or not file_ref:
                continue
            record = records.get(file_ref)
            if record is None:
                errors.append(
                    f"{path}: claim {claim_id} cites {file_ref}, which is not in the evidence manifest"
                )
                continue
            cited_hash = source.get("sha256")
            if cited_hash and cited_hash.lower() != str(record.get("sha256", "")).lower():
                errors.append(
                    f"{path}: claim {claim_id} cites {file_ref} with sha256 {cited_hash}, "
                    f"but the manifest records {record.get('sha256')}"
                )
    return errors


def validate_exchange(root: Path, manifest_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    messages = discover_messages(root)
    if not messages:
        return ["no EXCHANGE-*.json messages found"]

    manifest = None
    if manifest_path is None:
        manifest_path = find_manifest(root)
    if manifest_path is not None:
        try:
            manifest = load_json(manifest_path)
        except (OSError, ValueError) as exc:
            errors.append(f"could not load evidence manifest {manifest_path}: {exc}")

    ids = [m["message_id"] for _, m in messages]
    for message_id, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate message_id {message_id} appears {count} times")
    id_set = set(ids)
    senders = {m["message_id"]: m.get("sender") for _, m in messages}
    replies: Counter[str] = Counter()
    for path, message in messages:
        errors.extend(f"{path}: {e}" for e in validate_message(message))
        target = message.get("in_reply_to")
        if target:
            replies[target] += 1
            if target not in id_set:
                errors.append(f"{path}: in_reply_to references missing message {target}")
        corrects = message.get("corrects_message_id")
        if isinstance(corrects, str) and message.get("message_type") == "correction":
            if corrects not in id_set:
                errors.append(f"{path}: corrects_message_id references missing message {corrects}")
            elif senders.get(corrects) != message.get("sender"):
                errors.append(
                    f"{path}: correction targets {corrects}, which was sent by "
                    f"{senders.get(corrects)}; a participant corrects only its own messages"
                )
        if manifest is not None:
            errors.extend(validate_sources_against_manifest(path, message, manifest))
    for target, count in replies.items():
        if count > 1:
            errors.append(f"message {target} has {count} replies; expected at most one")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a SEEP exchange.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--manifest", type=Path, help="Evidence manifest to check claim sources against (default: first EVIDENCE_MANIFEST.json found under root).")
    args = parser.parse_args()
    errors = validate_exchange(args.root, args.manifest)
    if errors:
        print("Exchange validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"Exchange valid: {len(discover_messages(args.root))} message(s)")
