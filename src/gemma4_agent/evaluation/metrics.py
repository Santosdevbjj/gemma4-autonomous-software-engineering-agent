"""Aggregate evaluator outputs without inferring unreported pass/fail results."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from gemma4_agent.data.audit import _jsonl


def score_predictions(path: Path) -> dict[str, Any]:
    rows = list(_jsonl(path))
    ids = [str(row.get("id", row.get("instance_id", ""))) for row in rows]
    if any(not item for item in ids):
        raise ValueError("Each row must include id or instance_id")
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate prediction identifiers")
    patch_count = sum(
        bool(row.get("prediction")) and row.get("prediction") != "NO_PATCH" for row in rows
    )
    explicit = [row for row in rows if isinstance(row.get("passed"), bool)]
    repos = Counter(str(row.get("repo", "unknown")) for row in rows)
    passed = sum(row["passed"] for row in explicit)
    return {
        "rows": len(rows),
        "unique_ids": len(set(ids)),
        "patches_emitted": patch_count,
        "no_patch": len(rows) - patch_count,
        "explicit_pass_fail_rows": len(explicit),
        "pass_rate": (passed / len(explicit)) if explicit else None,
        "repository_counts": dict(sorted(repos.items())),
        "note": "A null pass_rate means predictions alone do not contain evaluator outcomes.",
    }
