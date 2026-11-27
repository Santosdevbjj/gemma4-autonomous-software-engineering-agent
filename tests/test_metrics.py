import json

import pytest

from gemma4_agent.evaluation.metrics import score_predictions


def test_predictions_without_eval_outcomes_do_not_get_invented_score(tmp_path):
    path = tmp_path / "predictions.jsonl"
    path.write_text(json.dumps({"id": "a", "prediction": "NO_PATCH"}) + "\n", encoding="utf-8")
    result = score_predictions(path)
    assert result["pass_rate"] is None
    assert result["no_patch"] == 1


def test_explicit_evaluator_outcomes_are_aggregated(tmp_path):
    path = tmp_path / "predictions.jsonl"
    path.write_text(
        json.dumps({"id": "a", "prediction": "diff", "passed": True})
        + "\n"
        + json.dumps({"id": "b", "prediction": "diff", "passed": False})
        + "\n",
        encoding="utf-8",
    )
    assert score_predictions(path)["pass_rate"] == 0.5


def test_duplicate_prediction_ids_are_rejected(tmp_path):
    path = tmp_path / "predictions.jsonl"
    row = {"id": "a", "prediction": "NO_PATCH"}
    path.write_text(json.dumps(row) + "\n" + json.dumps(row), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        score_predictions(path)
