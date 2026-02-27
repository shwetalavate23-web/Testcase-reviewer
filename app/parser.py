"""Parse Zephyr export files into normalized test case records."""

from __future__ import annotations

import csv
import io
import json
from typing import Any


EXPECTED_COLUMNS = {
    "title": ["title", "summary", "test case name", "name"],
    "steps": ["steps", "test steps"],
    "expected": ["expected result", "expected", "result"],
    "test_type": ["test type", "type"],
    "preconditions": ["preconditions", "pre-condition"],
    "labels": ["labels", "tags"],
}


def _lookup(row: dict[str, Any], aliases: list[str]) -> str:
    lower_map = {k.lower().strip(): v for k, v in row.items()}
    for alias in aliases:
        if alias in lower_map:
            return str(lower_map[alias] or "").strip()
    return ""


def parse_zephyr_upload(raw_bytes: bytes, filename: str) -> list[dict[str, str]]:
    if filename.lower().endswith(".json"):
        payload = json.loads(raw_bytes.decode("utf-8"))
        cases = payload if isinstance(payload, list) else payload.get("testCases", [])
        return [
            {
                "title": str(case.get("title") or case.get("name") or "").strip(),
                "steps": str(case.get("steps") or "").strip(),
                "expected": str(case.get("expectedResult") or case.get("expected") or "").strip(),
                "test_type": str(case.get("testType") or "").strip(),
                "preconditions": str(case.get("preconditions") or "").strip(),
                "labels": ", ".join(case.get("labels", [])) if isinstance(case.get("labels"), list) else str(case.get("labels") or "").strip(),
            }
            for case in cases
        ]

    text = raw_bytes.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    records: list[dict[str, str]] = []
    for row in reader:
        records.append(
            {
                field: _lookup(row, aliases)
                for field, aliases in EXPECTED_COLUMNS.items()
            }
        )
    return records
