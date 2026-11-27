"""Build a path-safe ZIP archive from a submission directory."""

from __future__ import annotations

import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

_DENIED_PARTS = {".git", ".venv", "__pycache__", "data", "datasets", "checkpoints"}
_DENIED_SUFFIXES = {".pyc", ".pyo", ".log"}
_DENIED_NAMES = {"kaggle.json", "credentials.json"}
_INCLUDE = re.compile(r"^\s*[^#\n]+:\s*!include\s+([^\s#]+)", re.MULTILINE)


def _validate_includes(source: Path) -> None:
    for config in source.rglob("*.yaml"):
        if config.is_symlink():
            raise ValueError(f"Symlinks are not allowed: {config.relative_to(source)}")
        content = config.read_text(encoding="utf-8")
        for include in _INCLUDE.findall(content):
            candidate = (config.parent / include).resolve()
            if not candidate.is_relative_to(source):
                raise ValueError(
                    f"!include escapes submission root: {config.relative_to(source)} -> {include}"
                )
            if not candidate.is_file():
                raise ValueError(
                    f"Missing !include target: {config.relative_to(source)} -> {include}"
                )


def build_archive(source: Path, output: Path) -> None:
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("source must be a directory")
    if not (source / "agent.yaml").is_file():
        raise ValueError("agent.yaml must exist at the submission root")
    _validate_includes(source)

    members = []
    output_resolved = output.resolve()
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in _DENIED_PARTS for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Symlinks are not allowed: {relative}")
        if not path.is_file() or path.resolve() == output_resolved:
            continue
        if (
            path.name in _DENIED_NAMES
            or path.name.startswith(".env")
            or path.suffix.lower() in _DENIED_SUFFIXES
            or path.suffix.lower() in {".pem", ".key"}
        ):
            raise ValueError(f"Sensitive or generated file is not allowed: {relative}")
        archive_name = PurePosixPath(*relative.parts).as_posix()
        if archive_name.startswith("/") or ".." in PurePosixPath(archive_name).parts:
            raise ValueError(f"Unsafe archive path: {archive_name}")
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError(f"Only regular files are allowed: {relative}")
        members.append((path, archive_name))

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
        ) as archive:
            for path, archive_name in members:
                archive.write(path, archive_name)
        with zipfile.ZipFile(temporary) as archive:
            if "agent.yaml" not in archive.namelist():
                raise ValueError("agent.yaml missing from archive root")
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
