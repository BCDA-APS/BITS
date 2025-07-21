#!/usr/bin/env python3
"""
Create a new instrument from a fixed template.

Copies the template directory and updates pyproject.toml and .templatesyncignore.
"""

__version__ = "1.0.0"

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def copy_instrument(destination_dir: Path) -> None:
    """
    Copy template directory to the destination.

    :param template_dir: Path to the template directory.
    :param destination_dir: Path to the new instrument directory.
    :return: None
    """

    demo_template_path: Path = (
        Path(__file__).resolve().parent.parent / "demo_instrument"
    ).resolve()

    shutil.copytree(str(demo_template_path), str(destination_dir))


def create_qserver(qserver_dir: Path, name: str) -> None:
    """
    Create a qserver config file in the destination directory.
    """

    demo_qserver_path: Path = (
        Path(__file__).resolve().parent.parent / "demo_qserver"
    ).resolve()

    os.makedirs(qserver_dir, exist_ok=True)
    # Copy all yml files from demo_qserver to destination qserver dir
    for yml_file in demo_qserver_path.glob("*"):
        shutil.copy2(yml_file, qserver_dir)

    # Update startup module in qs-config.yml
    qs_config_path = qserver_dir / "qs-config.yml"

    with open(qs_config_path, "r") as f:
        config_contents = f.read()
    # Replace demo_instrument with new name in startup module path
    updated_contents = config_contents.replace(
        "startup_module: demo_instrument.startup", f"startup_module: {name}.startup"
    )

    with open(qs_config_path, "w") as f:
        f.write(updated_contents)

    new_script_path = qserver_dir / "qs_host.sh"

    # Read script contents
    with open(new_script_path, "r") as src:
        script_contents = src.read()

    # Replace demo package name with new instrument name
    updated_contents = script_contents.replace("demo_instrument", name)

    # Write updated script
    with open(new_script_path, "w") as dest:
        dest.write(updated_contents)

    # Make script executable
    os.chmod(new_script_path, new_script_path.stat().st_mode | 0o755)


def main() -> None:
    """
    Parse arguments and create the instrument.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Create an instrument from a fixed template."
    )
    parser.add_argument(
        "name", type=str, help="New instrument name; must be a valid package name."
    )
    args = parser.parse_args()

    if re.fullmatch(r"[a-z][_a-z0-9]*", args.name) is None:
        print(f"Error: Invalid instrument name '{args.name}'.", file=sys.stderr)
        sys.exit(1)

    main_path: Path = Path(os.getcwd()).resolve()

    new_instrument_dir: Path = main_path / "src" / args.name

    new_qserver_dir: Path = main_path / "src" / f"{args.name}_qserver"

    print(
        f"Creating instrument '{args.name}' from demo_instrument into \
        '{new_instrument_dir}'."
    )

    if new_instrument_dir.exists():
        print(f"Error: Destination '{new_instrument_dir}' exists.", file=sys.stderr)
        sys.exit(1)

    try:
        copy_instrument(new_instrument_dir)
        print(f"Template copied to '{new_instrument_dir}'.")
    except Exception as exc:
        print(f"Error copying instrument: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        create_qserver(new_qserver_dir, args.name)
        print(f"Qserver config created in '{new_qserver_dir}'.")
    except Exception as exc:
        print(f"Error creating qserver config: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Instrument '{args.name}' created.")


if __name__ == "__main__":
    main()
