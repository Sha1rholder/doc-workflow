"""
Check if file needs to be updated.
"""

from pathlib import Path


def needs_update(file_path: Path, new_content: str) -> bool:
    """Returns True if file doesn't exist or content differs."""
    return not (
        file_path.is_file() and file_path.read_text(encoding="utf-8") == new_content
    )
