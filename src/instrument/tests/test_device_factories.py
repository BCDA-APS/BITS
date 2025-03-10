"""Test the device factories."""

import pytest

from ..utils.sim_creator import motors
from ..utils.sim_creator import predefined_device


@pytest.mark.parametrize(
    "creator, name, klass",
    [
        ["ophyd.sim.motor", None, "SynAxis"],
        ["ophyd.sim.motor", "sim_motor", "SynAxis"],
        ["ophyd.sim.noisy_det", None, "SynGauss"],
        ["ophyd.sim.noisy_det", "sim_det", "SynGauss"],
    ],
)
def test_predefined(creator, name, klass):
    """import predefined devices"""
    for device in predefined_device(creator=creator, name=name):
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
