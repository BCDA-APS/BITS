#!/usr/bin/env python3
"""
Delete an instrument and its associated qserver configuration.

This script moves an instrument directory and its corresponding qserver
configuration directory to a .deleted directory in the workspace.
"""

__version__ = "1.0.0"

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


def validate_instrument_name(name: str) -> bool:
    """
    Validate that the instrument name follows the required pattern.

    :param name: The instrument name to validate.
    :return: True if the name is valid, False otherwise.
    """
    return re.fullmatch(r"[a-z][_a-z0-9]*", name) is not None


def get_instrument_paths(name: str) -> Tuple[Path, Path]:
    """
    Get the paths to the instrument and qserver directories.

    :param name: The name of the instrument.
    :return: A tuple containing the instrument directory path and qserver directory
             path.
    """
    main_path: Path = Path(os.getcwd()).resolve()
    instrument_dir: Path = main_path / "src" / name
    qserver_dir: Path = main_path / "src" / f"{name}_qserver"

    return instrument_dir, qserver_dir


def delete_instrument(instrument_dir: Path, qserver_dir: Path) -> None:
    """
    Move the instrument and qserver directories to a .deleted directory.

    :param instrument_dir: Path to the instrument directory.
    :param qserver_dir: Path to the qserver directory.
    :return: None
    """
    main_path: Path = Path(os.getcwd()).resolve()
    deleted_dir: Path = main_path / ".deleted"

    # Create .deleted directory if it doesn't exist
    if not deleted_dir.exists():
        deleted_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created .deleted directory at '{deleted_dir}'.")

    # Add timestamp to avoid name conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if instrument_dir.exists():
        # Create a new path with timestamp
        new_instrument_path = deleted_dir / f"{instrument_dir.name}_{timestamp}"
        shutil.move(str(instrument_dir), str(new_instrument_path))
        print(
            f"Instrument directory '{instrument_dir}' moved to '{new_instrument_path}'."
        )
    else:
        print(f"Warning: Instrument directory '{instrument_dir}' does not exist.")

    if qserver_dir.exists():
        # Create a new path with timestamp
        new_qserver_path = deleted_dir / f"{qserver_dir.name}_{timestamp}"
        shutil.move(str(qserver_dir), str(new_qserver_path))
        print(f"Qserver directory '{qserver_dir}' moved to '{new_qserver_path}'.")
    else:
        print(f"Warning: Qserver directory '{qserver_dir}' does not exist.")


def main() -> None:
    """
    Parse arguments and move the instrument to the .deleted directory.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description=(
            "Move an instrument and its associated qserver configuration to "
            ".deleted directory."
        )
    )
    parser.add_argument("name", type=str, help="Name of the instrument to delete.")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Skip confirmation prompt and delete immediately.",
    )
    args = parser.parse_args()

    if not validate_instrument_name(args.name):
        print(f"Error: Invalid instrument name '{args.name}'.", file=sys.stderr)
        sys.exit(1)

    instrument_dir, qserver_dir = get_instrument_paths(args.name)

    if not instrument_dir.exists() and not qserver_dir.exists():
        msg = (
            f"Error: Neither instrument '{args.name}' nor its qserver "
            f"configuration exist."
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    if not args.force:
        prompt = (
            f"Are you sure you want to move instrument '{args.name}' and its "
            f"qserver configuration to .deleted directory? [y/N]: "
        )
        confirmation = input(prompt)
        if confirmation.lower() != "y":
            print("Operation cancelled.")
            sys.exit(0)

    try:
        delete_instrument(instrument_dir, qserver_dir)
        msg = (
            f"Instrument '{args.name}' and its qserver configuration have been "
            "moved to .deleted directory."
        )
        print(msg)
    except Exception as exc:
        print(f"Error moving instrument: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
