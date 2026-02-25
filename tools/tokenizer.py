# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "typer>=0.15.0",
# ]
# ///
import csv
import json
import os
import socket
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional
import typer


app = typer.Typer(
    name="tokenizer",
    help="Moonshot tokenizer tool for calculating token counts in files",
    no_args_is_help=True,
)


@app.command(name="tokenize")
def tokenize_command(
    tokens_csv_path: Annotated[
        Path,
        typer.Argument(
            help="Path to tokens CSV file",
        ),
    ],
    endpoint: Annotated[
        str,
        typer.Argument(
            help="Moonshot API endpoint URL",
        ),
    ],
    files: Annotated[
        list[str],
        typer.Argument(
            help="List of files to tokenize",
        ),
    ],
    api_key: Annotated[
        Optional[str],
        typer.Option(
            "--api-key",
            "-k",
            help="Moonshot API key (defaults to MOONSHOT_API_KEY environment variable)",
        ),
    ] = None,
) -> None:
    """
    Run bulk tokenizer with explicit parameters.
    Requires MOONSHOT_API_KEY environment variable to be set if --api-key not provided.
    """
    if api_key is None:
        try:
            api_key = os.getenv("MOONSHOT_API_KEY")
        except Exception:
            print("Failed to read environment variable MOONSHOT_API_KEY.")
            raise typer.Exit(1)

    if not api_key:
        print("Missing environment variable MOONSHOT_API_KEY or --api-key not provided")
        raise typer.Exit(1)

    existing_data = read_existing_tokens(str(tokens_csv_path))
    data, success = bulk_tokenizer(
        endpoint,
        files,
        api_key,
        existing_data,
    )

    if not success:
        raise typer.Exit(1)

    write_tokens(str(tokens_csv_path), data)
    print("Token counts updated successfully!")


@app.command(name="tokenize-file")
def tokenize_file_command(
    file_path: Annotated[
        Path,
        typer.Argument(
            help="Path to the file to tokenize",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
    endpoint: Annotated[
        str,
        typer.Option(
            "--endpoint",
            "-e",
            help="Moonshot API endpoint URL",
        ),
    ] = "https://api.moonshot.cn/v1/tokenizers/estimate-token-count",
    api_key: Annotated[
        Optional[str],
        typer.Option(
            "--api-key",
            "-k",
            help="Moonshot API key (defaults to MOONSHOT_API_KEY environment variable)",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="Request timeout in seconds",
        ),
    ] = 3,
) -> None:
    """
    Tokenize a single file and display the token count.
    """
    if api_key is None:
        api_key = os.getenv("MOONSHOT_API_KEY")

    if not api_key:
        print(
            "Error: MOONSHOT_API_KEY environment variable not set and --api-key not provided"
        )
        raise typer.Exit(1)

    tokens = tokenizer_add1(endpoint, str(file_path), api_key, timeout)
    if tokens:
        print(f"{file_path}: {tokens - 1} tokens")
    else:
        print("Failed to tokenize file")
        raise typer.Exit(1)


@app.command(name="read-tokens")
def read_tokens_command(
    tokens_csv: Annotated[
        Path,
        typer.Argument(
            help="Path to tokens CSV file",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
) -> None:
    """
    Read and display token counts from CSV file in a formatted table.
    """
    data = read_existing_tokens(str(tokens_csv))

    if not data:
        print("No token data found")
        return

    print("Token Counts")
    print("-" * 80)
    print(f"{'File':<50} {'Tokens':>15} {'Last Updated':>20}")
    print("-" * 80)
    for file_path, info in sorted(data.items()):
        print(f"{file_path:<50} {info['tokens']:>15} {info['time']:>20}")
    print("-" * 80)


@app.command(name="write-tokens")
def write_tokens_command(
    tokens_csv: Annotated[
        Path,
        typer.Argument(
            help="Path to tokens CSV file to write",
        ),
    ],
    file_token_pairs: Annotated[
        list[str],
        typer.Argument(
            help="File and token pairs in format 'file:tokens'",
        ),
    ],
) -> None:
    """
    Write token counts to CSV file.
    Usage: write-tokens tokens.csv file1.md:100 file2.md:200
    """
    data: dict = {}
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for pair in file_token_pairs:
        if ":" not in pair:
            print(f"Invalid format: {pair}. Expected 'file:tokens'")
            raise typer.Exit(1)
        file_path, tokens = pair.split(":", 1)
        data[file_path] = {"tokens": tokens, "time": now_str}

    write_tokens(str(tokens_csv), data)
    print(f"Wrote {len(data)} entries to {tokens_csv}")


def tokenizer_add1(
    tokenizer_endpoint: str,
    file_path: str,
    MOONSHOT_API_KEY: str,
    moonshot_timeout: int = 3,
) -> int:
    """
    Calculate token count for a single file, returns count + 1.
    Returns 0 on failure.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        data = {
            "model": "kimi-k2.5",
            "messages": [{"role": "user", "content": content}],
        }

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


def bulk_tokenizer(
    tokenizer_endpoint: str,
    tokenizer_files: list[str],
    MOONSHOT_API_KEY: str,
    existing_data: dict | None = None,
) -> tuple[dict, bool]:
    """
    Bulk calculate token counts for multiple files.
    Returns (new_data_dict, success_flag).
    """
    if existing_data is None:
        existing_data = {}

    data = existing_data.copy()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for url in tokenizer_files:
        count_add1 = tokenizer_add1(tokenizer_endpoint, url, MOONSHOT_API_KEY)
        if count_add1:
            data[url] = {"tokens": str(count_add1 - 1), "time": now_str}
        else:
            return {}, False

    return data, True


def write_tokens(tokens_csv: str, data: dict) -> None:
    """
    Write token data to CSV file.
    """
    tokens_path = Path(tokens_csv)
    sorted_data = dict(sorted(data.items()))

    with tokens_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "tokens", "time"])
        for url, info in sorted_data.items():
            writer.writerow([url, info["tokens"], info["time"]])


def read_existing_tokens(tokens_csv: str) -> dict:
    """
    Read existing token data from CSV file.
    Returns empty dict if file doesn't exist.
    """
    tokens_path = Path(tokens_csv)
    data = {}

    if tokens_path.exists():
        with tokens_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row["file"]] = {"tokens": row["tokens"], "time": row["time"]}

    return data


if __name__ == "__main__":
    app()
