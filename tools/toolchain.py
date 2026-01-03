import csv
import glob
import os
from datetime import datetime
import tomllib

from clear import clear
from combine import combine
from moonshot import estimate_token


def init_all() -> None:
    for d in ("cleared", "combined"):
        if os.path.exists(d):
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))


def clear_all():
    os.makedirs("cleared", exist_ok=True)
    for md_file in glob.glob("*.md"):
        clear(md_file, f"cleared/{md_file}")


def combine_all(combinations: dict):
    os.makedirs("combined", exist_ok=True)
    for cfg in combinations.values():
        combine(cfg["output"], cfg["inputs"])


def tokens_update(files_tokenizer: list[str]):
    tokens_path = "tokens.csv"
    existing = {}

    if os.path.exists(tokens_path):
        with open(tokens_path, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row:
                    existing[row[0]] = (
                        (row[1], row[2])
                        if len(row) > 2
                        else (
                            row[1] if len(row) > 1 else "0",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )
                    )

    for url in files_tokenizer:
        count = estimate_token(url)
        existing[url] = (str(count), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with open(tokens_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for url, (count, time) in existing.items():
            writer.writerow([url, count, time])


def format_tokens():
    tokens_path = "tokens.csv"
    if not os.path.exists(tokens_path):
        return

    with open(tokens_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    data_rows = [r for r in rows if r and r[0] != "file"]

    root_rows = [r for r in data_rows if not r[0].startswith("combined/")]
    other_rows = [r for r in data_rows if r[0].startswith("combined/")]

    root_rows.sort(key=lambda x: x[0])
    other_rows.sort(key=lambda x: x[0])

    with open(tokens_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "tokens", "time"])
        writer.writerows(root_rows)
        writer.writerows(other_rows)


if __name__ == "__main__":
    with open("settings.toml", "rb") as f:
        settings = tomllib.load(f)
    do_init = settings.get("do_init", False)
    do_clear = settings.get("do_clear", False)
    do_combine = settings.get("do_combine", False)
    do_tokenizer = settings.get("do_tokenizer", False)

    init_all() if do_init else None
    clear_all() if do_clear else None
    combine_all(settings.get("combinations", {})) if do_combine else None
    (
        tokens_update(settings.get("tokenizer", {}).get("files", []))
        if do_tokenizer
        else None
    )
    format_tokens()
