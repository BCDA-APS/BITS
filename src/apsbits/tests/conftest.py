"""
Pytest fixtures for instrument tests.

This module provides fixtures for initializing the RunEngine with devices,
allowing tests to operate with device-dependent configurations without relying
on the production startup logic.

Fixtures:
    runengine_with_devices: A RunEngine object in a session with devices configured.
"""

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

    RE(make_devices(file="devices.yml"))
    return RE
