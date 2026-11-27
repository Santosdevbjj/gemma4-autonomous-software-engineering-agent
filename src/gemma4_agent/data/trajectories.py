"""Prepare public issue/reference-patch pairs for supervised fine-tuning."""

from __future__ import annotations

import json
import random
from pathlib import Path

from gemma4_agent.data.audit import _jsonl


def prepare_sft(
    tasks_path: Path, output_path: Path, seed: int = 17, max_examples: int | None = None
) -> int:
    """Write simple public issue->patch pairs; no hidden set or invented reasoning."""
    tasks = list(_jsonl(tasks_path))
    eligible = [task for task in tasks if task.get("problem_statement") and task.get("patch")]
    random.Random(seed).shuffle(eligible)
    if max_examples is not None:
        if max_examples < 1:
            raise ValueError("max_examples must be positive")
        eligible = eligible[:max_examples]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as stream:
        for task in eligible:
            prompt = str(task["problem_statement"]).strip()
            hints = str(task.get("hints_text", "")).strip()
            if hints:
                prompt += "\n\nMaintainer hints:\n" + hints
            row = {
                "instance_id": task.get("instance_id"),
                "prompt": prompt,
                "completion": str(task["patch"]),
                "source": "public_training_patch",
            }
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(eligible)
