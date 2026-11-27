from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

from gemma4_agent.cli import main as cli_main
from gemma4_agent.training.train_lora import load_rows


def test_cli_end_to_end_subcommands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        json.dumps(
            {
                "instance_id": "repo_1",
                "repo": "owner/repo",
                "problem_statement": "Fix edge case",
                "patch": "diff --git a/x.py b/x.py\n+pass\n",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    audit_out = tmp_path / "reports" / "eda.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["gemma4-agent", "audit", "--tasks", str(tasks), "--output", str(audit_out)],
    )
    cli_main()
    audit_data = json.loads(audit_out.read_text(encoding="utf-8"))
    assert audit_data["task_count"] == 1

    sft_out = tmp_path / "build" / "sft.jsonl"
    monkeypatch.setattr(
        sys,
        "argv",
        ["gemma4-agent", "prepare-sft", "--tasks", str(tasks), "--output", str(sft_out)],
    )
    cli_main()
    assert "Wrote 1 examples" in capsys.readouterr().out
    assert sft_out.is_file()

    preds = tmp_path / "predictions.jsonl"
    preds.write_text(
        json.dumps({"instance_id": "repo_1", "prediction": "diff", "passed": True}) + "\n",
        encoding="utf-8",
    )
    score_out = tmp_path / "reports" / "score.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["gemma4-agent", "score", "--predictions", str(preds), "--output", str(score_out)],
    )
    cli_main()
    score_data = json.loads(score_out.read_text(encoding="utf-8"))
    assert score_data["pass_rate"] == 1.0

    sub_dir = tmp_path / "submission"
    sub_dir.mkdir()
    (sub_dir / "agent.yaml").write_text("name: cli_agent\n", encoding="utf-8")
    zip_out = tmp_path / "build" / "submission.zip"
    monkeypatch.setattr(
        sys,
        "argv",
        ["gemma4-agent", "package", "--source", str(sub_dir), "--output", str(zip_out)],
    )
    cli_main()
    assert "Created" in capsys.readouterr().out
    with zipfile.ZipFile(zip_out) as archive:
        assert archive.namelist() == ["agent.yaml"]


def test_train_lora_load_rows_validates_schema(tmp_path: Path) -> None:
    valid_path = tmp_path / "train.jsonl"
    valid_path.write_text(
        "\n" + json.dumps({"prompt": "Issue", "completion": "Patch"}) + "\n",
        encoding="utf-8",
    )
    rows = load_rows(valid_path)
    assert rows == [{"prompt": "Issue", "completion": "Patch"}]

    empty_path = tmp_path / "empty.jsonl"
    empty_path.write_text("\n   \n", encoding="utf-8")
    with pytest.raises(ValueError, match="no examples"):
        load_rows(empty_path)

    bad_path = tmp_path / "bad.jsonl"
    bad_path.write_text(json.dumps({"prompt": "Missing completion"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 1"):
        load_rows(bad_path)