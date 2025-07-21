#!/usr/bin/env python3
"""
Run an instrument's startup module and return the ophyd registry information.

This module provides functionality to dynamically import and run a package's
startup module, then return the ophyd registry information.
"""

__version__ = "1.0.0"

import argparse
import importlib
import sys
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

from apsbits.core.instrument_init import oregistry as Registry


def run_instrument_startup(package_name: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Run a package's startup module and return the ophyd registry information.

    :param package_name: The name of the package to run.
    :return: A tuple containing a boolean indicating success and the registry
             information.
    """
    try:
        # Import the startup module
        startup_module = importlib.import_module(f"{package_name}.startup")

        # Run the startup module
        if hasattr(startup_module, "main"):
            startup_module.main()

        # Get the registry information
        registry_info = {}
        for name, obj in Registry.registry.items():
            registry_info[name] = {
                "type": obj.__class__.__name__,
                "module": obj.__class__.__module__,
            }

        return True, registry_info
    except ImportError as exc:
        print(f"Error importing {package_name}.startup: {exc}", file=sys.stderr)
        return False, None
    except Exception as exc:
        print(f"Error running {package_name}.startup: {exc}", file=sys.stderr)
        return False, None


def main() -> None:
    """
    Parse arguments and run the instrument startup.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run an instrument's startup module and return the ophyd registry "
            "information."
        )
    )
    parser.add_argument("package_name", type=str, help="Name of the package to run.")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file to write the registry information to.",
    )
    args = parser.parse_args()

    success, registry_info = run_instrument_startup(args.package_name)

    if not success:
        sys.exit(1)

    if registry_info:
        print(f"Found {len(registry_info)} devices in the registry:")
        for name, info in registry_info.items():
            print(f"  {name}: {info['type']} from {info['module']}")

        if args.output:
            import json

            with open(args.output, "w") as f:
                json.dump(registry_info, f, indent=2)
            print(f"Registry information written to {args.output}")
    else:
        print("No devices found in the registry.")


if __name__ == "__main__":
    main()
