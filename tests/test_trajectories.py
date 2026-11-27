import json

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
