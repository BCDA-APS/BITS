#!/usr/bin/env python3
"""
Create a new startup file from a template in demo_instrument.
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def bits_create_startup(name: str) -> None:
    """
    Create a new startup file by copying from demo_instrument.

    :param name: Name for the new startup file.
    :return: None
    """
    # Validate the name
    if re.fullmatch(r"[a-z][_a-z0-9]*", name) is None:
        raise ValueError(f"Invalid name '{name}'. Must be a valid package name.")

    # Get the path to the demo_instrument directory
    demo_instrument_path: Path = (
        Path(__file__).resolve().parent.parent / "demo_instrument"
    ).resolve()

    # Find the startup file in demo_instrument
    # Assuming it's startup.py or similar
    source_file = demo_instrument_path / "startup.py"

    # Create the destination path
    current_path = Path(os.getcwd()).resolve()
    dest_file = current_path / f"{name}_startup.py"

    # Check if destination already exists
    if dest_file.exists():
        raise FileExistsError(f"Destination file '{dest_file}' already exists.")

    # Copy the file
    try:
        shutil.copy2(source_file, dest_file)
        print(f"Created startup file: {dest_file}")
    except Exception as exc:
        raise RuntimeError(f"Error copying startup file: {exc}")


def main() -> None:
    """
    Parse arguments and create the startup file.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Create a startup file from demo_instrument template."
    )
    parser.add_argument(
        "name",
        type=str,
        help="Name for the new startup file; must be a valid package name.",
    )
    args = parser.parse_args()

    try:
        bits_create_startup(args.name)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
