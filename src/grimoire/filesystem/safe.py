"""Safe directory promotion for generated Grimoire packs."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path


class SafeOutputError(RuntimeError):
    """Controlled filesystem failure without echoing untrusted paths."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def _existing_ancestors(path: Path) -> tuple[Path, ...]:
    ancestors = []
    current = path
    while True:
        if current.exists() or current.is_symlink():
            ancestors.append(current)
        if current.parent == current:
            break
        current = current.parent
    return tuple(reversed(ancestors))


def _reject_symlink_path(path: Path) -> None:
    for component in _existing_ancestors(path):
        if component.is_symlink():
            raise SafeOutputError(
                "symlink_path_rejected",
                "output path contains a symlink component",
            )


def resolve_child(root: Path, child: str | Path) -> Path:
    """Resolve a child path and require it to remain inside root."""

    root_path = root.expanduser().resolve()
    candidate = (root_path / child).resolve()
    if candidate != root_path and root_path not in candidate.parents:
        raise SafeOutputError(
            "path_escape_rejected",
            "path escapes the declared output root",
        )
    _reject_symlink_path(candidate)
    return candidate


def _file_set(directory: Path) -> set[str]:
    return {
        str(path.relative_to(directory))
        for path in directory.rglob("*")
        if path.is_file()
    }


def _validate_expected_files(directory: Path, expected_files: Iterable[str]) -> None:
    expected = set(expected_files)
    actual = _file_set(directory)
    if actual != expected:
        raise SafeOutputError(
            "unexpected_file_set",
            "generated output files do not match the declared file set",
        )


def atomic_write_directory(
    output: Path,
    expected_files: Iterable[str],
    builder: Callable[[Path], object],
) -> None:
    """Build a directory in temporary storage and promote it as one pack."""

    requested_output = output.expanduser()
    if requested_output.is_symlink():
        raise SafeOutputError(
            "symlink_path_rejected",
            "output path contains a symlink component",
        )
    output_path = requested_output.resolve()
    _reject_symlink_path(output_path)
    parent = output_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink_path(parent)
    if output_path.exists() and not output_path.is_dir():
        raise SafeOutputError(
            "non_directory_output_rejected",
            "output path must be a directory",
        )

    temp_root = Path(
        tempfile.mkdtemp(prefix=f".grimoire-build-{output_path.name}-", dir=parent)
    )
    backup: Path | None = None
    try:
        builder(temp_root)
        _reject_symlink_path(temp_root)
        _validate_expected_files(temp_root, expected_files)
        backup = parent / f".grimoire-backup-{output_path.name}"
        if backup.exists():
            shutil.rmtree(backup)
        if output_path.exists():
            output_path.rename(backup)
        temp_root.rename(output_path)
        if backup and backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if temp_root.exists():
            shutil.rmtree(temp_root)
        if backup and backup.exists() and not output_path.exists():
            backup.rename(output_path)
        raise
