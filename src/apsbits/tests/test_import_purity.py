"""
Import purity regression test.

Verifies that every module in src/apsbits/ (except demo_instrument/startup.py)
can be imported without side effects. The import-purity test spawns a subprocess
per module with network I/O blocked to catch the most dangerous class of side effect.
"""

import os
import subprocess
import sys

import pytest


def discover_all_modules():
    """Walk src/apsbits/ and return dotted module names for all .py files."""
    base = os.path.join(os.path.dirname(__file__), "..")
    base = os.path.abspath(base)
    modules = []

    for root, dirs, files in os.walk(base):
        # Skip test directories and __pycache__
        dirs[:] = [d for d in dirs if d not in ("tests", "__pycache__")]

        for f in files:
            if not f.endswith(".py"):
                continue
            if f == "_version.py":
                continue

            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, os.path.join(base, ".."))

            # Skip startup.py — it IS the init sequence
            if relpath.endswith("demo_instrument/startup.py"):
                continue

            # Convert path to module name
            module = relpath.replace(os.sep, ".").removesuffix(".py")
            if module.endswith(".__init__"):
                module = module.removesuffix(".__init__")

            modules.append(module)

    return sorted(modules)


@pytest.mark.slow
@pytest.mark.parametrize("module_name", discover_all_modules())
def test_module_imports_cleanly(module_name):
    """Every module must be importable without network I/O side effects."""
    script = (
        "import socket\n"
        "_orig_connect = socket.socket.connect\n"
        "def _block(*a, **kw):\n"
        "    raise RuntimeError('Network I/O during import')\n"
        "socket.socket.connect = _block\n"
        f"import {module_name}\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        timeout=30,
    )
    assert (
        result.returncode == 0
    ), f"{module_name} failed to import cleanly:\n{result.stderr.decode()}"
