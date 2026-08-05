"""
Test to check if the make_devices function works as expected.
"""

from apsbits.core.instrument_init import init_instrument
from apsbits.demo_instrument.startup import make_devices


def test_make_devices_file_name() -> None:
    """
    Test that make_devices registers the expected devices in the oregistry.
    """
    instrument, oregistry = init_instrument("guarneri")

    make_devices(file="devices.yml", device_manager=instrument)

    # Devices resolve by name in the registry (replaces the brittle log-text check).
    for device in ("sim_motor", "sim_det"):
        assert oregistry[device] is not None
