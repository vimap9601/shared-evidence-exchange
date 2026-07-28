from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "SEEP-0.4"
MESSAGE_ID_RE = re.compile(r"^EXCHANGE-(\d{4})([A-Z]?)$")
REQUIRED_FIELDS = {
    "protocol", "project_id", "message_id", "in_reply_to", "sender",
    "recipient", "created_at", "message_type", "summary_markdown",
    "evidence_coverage", "claims", "open_questions", "required_response",
}
AGREEMENT_POSITIONS = {"agree", "partially_agree"}
# These sets mirror protocol/RESPONSE_SCHEMA.json so workspaces need no
# third-party validator; the schema-agreement tests fail if they drift apart.
MESSAGE_TYPES = {
    "audit_challenge", "response", "rebuttal", "correction",
    "reconciliation", "escalation",
}
CLAIM_POSITIONS = {
    "supported", "rejected", "uncertain", "agree", "disagree",
    "partially_agree", "unresolved",
}
CLAIM_MATERIALITY = {"low", "medium", "high", "critical"}
REQUIRED_CLAIM_FIELDS = {
    "claim_id", "statement", "position", "confidence", "materiality",
    "reasoning_summary", "sources",
}
REQUIRED_OPEN_QUESTION_FIELDS = {"question_id", "question", "evidence_needed"}
REQUIRED_COVERAGE_FIELDS = {
    "manifest_file", "reviewer", "inventory_complete", "files_total",
    "files_opened", "files_parsed", "files_visually_inspected",
    "files_not_opened", "folders_not_recursively_reviewed",
    "unsupported_file_types", "archives_not_inspected",
    "known_connector_limitations", "missing_claim_gate_satisfied",
}
SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")


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


def validate_source_entries(prefix: str, sources: list[Any]) -> list[str]:
    errors: list[str] = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"{prefix}[{index}] must be an object")
            continue
        for key in ["file", "authority"]:
            value = source.get(key)
            if not isinstance(value, str) or not value:
                errors.append(f"{prefix}[{index}].{key} must be a nonempty string")
        digest = source.get("sha256")
        if digest is not None and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
            errors.append(f"{prefix}[{index}].sha256 must be 64 hexadecimal characters")
    return errors


def validate_message(message: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - message.keys())
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))

    if message.get("protocol") != PROTOCOL_VERSION:
        errors.append(f"protocol must equal {PROTOCOL_VERSION}")

    if message.get("message_type") not in MESSAGE_TYPES:
        errors.append("message_type must be one of: " + ", ".join(sorted(MESSAGE_TYPES)))

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
    for field in ["project_id", "sender", "recipient"]:
        value = message.get(field)
        if field in message and (not isinstance(value, str) or not value):
            errors.append(f"{field} must be a nonempty string")
    if "summary_markdown" in message and not isinstance(message["summary_markdown"], str):
        errors.append("summary_markdown must be a string")

    corrects = message.get("corrects_message_id")
    if message.get("message_type") == "correction":
        if not isinstance(corrects, str) or not MESSAGE_ID_RE.fullmatch(corrects):
            errors.append("a correction requires corrects_message_id with a valid exchange ID")
        elif corrects == message_id:
            errors.append("a correction cannot correct itself")
    elif corrects is not None:
        errors.append("corrects_message_id is only allowed on correction messages")

    coverage = message.get("evidence_coverage")
    if not isinstance(coverage, dict):
        errors.append("evidence_coverage must be an object")
    else:
        missing_coverage = sorted(REQUIRED_COVERAGE_FIELDS - coverage.keys())
        if missing_coverage:
            errors.append("evidence_coverage missing fields: " + ", ".join(missing_coverage))
        reviewer = coverage.get("reviewer")
        if "reviewer" in coverage:
            if not isinstance(reviewer, str) or not reviewer:
                errors.append("evidence_coverage.reviewer must be a nonempty string")
            elif sender and reviewer != sender:
                errors.append(
                    "evidence_coverage.reviewer must equal sender; "
                    "coverage is per participant and may not be reported on another participant's behalf"
                )
        for key in ["files_total", "files_opened", "files_parsed", "files_visually_inspected", "files_not_opened"]:
            value = coverage.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"evidence_coverage.{key} must be a nonnegative integer")
        total = coverage.get("files_total")
        opened = coverage.get("files_opened")
        not_opened = coverage.get("files_not_opened")
        if all(isinstance(value, int) and not isinstance(value, bool) for value in [total, opened, not_opened]):
            if opened + not_opened != total:
                errors.append("evidence_coverage files_opened + files_not_opened must equal files_total")

    claims = message.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be an array")
    else:
        seen: set[str] = set()
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append(f"claims[{index}] must be an object")
                continue
            missing_fields = sorted(REQUIRED_CLAIM_FIELDS - claim.keys())
            if missing_fields:
                errors.append(f"claims[{index}] missing required fields: " + ", ".join(missing_fields))
            statement = claim.get("statement")
            if "statement" in claim and (not isinstance(statement, str) or not statement):
                errors.append(f"claims[{index}].statement must be a nonempty string")
            if "reasoning_summary" in claim and not isinstance(claim["reasoning_summary"], str):
                errors.append(f"claims[{index}].reasoning_summary must be a string")
            if "position" in claim and claim["position"] not in CLAIM_POSITIONS:
                errors.append(f"claims[{index}].position must be one of: " + ", ".join(sorted(CLAIM_POSITIONS)))
            if "materiality" in claim and claim["materiality"] not in CLAIM_MATERIALITY:
                errors.append(f"claims[{index}].materiality must be one of: " + ", ".join(sorted(CLAIM_MATERIALITY)))
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
            sources = claim.get("sources")
            if not isinstance(sources, list):
                errors.append(f"claims[{index}].sources must be an array")
            else:
                errors.extend(validate_source_entries(f"claims[{index}].sources", sources))
                if claim.get("position") in AGREEMENT_POSITIONS and not sources:
                    errors.append(
                        f"claims[{index}] position {claim['position']} requires at least one source; "
                        "agreement without primary evidence remains unresolved"
                    )
            counterevidence = claim.get("counterevidence")
            if counterevidence is not None:
                if not isinstance(counterevidence, list):
                    errors.append(f"claims[{index}].counterevidence must be an array")
                else:
                    errors.extend(validate_source_entries(f"claims[{index}].counterevidence", counterevidence))

    open_questions = message.get("open_questions")
    if not isinstance(open_questions, list):
        errors.append("open_questions must be an array")
    else:
        for index, question in enumerate(open_questions):
            if not isinstance(question, dict):
                errors.append(f"open_questions[{index}] must be an object")
                continue
            missing_fields = sorted(REQUIRED_OPEN_QUESTION_FIELDS - question.keys())
            if missing_fields:
                errors.append(f"open_questions[{index}] missing required fields: " + ", ".join(missing_fields))
    if not isinstance(message.get("required_response"), dict):
        errors.append("required_response must be an object")
    return errors
