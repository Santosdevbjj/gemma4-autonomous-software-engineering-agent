"""Metadata-only audit utilities; never emit reference patches or issue text."""

from __future__ import annotations

import json
import re
import statistics
import struct
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


def _jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc


def audit_dataset(
    tasks_path: Path, graphs_dir: Path | None = None, embeddings_dir: Path | None = None
) -> dict[str, Any]:
    """Summarize public task and artifact metadata without copying sensitive content."""
    tasks = list(_jsonl(tasks_path))
    ids = [str(task.get("instance_id", "")) for task in tasks]
    if any(not item for item in ids):
        raise ValueError("Every task must have a non-empty instance_id")
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate instance_id values found")

    repos = Counter(str(task.get("repo", "unknown")) for task in tasks)
    statement_lengths = [len(str(task.get("problem_statement", ""))) for task in tasks]
    hint_count = sum(bool(str(task.get("hints_text", "")).strip()) for task in tasks)
    patch_count = sum(bool(task.get("patch")) for task in tasks)

    result: dict[str, Any] = {
        "task_count": len(tasks),
        "repository_counts": dict(sorted(repos.items())),
        "problem_statement_chars": _summary(statement_lengths),
        "tasks_with_hints": hint_count,
        "tasks_with_public_reference_patch": patch_count,
        "graph_artifacts": _inspect_graphs(graphs_dir),
        "embedding_artifacts": _inspect_embeddings(embeddings_dir),
        "privacy_note": (
            "Metadata only; issue text, patches and tests "
            "were not copied into this report."
        ),
    }
    return result


def _summary(values: list[int]) -> dict[str, float | int | None]:
    if not values:
        return {"min": None, "median": None, "mean": None, "max": None}
    return {
        "min": min(values),
        "median": statistics.median(values),
        "mean": round(statistics.mean(values), 2),
        "max": max(values),
    }


def _inspect_graphs(directory: Path | None) -> dict[str, Any]:
    if directory is None:
        return {"directory_provided": False}
    paths = sorted(directory.glob("*.json"))
    parsed = nodes = edges = malformed = 0
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Graph JSON root must be an object")
            nodes += len(data.get("nodes", []))
            edges += len(data.get("edges", []))
            parsed += 1
        except (OSError, json.JSONDecodeError, ValueError, AttributeError, TypeError):
            malformed += 1
    return {
        "directory_provided": True,
        "files": len(paths),
        "valid_files": parsed,
        "malformed_files": malformed,
        "nodes_total": nodes,
        "edges_total": edges,
    }


def _inspect_embeddings(directory: Path | None) -> dict[str, Any]:
    if directory is None:
        return {"directory_provided": False}
    paths = sorted(directory.glob("*.npz"))
    arrays = Counter()
    shapes = Counter()
    malformed = 0
    for path in paths:
        try:
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    if not name.endswith(".npy"):
                        continue
                    arrays[name] += 1
                    with archive.open(name) as stream:
                        if stream.read(6) != b"\x93NUMPY":
                            raise ValueError("Invalid NPY magic")
                        major, minor = stream.read(2)
                        if major == 1:
                            header_length = struct.unpack("<H", stream.read(2))[0]
                        elif major in (2, 3):
                            header_length = struct.unpack("<I", stream.read(4))[0]
                        else:
                            raise ValueError(f"Unsupported NPY version {major}.{minor}")
                        header = stream.read(header_length).decode("latin1")
                        match = re.search(r"['\"]shape['\"]\s*:\s*\(([^)]*)\)", header)
                        if not match:
                            raise ValueError("NPY shape missing")
                        dims = tuple(
                            int(value.strip())
                            for value in match.group(1).split(",")
                            if value.strip()
                        )
                        shapes[str(dims)] += 1
        except (OSError, zipfile.BadZipFile, ValueError, struct.error, UnicodeDecodeError):
            malformed += 1
    return {
        "directory_provided": True,
        "files": len(paths),
        "malformed_files": malformed,
        "array_entries": sum(arrays.values()),
        "shape_counts": dict(sorted(shapes.items())),
        "numpy_required": False,
    }