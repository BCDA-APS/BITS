"""
Pytest fixtures for instrument tests.

This module provides fixtures for initializing the RunEngine with devices,
allowing tests to operate with device-dependent configurations without relying
on the production startup logic.

Fixtures:
    runengine_with_devices: A RunEngine object in a session with devices configured.
    _preserve_global_config: (autouse) isolate global-config mutations between tests.
"""

import time
from pathlib import Path
from typing import Any

import pytest

from apsbits.demo_instrument.startup import RE
from apsbits.demo_instrument.startup import make_devices
from apsbits.utils.config_loaders import get_config
from apsbits.utils.config_loaders import load_config
from apsbits.utils.config_loaders import reset_config
from apsbits.utils.config_loaders import update_config


@pytest.fixture(autouse=True)
def _preserve_global_config():
    """
    Isolate global-config mutations so tests don't leak state to each other.

    ``make_devices`` (and others) read the module-global iconfig for the configs
    path; tests such as ``test_config`` replace or clear it. Snapshot before and
    restore after each test so ordering can't make a later test read a stale or
    empty configuration.
    """
    snapshot = dict(get_config())
    yield
    reset_config()
    update_config(snapshot)


@pytest.fixture(scope="function")
def runengine_with_devices() -> Any:
    """
    Initialize the RunEngine with devices for testing.

    Function-scoped for determinism: each test reloads the demo config and
    rebuilds the sim devices (``clear=True``), so a test's result never depends
    on which test triggered setup first.

    Shared-state contract: the returned RunEngine, plus the ``cat``/``bec``/
    ``oregistry`` globals imported from ``demo_instrument.startup``, are
    module-level singletons created once when that module is imported. This
    fixture refreshes the *device set* on each call, not those singletons.

    Returns:
        Any: The RunEngine with the sim devices (re)loaded.
    """
    # Load the configuration before testing
    instrument_path = Path(__file__).parent.parent / "demo_instrument"
    iconfig_path = instrument_path / "configs" / "iconfig.yml"
    load_config(iconfig_path)

    # Initialize instrument and make devices
    from apsbits.core.instrument_init import init_instrument

    instrument, oregistry = init_instrument("guarneri")
    make_devices(clear=True, file="devices.yml", device_manager=instrument)

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
    import shutil
    import subprocess
    import tempfile

    if shutil.which("softIoc") is None:
        pytest.skip("softIoc (EPICS base) not available")

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
    proc = None
    try:
        tf.write(db_text)
        tf.flush()
        tf.close()

        # Start softIoc. Capture output so if it fails immediately we can
        # surface useful error messages.
        try:
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
        except FileNotFoundError:
            pytest.skip("softIoc (EPICS base) not available")

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
        yield dict(prefix="test:", host="127.0.0.1", pv="test:scan_id")

    finally:
        # Teardown: terminate the softIoc subprocess and remove the DB file.
        if proc is not None:
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
