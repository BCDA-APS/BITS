"""
Pytest fixtures for instrument tests.

This module provides fixtures for initializing the RunEngine with devices,
allowing tests to operate with device-dependent configurations without relying
on the production startup logic.

Fixtures:
    runengine_with_devices: A RunEngine object in a session with devices configured.
"""

import asyncio
import threading
import time
from pathlib import Path
from typing import Any

import pytest
from caproto.server import PVGroup
from caproto.server import pvproperty
from caproto.server import run

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
def ioc():  # FIXME: IOC and PV is not found by test code
    """Running IOC using caproto, serving PV 'test:scan_id'."""

    class TestIOC(PVGroup):
        scan_id = pvproperty(value=0, dtype="int")

    # Options dict expected by caproto.server.run()
    opts = {
        "ioc": TestIOC,
        "name": "test_ioc",
        "prefix": "test:",
        "tcp_port": 0,  # use 0 so OS assigns a free port
        "udp_port": 0,
        "broadcast": None,
        "nodaemon": True,
        "verbose": False,
        "discovered": True,
        "version": False,
        "print_prefix": False,
        "list_pvs": False,
        "foreground": True,
        "quiet": False,
        "reactor": None,
        "log": None,
        "args": [],
    }

    loop = asyncio.new_event_loop()
    thread_exc = {}
    # Will be populated after run() starts with a mapping containing server info,
    # specifically the selected tcp_port (CA server port) used for connecting.
    started = {}

    def run_ioc():
        asyncio.set_event_loop(loop)
        try:
            # run(opts) returns when IOC is running; it exposes server info via its return
            info = loop.run_until_complete(run(opts))
            # run() may return None in some builds; try to read opts['tcp_port'] if set later.
            started["info"] = info
        except Exception as exc:
            thread_exc["exc"] = exc
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception:
                pass
            loop.close()

    t = threading.Thread(target=run_ioc, daemon=True)
    t.start()

    # Wait for IOC to start and discover the chosen port.
    timeout = 5.0
    poll = 0.0
    interval = 0.05
    while poll < timeout and "info" not in started and "exc" not in thread_exc:
        time.sleep(interval)
        poll += interval

    if thread_exc.get("exc"):
        raise thread_exc["exc"]

    # If run() returned server info use that. Otherwise fallback: try to obtain tcp_port from opts
    tcp_port = None
    if started.get("info") and isinstance(started["info"], dict):
        tcp_port = started["info"].get("tcp_port")
    if tcp_port is None:
        # If run() didn't return info, inspect opts -- caproto may have set tcp_port to actual value.
        tcp_port = opts.get("tcp_port") or 0

    # If tcp_port is 0 here, discovery by broadcast may still work; to be deterministic,
    # let the test use the host/port returned by the IOC via CA search. Provide prefix and port.
    yield {"prefix": "test:", "ca_port": tcp_port, "host": "127.0.0.1"}

    # Teardown: stop IOC by stopping its event loop thread
    loop.call_soon_threadsafe(loop.stop)
    t.join(timeout=2)
