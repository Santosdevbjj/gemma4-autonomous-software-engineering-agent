import zipfile

import pytest

from gemma4_agent.packaging.archive import build_archive


def test_archive_has_agent_at_root_and_safe_relative_paths(tmp_path):
    source = tmp_path / "submission"
    source.mkdir()
    (source / "agent.yaml").write_text("name: example\n", encoding="utf-8")
    (source / "prompts").mkdir()
    (source / "prompts" / "system.md").write_text("instructions\n", encoding="utf-8")
    target = tmp_path / "out" / "submission.zip"
    build_archive(source, target)
    with zipfile.ZipFile(target) as archive:
        assert "agent.yaml" in archive.namelist()
        assert "prompts/system.md" in archive.namelist()
        assert all(".." not in name.split("/") for name in archive.namelist())


def test_archive_requires_root_agent(tmp_path):
    source = tmp_path / "submission"
    source.mkdir()
    with pytest.raises(ValueError, match="agent.yaml"):
        build_archive(source, tmp_path / "submission.zip")


def test_archive_rejects_credentials(tmp_path):
    source = tmp_path / "submission"
    source.mkdir()
    (source / "agent.yaml").write_text("name: example\n", encoding="utf-8")
    (source / ".env").write_text("SECRET=value", encoding="utf-8")
    with pytest.raises(ValueError, match="Sensitive"):
        build_archive(source, tmp_path / "submission.zip")


def test_archive_rejects_include_outside_root(tmp_path):
    source = tmp_path / "submission"
    source.mkdir()
    (source / "agent.yaml").write_text("instruction: !include ../outside.md\n", encoding="utf-8")
    (tmp_path / "outside.md").write_text("no", encoding="utf-8")
    with pytest.raises(ValueError, match="escapes"):
        build_archive(source, tmp_path / "submission.zip")


def test_archive_rejects_missing_include(tmp_path):
    source = tmp_path / "submission"
    source.mkdir()
    (source / "agent.yaml").write_text(
        "instruction: !include prompts/missing.md\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Missing !include"):
        build_archive(source, tmp_path / "submission.zip")
def test_archive_skips_denied_directories_and_rejects_denied_suffixes(tmp_path):
    source = tmp_path / "submission"
    source.mkdir()
    (source / "agent.yaml").write_text("name: example\n", encoding="utf-8")
    (source / "__pycache__").mkdir()
    (source / "__pycache__" / "cached.pyc").write_bytes(b"0000")
    (source / "data").mkdir()
    (source / "data" / "secret.jsonl").write_text("{}", encoding="utf-8")

    target = tmp_path / "out" / "submission.zip"
    build_archive(source, target)
    with zipfile.ZipFile(target) as archive:
        assert archive.namelist() == ["agent.yaml"]

    (source / "private.key").write_text("PRIVATE KEY", encoding="utf-8")
    with pytest.raises(ValueError, match="Sensitive"):
        build_archive(source, target)