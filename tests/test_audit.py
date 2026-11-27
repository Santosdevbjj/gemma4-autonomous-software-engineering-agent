import json

import pytest

from gemma4_agent.data.audit import audit_dataset


def test_audit_reports_only_metadata(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        json.dumps(
            {
                "instance_id": "r_1",
                "repo": "owner/r",
                "problem_statement": "secret issue",
                "hints_text": "hint",
                "patch": "SECRET DIFF",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    result = audit_dataset(tasks)
    assert result["task_count"] == 1
    assert result["repository_counts"] == {"owner/r": 1}
    assert "SECRET DIFF" not in json.dumps(result)
    assert "secret issue" not in json.dumps(result)


def test_audit_rejects_duplicate_ids(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    row = {"instance_id": "same", "repo": "owner/r", "problem_statement": "x"}
    tasks.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        audit_dataset(tasks)
def test_audit_rejects_invalid_json_and_missing_id(tmp_path):
    bad_json = tmp_path / "bad.jsonl"
    bad_json.write_text("{not-json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON on line 1"):
        audit_dataset(bad_json)

    missing_id = tmp_path / "missing_id.jsonl"
    missing_id.write_text(json.dumps({"repo": "owner/r"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty instance_id"):
        audit_dataset(missing_id)


def test_audit_inspects_valid_and_malformed_graphs(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        json.dumps({"instance_id": "r_1", "repo": "owner/r", "problem_statement": "x"}) + "\n",
        encoding="utf-8",
    )
    graphs = tmp_path / "graphs"
    graphs.mkdir()
    (graphs / "ok.json").write_text(
        json.dumps({"nodes": ["a", "b"], "edges": [["a", "b"]]}), encoding="utf-8"
    )
    (graphs / "not_dict.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    (graphs / "corrupt.json").write_text("{broken", encoding="utf-8")

    result = audit_dataset(tasks, graphs_dir=graphs)
    assert result["graph_artifacts"] == {
        "directory_provided": True,
        "files": 3,
        "valid_files": 1,
        "malformed_files": 2,
        "nodes_total": 2,
        "edges_total": 1,
    }