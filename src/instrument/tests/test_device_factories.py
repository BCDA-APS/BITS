"""Test the device factories."""

import pytest

from ..devices.factories import motors
from ..devices.factories import predefined_device


@pytest.mark.parametrize(
    "callable, name, klass",
    [
        ["ophyd.sim.motor", None, "SynAxis"],
        ["ophyd.sim.motor", "sim_motor", "SynAxis"],
        ["ophyd.sim.noisy_det", None, "SynGauss"],
        ["ophyd.sim.noisy_det", "sim_det", "SynGauss"],
    ],
)
def test_predefined(callable, name, klass):
    """import predefined devices"""
    for device in predefined_device(callable=callable, name=name):
        assert device is not None
        assert device.__class__.__name__ == klass
        if name is not None:
            assert device.name == name


@pytest.mark.parametrize(
    "kwargs",
    [
        {"prefix": "ioc:m", "first": 1, "last": 4, "labels": ["motor"]},
        {"prefix": "ioc:m", "names": "m", "first": 7, "last": 22, "labels": ["motor"]},
    ],
)
def test_motors(kwargs):
    """create a block of motors"""
    count = 0
    for device in motors(**kwargs):
        count += 1
        assert device is not None
        assert device.__class__.__name__ == "EpicsMotor"
        if kwargs.get("names") is None:
            assert device.name.startswith("m")
            assert isinstance(int(device.name[1:]), int)
    assert count == (1 + kwargs["last"] - kwargs["first"])
