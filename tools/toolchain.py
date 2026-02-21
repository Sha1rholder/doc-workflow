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

    if args.init:
        init()

    clear_all()

    with Path("settings.toml").open("rb") as f:
        settings = tomllib.load(f)
    combine_all(settings.get("combinations", {}))

    if args.tokenizer:
        import os

        tokenizer_config = settings.get("tokenizer", {})
        files_tokenizer = tokenizer_config.get("files", [])
        MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
        if MOONSHOT_API_KEY:
            tokens_update(files_tokenizer, MOONSHOT_API_KEY)
        else:
            print("Missing environment variable MOONSHOT_API_KEY")
            return 1
    return 0


def init() -> None:
    import shutil

    """删除 cleared/ 和 combined/ 目录"""
    shutil.rmtree("cleared", ignore_errors=True)
    shutil.rmtree("combined", ignore_errors=True)
    print("Initialized: cleared/ and combined/ directories removed.")


def is_same(file_path: Path, new_content: str) -> bool:
    """
    比较磁盘上的文件内容与新生成的内容是否完全一致。
    如果文件不存在，返回 False
    """
    try:
        return file_path.read_text(encoding="utf-8") == new_content
    except FileNotFoundError:
        return False


def clear_all() -> None:
    output_dir = Path("cleared")
    output_dir.mkdir(exist_ok=True)
    # 遍历当前目录下的所有 .md 文件
    for md_file in Path(".").glob("*.md"):
        # 读取原始文件内容
        content = md_file.read_text(encoding="utf-8")
        # 移除 HTML 注释并添加头部声明
        cleared_content = "<!-- Automatically deleted HTML comments. -->\n\n" + re.sub(
            r"<!--.*?-->", "", content, flags=re.DOTALL
        )
        output_path = output_dir / md_file.name
        # 注意：此处将 Path 对象转换为 str 以匹配你原有的 is_same 签名
        if not is_same(output_path, cleared_content):
            output_path.write_text(cleared_content, encoding="utf-8")
            print(f"Updated: {output_path}")


def combine_all(combinations: dict[str, dict]) -> None:
    output_dir = Path("combined")
    output_dir.mkdir(exist_ok=True)

    for cfg in combinations.values():
        base_name: str = cfg["output"]
        input_urls: list[str] = cfg["inputs"]

        parts = [f'<?xml version="1.0" encoding="UTF-8"?><root id="{base_name}">']

        for url in input_urls:
            content = Path(url).read_text(encoding="utf-8")
            safe_content = content.replace("]]>", "]]]]><![CDATA[>")
            parts.append(f'<file id="{url}"><![CDATA[{safe_content}]]></file>')

        parts.append("</root>")
        final_content = "".join(parts)

        xml_path = output_dir / f"{base_name}.xml"
        txt_path = xml_path.with_suffix(".txt")

        if not is_same(xml_path, final_content):
            xml_path.write_text(final_content, encoding="utf-8")
            txt_path.write_text(final_content, encoding="utf-8")
            print(f"Updated: {base_name}")


def estimate_token(file_path: str, MOONSHOT_API_KEY: str, moonshot_timeout=3) -> int:
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
            "https://api.moonshot.cn/v1/tokenizers/estimate-token-count",
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
            return result
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


def tokens_update(files_tokenizer: list[str], MOONSHOT_API_KEY: str) -> None:
    from datetime import datetime
    import csv

    tokens_path = Path("tokens.csv")

    data = {}
    if tokens_path.exists():
        with tokens_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row["file"]] = {"tokens": row["tokens"], "time": row["time"]}

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for url in files_tokenizer:
        count = estimate_token(url, MOONSHOT_API_KEY)
        data[url] = {"tokens": str(count), "time": now_str}

    sorted_items = sorted(
        data.items(), key=lambda x: (x[0].startswith("combined/"), x[0])
    )
    sorted_data = dict(sorted_items)

    with tokens_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "tokens", "time"])
        for url, info in sorted_data.items():
            writer.writerow([url, info["tokens"], info["time"]])


if __name__ == "__main__":
    sys.exit(main())
