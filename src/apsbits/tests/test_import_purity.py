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
    """Every module must import without network I/O or file-write side effects.

    Blocks TCP connect and UDP ops (EPICS Channel Access uses UDP broadcast for
    PV discovery) plus write-mode file opens, all of which are forbidden at
    import time.
    """
    script = (
        "import socket\n"
        "def _blocker(name):\n"
        "    def _f(*a, **kw):\n"
        "        raise RuntimeError('Network I/O during import via ' + name)\n"
        "    return _f\n"
        "socket.socket.connect = _blocker('connect')\n"
        "socket.socket.bind = _blocker('bind')\n"
        "socket.socket.sendto = _blocker('sendto')\n"
        "import builtins\n"
        "_orig_open = builtins.open\n"
        "def _guarded_open(file, mode='r', *a, **kw):\n"
        "    if any(m in str(mode) for m in ('w', 'a', 'x', '+')):\n"
        "        raise RuntimeError('File write during import: ' + repr(file))\n"
        "    return _orig_open(file, mode, *a, **kw)\n"
        "builtins.open = _guarded_open\n"
        f"import {module_name}\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"{module_name} failed to import cleanly:\n{result.stderr.decode()}"
    )
