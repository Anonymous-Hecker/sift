
import shutil
from pathlib import Path

from . import config


class FsOpError(Exception):
    """Raised when a file operation is refused or fails."""


def is_protected(path):
    """True if the path is inside a Windows system folder."""
    parts = Path(path).resolve().parts
    return len(parts) > 1 and parts[1].lower() in config.PROTECTED_TOP_LEVEL


def check_move(source, dest):
    """Return a description of the problem, or None if the move looks safe."""
    source = Path(source)
    dest = Path(dest)

    if is_protected(source) or is_protected(dest):
        return "Path is inside a protected system folder"
    if not source.exists():
        return f"Source does not exist: {source}"
    if dest.exists():
        return f"Destination already exists (refusing to overwrite): {dest}"
    return None


def safe_move(source, dest):
    """Move a file, but only if every safety check passes."""
    problem = check_move(source, dest)
    if problem:
        raise FsOpError(problem)

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(source), str(dest))
    except OSError as error:
        raise FsOpError(f"Move failed: {error}") from error



