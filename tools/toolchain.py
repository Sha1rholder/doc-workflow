# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "typer>=0.15.0",
# ]
# ///
"""
Project toolchain - main entry point.
Only this file reads settings.toml and coordinates other modules.
"""

import os
import tomllib
from pathlib import Path
from typing import Annotated
import typer

from init import init_outputs
from clear import clear_comments
from combine import combine_files


app = typer.Typer(
    name="toolchain",
    help="Project toolchain for cleaning HTML comments and combining files",
    no_args_is_help=True,
)


def load_settings(
    config_path: Path,
) -> tuple[
    str,
    bool,
    str,
    str,
    str,
    list[str],
    list[dict],
    dict,
]:
    """
    Load settings from config file.

    Returns (cleared_folder, delete_cleared, combined_folder, combined_extension,
             tokens_csv, remove_comments, combinations, tokenizer_config)
    """
    with Path(config_path).open("rb") as f:
        settings = tomllib.load(f)
    return (
        settings["cleared_folder"],
        settings["delete_cleared"],
        settings["combined_folder"],
        settings["combined_extension"],
        settings["tokens_csv"],
        settings["remove_comments"],
        settings["combinations"],
        settings["tokenizer"],
    )


@app.callback(invoke_without_command=True)
def main(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="Path to config file",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
    init: Annotated[
        bool,
        typer.Option(
            "--init",
            help="Initialize by clearing output folders and tokens.csv first",
        ),
    ] = False,
    clear: Annotated[
        bool,
        typer.Option(
            "--clear",
            help="Remove HTML comments from files",
        ),
    ] = False,
    combine: Annotated[
        bool,
        typer.Option(
            "--combine",
            help="Combine files into XML",
        ),
    ] = False,
    tokenizer: Annotated[
        bool,
        typer.Option(
            "--tokenizer",
            help="Run tokenizer to calculate token counts (requires MOONSHOT_API_KEY)",
        ),
    ] = False,
) -> None:
    """
    Run the workflow with specified steps.
    At least one step (--init, --clear, --combine, --tokenizer) must be specified.
    """
    if not (init or clear or combine or tokenizer):
        print(
            "Error: At least one of --init, --clear, --combine, --tokenizer must be specified"
        )
        raise typer.Exit(1)

    (
        cleared_folder,
        delete_cleared,
        combined_folder,
        combined_extension,
        tokens_csv,
        remove_comments,
        combinations,
        tokenizer_config,
    ) = load_settings(config)

    if init:
        init_outputs(cleared_folder, combined_folder, tokens_csv)

    if clear:
        print("Removing HTML comments...")
        clear_comments(cleared_folder, remove_comments)

    if combine:
        print("Combining files...")
        combine_files(
            cleared_folder,
            delete_cleared,
            combined_folder,
            combined_extension,
            combinations,
        )

    if tokenizer:
        try:
            MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
        except Exception:
            print("Failed to read environment variable MOONSHOT_API_KEY.")
            raise typer.Exit(1)

        if MOONSHOT_API_KEY:
            from tokenizer import bulk_tokenizer, write_tokens, read_existing_tokens

            print("Updating token counts...")
            existing_data = read_existing_tokens(tokens_csv)
            data, success = bulk_tokenizer(
                tokenizer_config["endpoint"],
                tokenizer_config["files"],
                MOONSHOT_API_KEY,
                existing_data,
            )

            if not success:
                raise typer.Exit(1)

            write_tokens(tokens_csv, data)
            print("Token counts updated successfully!")
        else:
            print("Missing environment variable MOONSHOT_API_KEY")
            raise typer.Exit(1)

    print("Workflow completed successfully!")


if __name__ == "__main__":
    app()
