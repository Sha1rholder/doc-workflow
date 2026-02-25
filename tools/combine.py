"""
Combine module - combines files into XML format.
"""

import shutil
from pathlib import Path

from compare import needs_update


def combine_files(
    cleared_folder: str,
    delete_cleared: bool,
    combined_folder: str,
    combined_extension: str,
    combinations: list[dict],
) -> None:
    """
    Combine files into XML format.

    Args:
        cleared_folder: Path to folder with cleared files
        delete_cleared: Whether to delete cleared_folder after execution
        combined_folder: Output directory for combined files
        combined_extension: File extension for combined output files
        combinations: List of combination configurations
    """
    output_dir = Path(combined_folder)
    output_dir.mkdir(exist_ok=True)
    cleared_path = Path(cleared_folder)
    combined_path = Path(combined_folder)

    for combo in combinations:
        base_name = combo["name"]
        urls = combo["filelist"]
        comment = combo.get("comment")

        parts = []
        for url in urls:
            file_path = Path(url)
            content = file_path.read_text(encoding="utf-8")
            try:
                # Use Path.is_relative_to for reliable cross-platform check
                if file_path.is_relative_to(combined_path):
                    content = f'<group path="{url}">{content}</group>'
                elif file_path.is_relative_to(cleared_path):
                    display_path = str(file_path.relative_to(cleared_path))
                    # Always use forward slashes in XML output
                    display_path = "/" + display_path.replace("\\", "/")
                    content = f'<file path="{display_path}" note="HTML comments were removed"><![CDATA[{content.replace("]]>", "]]]]><![CDATA[>")}]]></file>'
                else:
                    content = f'<file path="{url}"><![CDATA[{content.replace("]]>", "]]]]><![CDATA[>")}]]></file>'
            except ValueError:
                # If not relative, treat as regular file
                content = f'<file path="{url}"><![CDATA[{content.replace("]]>", "]]]]><![CDATA[>")}]]></file>'
            parts.append(content)

        final_content = "".join(parts)
        if comment:
            final_content = f"<!--{comment}-->" + final_content

        xml_path = output_dir / f"{base_name}{combined_extension}"

        if needs_update(xml_path, final_content):
            xml_path.write_text(final_content, encoding="utf-8")
            print(f"Updated: {base_name}{combined_extension}")

    if delete_cleared:
        try:
            shutil.rmtree(cleared_folder, ignore_errors=False)
            print(f"Deleted: {cleared_folder}")
        except PermissionError:
            print(f"Permission error! Denied deleting {cleared_folder}.")
        except OSError as e:
            print(f"Failed deleting {cleared_folder}: {e}")
