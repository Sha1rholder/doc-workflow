"""
Init module - clears output folders and tokens.csv.
"""

import os
import shutil


def init_outputs(cleared_folder: str, combined_folder: str, tokens_csv: str) -> None:
    """
    Initialize by clearing output folders and tokens.csv file.

    Args:
        cleared_folder: Path to cleared folder to delete
        combined_folder: Path to combined folder to delete
        tokens_csv: Path to tokens CSV file to delete
    """
    shutil.rmtree(cleared_folder, ignore_errors=True)
    shutil.rmtree(combined_folder, ignore_errors=True)
    if os.path.exists(tokens_csv):
        os.remove(tokens_csv)

    print("Initialized:")
    print(f"  - Cleared: {cleared_folder}")
    print(f"  - Cleared: {combined_folder}")
    print(f"  - Removed: {tokens_csv}")
