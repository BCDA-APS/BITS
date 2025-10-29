"""
Test the controls_setup module.
"""

from contextlib import nullcontext as does_not_raise

import ophyd
import pytest
from bluesky import RunEngine
from bluesky import plans as bp

from apsbits.utils.controls_setup import EpicsScanIdSource


def test_ioc(ioc):
    """Test the soft IOC."""
    signal = ophyd.EpicsSignal("test:scan_id", name="signal", connection_timeout=4)
    signal.wait_for_connection()
    assert signal.get() == -10


@pytest.mark.parametrize(
    "signal, initial, context",
    [
        pytest.param(
            ophyd.Signal(name="signal", value=-10),
            0,
            does_not_raise(),
            id="default",
        ),
        pytest.param(
            ophyd.Signal(name="signal", value=-10),
            1234,
            does_not_raise(),
            id="non-zero scan_id",
        ),
        pytest.param(
            ophyd.Signal(name="signal", value=-10),
            -654321,
            does_not_raise(),
            id="negative scan_id",
        ),
        pytest.param(
            ophyd.EpicsSignal(
                "no:such:pv",
                name="signal",
                connection_timeout=0.1,
            ),
            0,
            pytest.raises(TimeoutError, match="could not connect"),
            id="non-existing EPICS PV",
        ),
        pytest.param(
            ophyd.EpicsSignal(
                "test:scan_id",
                name="signal",
                connection_timeout=2,
            ),
            0,
            does_not_raise(),
            id="existing EPICS PV",
        ),
    ],
)
def test_EpicsScanIdSource(signal, initial, context, ioc):
    """Test the EpicsScanIdSource class"""
    with context:
        signal.wait_for_connection()
        assert signal.connected

        assert isinstance(ioc, dict)

        original_scan_id = signal.get()
        assert isinstance(original_scan_id, int)

        detector = ophyd.Signal(name="detector", value=0)
        RE = RunEngine()
        assert "scan_id" not in RE.md
        assert signal.get() == original_scan_id

        source = EpicsScanIdSource(signal)
        assert source.signal == signal

        RE.scan_id_source = source.epics_scan_id_source
        assert "scan_id" not in RE.md
        assert signal.get() == original_scan_id

        RE.md["scan_id"] = initial
        assert "scan_id" in RE.md
        assert signal.get() == original_scan_id  # still not updated by RE yet

        signal.put(initial)  # update the signal directly
        assert signal.get(use_monitor=False) == initial  # and confirm

        RE(bp.count([detector]))  # advances the scan_id
        assert "scan_id" in RE.md
        assert RE.md["scan_id"] == max(initial, 0) + 1
        assert RE.md["scan_id"] == signal.get()  # confirm RE updated this
