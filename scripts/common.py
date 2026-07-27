from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

MESSAGE_ID_RE = re.compile(r"^EXCHANGE-(\d{4})([A-Z]?)$")
REQUIRED_FIELDS = {
    "protocol", "project_id", "message_id", "in_reply_to", "sender",
    "recipient", "created_at", "message_type", "summary_markdown",
    "claims", "open_questions", "required_response",
}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def discover_messages(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    messages = []
    for path in sorted(root.rglob("EXCHANGE-*.json")):
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if "message_id" in data:
            messages.append((path, data))
    return messages


def validate_message(message: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - message.keys())
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))

    if message.get("protocol") != "SEEP-1.0":
        errors.append("protocol must equal SEEP-1.0")

    message_id = message.get("message_id")
    if not isinstance(message_id, str) or not MESSAGE_ID_RE.fullmatch(message_id):
        errors.append("message_id must match EXCHANGE-0000 or EXCHANGE-0000A")

    reply_to = message.get("in_reply_to")
    if reply_to is not None:
        if not isinstance(reply_to, str) or not MESSAGE_ID_RE.fullmatch(reply_to):
            errors.append("in_reply_to must be null or a valid exchange ID")
        if reply_to == message_id:
            errors.append("a message cannot reply to itself")

    sender, recipient = message.get("sender"), message.get("recipient")
    if sender and recipient and sender == recipient:
        errors.append("sender and recipient must differ")

    claims = message.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be an array")
    else:
        seen: set[str] = set()
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append(f"claims[{index}] must be an object")
                continue
            claim_id = claim.get("claim_id")
            if not isinstance(claim_id, str) or not claim_id:
                errors.append(f"claims[{index}].claim_id is required")
            elif claim_id in seen:
                errors.append(f"duplicate claim_id in message: {claim_id}")
            else:
                seen.add(claim_id)
            confidence = claim.get("confidence")
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                errors.append(f"claims[{index}].confidence must be numeric")
            elif not 0 <= confidence <= 1:
                errors.append(f"claims[{index}].confidence must be between 0 and 1")
            if not isinstance(claim.get("sources"), list):
                errors.append(f"claims[{index}].sources must be an array")

    if not isinstance(message.get("open_questions"), list):
        errors.append("open_questions must be an array")
    if not isinstance(message.get("required_response"), dict):
        errors.append("required_response must be an object")
    return errors
