import os
import sys
import argparse
import re
from pathlib import Path
import tomllib


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Toolchain")
    parser.add_argument("--init", action="store_true", help="Run initialization")
    parser.add_argument("--tokenizer", action="store_true", help="Run tokenizer update")
    args = parser.parse_args()

    with Path("settings.toml").open("rb") as f:
        settings = tomllib.load(f)
    derived_folder, tokens_csv, remove_comments, combinations, tokenizer = (
        settings["derived_folder"],
        settings["tokens_csv"],
        settings["remove_comments"],
        settings["combinations"],
        settings["tokenizer"],
    )

    if args.init:
        import shutil

        shutil.rmtree(derived_folder, ignore_errors=True)
        if os.path.exists(tokens_csv):
            os.remove(tokens_csv)

    remove_all(derived_folder, remove_comments)
    combine_all(derived_folder, combinations)

    if args.tokenizer:
        try:
            MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
        except:
            print("Fail to read environment variable MOONSHOT_API_KEY.")
            return 1
        if MOONSHOT_API_KEY:
            tokens_update(
                derived_folder,
                tokens_csv,
                tokenizer["endpoint"],
                tokenizer["files"],
                MOONSHOT_API_KEY,
            )
        else:
            print("Missing environment variable MOONSHOT_API_KEY")
            return 1
    return 0


def is_same(file_path: Path, new_content: str) -> bool:
    try:
        return file_path.read_text(encoding="utf-8") == new_content
    except FileNotFoundError:
        return False


def remove_all(derived_folder: str, remove_comments: list[str]) -> None:
    output_dir = Path(derived_folder)
    output_dir.mkdir(exist_ok=True)

    for url in remove_comments:
        content = Path(url).read_text(encoding="utf-8")
        path_obj = Path(url)
        filename_without_ext = path_obj.with_suffix("")
        output_filename = (
            str(filename_without_ext).replace("/", "__").replace("\\", "__")
            + ".comments_removed.md"
        )
        output_path = output_dir / output_filename
        cleared_content = "<!-- HTML comments removed. -->\n" + re.sub(
            r"<!--.*?-->", "", content, flags=re.DOTALL
        )

        if not is_same(output_path, cleared_content):
            output_path.write_text(cleared_content, encoding="utf-8")
            print(f"Updated: {output_path}")


def combine_all(derived_folder: str, combinations: list[dict]) -> None:
    output_dir = Path(derived_folder)
    output_dir.mkdir(exist_ok=True)
    derived_path = Path(derived_folder)

    for combo in combinations:
        base_name = combo["name"]
        urls = combo["filelist"]
        comment = combo.get("comment")

        parts = []
        for url in urls:
            content = Path(url).read_text(encoding="utf-8")
            if url.endswith(".xml.txt"):
                content = f'<group path="{url}">{content}</group>'
            else:
                display_path = url
                url_path = Path(url)
                if url.endswith(".comments_removed.md"):
                    relative_path = url_path.relative_to(derived_path)
                    # Convert to string and process
                    display_path = (
                        str(relative_path).replace("__", "/").replace("\\", "/")
                    )

                content = f'<file path="{display_path}"><![CDATA[{content.replace("]]>", "]]]]><![CDATA[>")}]]></file>'
            parts.append(content)

        final_content = "".join(parts)
        if comment:
            final_content = f"<!--{comment}-->" + final_content

        xml_path = output_dir / f"{base_name}.xml.txt"

        if not is_same(xml_path, final_content):
            xml_path.write_text(final_content, encoding="utf-8")
            print(f"Updated: {base_name}.xml.txt")


def estimate_token_add1(
    tokenizer_endpoint: str, file_path: str, MOONSHOT_API_KEY: str, moonshot_timeout=3
) -> int:
    import json
    import urllib.request
    import urllib.error
    import socket

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    data = {
        "model": "kimi-k2.5",
        "messages": [{"role": "user", "content": content}],
    }

    try:
        req = urllib.request.Request(
            tokenizer_endpoint,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MOONSHOT_API_KEY}",
            },
        )
        with urllib.request.urlopen(req, timeout=moonshot_timeout) as response:
            result = (
                json.loads(response.read().decode("utf-8"))
                .get("data", {})
                .get("total_tokens", 0)
            )
            print(file_path, "tokens:", result)
            return result + 1
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e}")
        return 0
    except urllib.error.URLError as e:
        print(f"URLError: {e}")
        return 0
    except socket.timeout as e:
        print(f"socket.timeout: {e}")
        return 0
    except ConnectionError as e:
        print(f"ConnectionError: {e}")
        return 0
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return 0
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        return 0
    except OSError as e:
        print(f"OSError: {e}")
        return 0
    except Exception as e:
        print(f"Exception: {e}")
        return 0


def tokens_update(
    derived_folder: str,
    tokens_csv: str,
    tokenizer_endpoint: str,
    tokenizer_files: list[str],
    MOONSHOT_API_KEY: str,
) -> int:
    from datetime import datetime
    import csv

    tokens_path = Path(tokens_csv)

    data = {}
    if tokens_path.exists():
        with tokens_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row["file"]] = {"tokens": row["tokens"], "time": row["time"]}

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for url in tokenizer_files:
        count_add1 = estimate_token_add1(tokenizer_endpoint, url, MOONSHOT_API_KEY)
        if count_add1:
            data[url] = {"tokens": str(count_add1 - 1), "time": now_str}
        else:
            return 1

    sorted_items = sorted(
        data.items(), key=lambda x: (Path(x[0]).is_relative_to(derived_folder), x[0])
    )
    sorted_data = dict(sorted_items)

    with tokens_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "tokens", "time"])
        for url, info in sorted_data.items():
            writer.writerow([url, info["tokens"], info["time"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
