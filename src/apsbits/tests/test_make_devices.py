"""
Test to check if the make_devices function works as expected.
"""

import logging
from typing import TYPE_CHECKING

from apsbits.core.instrument_init import init_instrument
from apsbits.demo_instrument.startup import make_devices

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_make_devices_file_name(caplog: "LogCaptureFixture[str]") -> None:
    """
    Test to check if the make_devices function works as expected.
    """
    # Set the log level to capture INFO messages
    caplog.set_level(logging.INFO)
    instrument, oregistry = init_instrument("guarneri")

    # Run your function
    make_devices(file="devices.yml", device_manager=instrument)

    # Expected device names
    expected_devices = ["sim_motor", "sim_det"]

    # Check if all expected device messages are in the log output
    for device in expected_devices:
        expected_message = f"Adding ophyd device '{device}' to main namespace"
        assert any(expected_message in record.message for record in caplog.records)
