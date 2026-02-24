import os
import sys
import argparse
import re
from pathlib import Path
import tomllib
import shutil


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Toolchain")
    parser.add_argument("--init", action="store_true", help="Run initialization")
    parser.add_argument("--tokenizer", action="store_true", help="Run tokenizer update")
    args = parser.parse_args()

    with Path("settings.toml").open("rb") as f:
        settings = tomllib.load(f)
    (
        cleared_folder,
        delete_cleared,
        combined_folder,
        combined_extension,
        tokens_csv,
        remove_comments,
        combinations,
        tokenizer,
    ) = (
        settings["cleared_folder"],
        settings["delete_cleared"],
        settings["combined_folder"],
        settings["combined_extension"],
        settings["tokens_csv"],
        settings["remove_comments"],
        settings["combinations"],
        settings["tokenizer"],
    )

    if args.init:
        shutil.rmtree(cleared_folder, ignore_errors=True)
        shutil.rmtree(combined_folder, ignore_errors=True)
        if os.path.exists(tokens_csv):
            os.remove(tokens_csv)

    remove_all(cleared_folder, remove_comments)
    combine_all(
        cleared_folder,
        delete_cleared,
        combined_folder,
        combined_extension,
        combinations,
    )

    if args.tokenizer:
        try:
            MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
        except:
            print("Fail to read environment variable MOONSHOT_API_KEY.")
            return 1
        if MOONSHOT_API_KEY:
            tokens_update(
                tokens_csv,
                tokenizer["endpoint"],
                tokenizer["files"],
                MOONSHOT_API_KEY,
            )
        else:
            print("Missing environment variable MOONSHOT_API_KEY")
            return 1
    return 0


def needs_update(file_path: Path, new_content: str) -> bool:
    return not (
        file_path.is_file() and file_path.read_text(encoding="utf-8") == new_content
    )


def remove_all(cleared_folder: str, remove_comments: list[str]) -> None:
    output_dir = Path(cleared_folder)
    output_dir.mkdir(exist_ok=True)

    for url in remove_comments:
        src_path = Path(url)
        content = src_path.read_text(encoding="utf-8")
        cleared_content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        output_path = output_dir / src_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if needs_update(output_path, cleared_content):
            output_path.write_text(cleared_content, encoding="utf-8")
            print(f"Updated: {output_path}")


def combine_all(
    cleared_folder: str,
    delete_cleared: bool,
    combined_folder: str,
    combined_extension: str,
    combinations: list[dict],
) -> None:
    output_dir = Path(combined_folder)
    output_dir.mkdir(exist_ok=True)

    for combo in combinations:
        base_name = combo["name"]
        urls = combo["filelist"]
        comment = combo.get("comment")

        parts = []
        for url in urls:
            content = Path(url).read_text(encoding="utf-8")
            if url.startswith(combined_folder):
                content = f'<group path="{url}">{content}</group>'
            elif url.startswith(cleared_folder):
                display_path = url[len(cleared_folder) :]
                content = f'<file path="{display_path}" note="HTML comments were removed"><![CDATA[{content.replace("]]>", "]]]]><![CDATA[>")}]]></file>'
            else:
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
        shutil.rmtree(cleared_folder, ignore_errors=True)
        print(f"Deleted: {cleared_folder}")


def tokens_update(
    tokens_csv: str,
    tokenizer_endpoint: str,
    tokenizer_files: list[str],
    MOONSHOT_API_KEY: str,
) -> int:
    from datetime import datetime
    import csv
    from tokenizer import tokenizer_add1

    tokens_path = Path(tokens_csv)

    data = {}
    if tokens_path.exists():
        with tokens_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row["file"]] = {"tokens": row["tokens"], "time": row["time"]}

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for url in tokenizer_files:
        count_add1 = tokenizer_add1(tokenizer_endpoint, url, MOONSHOT_API_KEY)
        if count_add1:
            data[url] = {"tokens": str(count_add1 - 1), "time": now_str}
        else:
            return 1

    sorted_data = dict(sorted(data.items()))

    with tokens_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "tokens", "time"])
        for url, info in sorted_data.items():
            writer.writerow([url, info["tokens"], info["time"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
