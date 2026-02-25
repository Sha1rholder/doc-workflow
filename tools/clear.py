"""
Clear module - removes HTML comments from files.
"""

import re
from pathlib import Path

from compare import needs_update


def clear_comments(cleared_folder: str, remove_comments_list: list[str]) -> None:
    """
    Remove HTML comments from files and save to cleared_folder.

    Args:
        cleared_folder: Output directory for files with comments removed
        remove_comments_list: List of files to process
    """
    output_dir = Path(cleared_folder)
    output_dir.mkdir(exist_ok=True)

    for url in remove_comments_list:
        src_path = Path(url)
        content = src_path.read_text(encoding="utf-8")
        cleared_content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        output_path = output_dir / src_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if needs_update(output_path, cleared_content):
            output_path.write_text(cleared_content, encoding="utf-8")
            print(f"Updated: {output_path}")
