"""
Test to check if the make_devices function works as expected.
"""

import logging

from apsbits.demo_instrument.startup import RE
from apsbits.demo_instrument.startup import make_devices


def test_make_devices_file_name(caplog):
    """
    Test to check if the make_devices function works as expected.
    """

    # Set the log level to capture INFO messages
    caplog.set_level(logging.INFO)

    # Run your function
    RE(make_devices(file="devices.yml"))

    # Expected device names
    expected_devices = ["sim_motor", "shutter", "sim_det"]

    # Check if all expected device messages are in the log output
    for device in expected_devices:
        expected_message = f"Adding ophyd device '{device}' to main namespace"
        assert any(expected_message in record.message for record in caplog.records)
