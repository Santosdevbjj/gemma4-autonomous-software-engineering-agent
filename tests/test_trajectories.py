import json

import pytest

from gemma4_agent.data.trajectories import prepare_sft


def test_prepare_sft_writes_only_prompt_and_reference_patch(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        json.dumps(
            {
                "instance_id": "r_1",
                "problem_statement": "fix it",
                "patch": "diff",
                "test_patch": "tests",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "build" / "sft.jsonl"
    assert prepare_sft(tasks, output) == 1
    row = json.loads(output.read_text(encoding="utf-8"))
    assert row["prompt"] == "fix it"
    assert row["completion"] == "diff"
    assert "test_patch" not in row


def test_prepare_sft_filters_ineligible_includes_hints_and_caps_examples(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    rows = [
        {
            "instance_id": "r_1",
            "problem_statement": "Bug one",
            "hints_text": "Check parser",
            "patch": "diff 1",
        },
        {
            "instance_id": "r_2",
            "problem_statement": "Bug two without patch",
            "patch": "",
        },
        {
            "instance_id": "r_3",
            "problem_statement": "Bug three",
            "patch": "diff 3",
        },
    ]
    tasks.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    output = tmp_path / "out" / "sft.jsonl"
    written = prepare_sft(tasks, output, seed=42, max_examples=1)
    assert written == 1

    lines = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 1
    assert lines[0]["instance_id"] in {"r_1", "r_3"}
    if lines[0]["instance_id"] == "r_1":
        assert "Maintainer hints:\nCheck parser" in lines[0]["prompt"]

    with pytest.raises(ValueError, match="max_examples"):
        prepare_sft(tasks, output, max_examples=0)