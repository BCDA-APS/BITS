"""
Pytest fixtures for instrument tests.

This module provides fixtures for initializing the RunEngine with devices,
allowing tests to operate with device-dependent configurations without relying
on the production startup logic.

Fixtures:
    runengine_with_devices: A RunEngine object in a session with devices configured.
"""

import time
from pathlib import Path
from typing import Any

import pytest

from apsbits.demo_instrument.startup import RE
from apsbits.demo_instrument.startup import make_devices
from apsbits.utils.config_loaders import load_config


@pytest.fixture(scope="session")
def runengine_with_devices() -> Any:
    """
    Initialize the RunEngine with devices for testing.

    This fixture calls RE with the `make_devices()` plan stub to mimic
    the behavior previously performed in the startup module.

    Returns:
        Any: An instance of the RunEngine with devices configured.
    """
    # Load the configuration before testing
    instrument_path = Path(__file__).parent.parent / "demo_instrument"
    iconfig_path = instrument_path / "configs" / "iconfig.yml"
    load_config(iconfig_path)

    # Initialize instrument and make devices
    from apsbits.core.instrument_init import init_instrument

    instrument, oregistry = init_instrument("guarneri")
    make_devices(file="devices.yml", device_manager=instrument)

    return RE


@pytest.fixture(scope="session")
def ioc():
    """Run a softIoc in a subprocess.

    Create a temporary EPICS database file that defines a long integer
    record at "test:scan_id", start softIoc in a subprocess and yield
    connection info for tests. Teardown stops the subprocess and
    removes the temporary file.
    """
    import os
    import subprocess
    import tempfile

    # Minimal EPICS DB defining a longout record for 'test:scan_id'.
    db_text = "\n".join(
        [
            'record(longout, "test:scan_id") {',
            # .
            '   field(DESC, "scan id")',
            "   field(VAL, -10)",
            "}",
        ]
    )

    # Write DB to a temporary file that persists until teardown.
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False)
    try:
        tf.write(db_text)
        tf.flush()
        tf.close()

        # Start softIoc. Capture output so if it fails immediately we can
        # surface useful error messages.
        proc = subprocess.Popen(
            [
                "softIoc",
                "-S",
                "-d",
                tf.name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait briefly for the process to initialize. If it exits early,
        # collect stdout/stderr and raise.
        timeout = 5.0
        poll = 0.0
        interval = 0.05
        while poll < timeout and proc.poll() is None:
            time.sleep(interval)
            poll += interval

        if proc.poll() is not None:
            out, err = proc.communicate(timeout=1)
            raise RuntimeError(
                "softIoc terminated unexpectedly. stdout: %r stderr: %r"
                % (out.decode(errors="ignore"), err.decode(errors="ignore"))
            )

        # Provide connection info for tests.
        yield dict(prefix="test1:", host="127.0.0.1", pv="test:scan_id")

    finally:
        # Teardown: terminate the softIoc subprocess and remove the DB file.
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        try:
            os.remove(tf.name)
        except Exception:
            pass
