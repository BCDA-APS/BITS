"""
EPICS & ophyd related setup
===========================

.. autosummary::
    ~connect_scan_id_pv
    ~EpicsScanIdSource
    ~set_control_layer
    ~set_timeouts
"""

import logging
from typing import Any
from typing import Optional

import ophyd
from ophyd.signal import EpicsSignalBase

logger = logging.getLogger(__name__)

DEFAULT_CONTROL_LAYER = "PyEpics"
DEFAULT_TIMEOUT = 60  # default used next...
SCAN_ID_SIGNAL_NAME = "scan_id_epics"


class EpicsScanIdSource:
    """
    Remember the Signal used to define the scan_id.

    Provides a callback function to be used by the RunEngine
    to read and update an ophyd Signal that stores the scan id value.

    Example::

        scan_id_epics = ophyd.EpicsSignal("IOC:scan_id", name="scan_id_epics")
        source = EpicsScanIdSource(scan_id_epics)
        RE.scan_id_source = source.epics_scan_id_source

    .. autosummary::
        ~epics_scan_id_source
    """

    def __init__(self, signal: ophyd.Signal):
        """
        Constructor.

        While the name suggests this will be used with an EPICS PV,
        this could be used with any Signal object, making the callback
        method easier to test.
        """
        self.signal = signal

    def epics_scan_id_source(self, _md: dict[str, Any]) -> int:
        """
        Callback function for RunEngine.  Returns *next* scan_id to be used.

        Outline:

        * Get current scan_id from PV.
        * Apply lower limit of zero.
        * Increment (so that scan_id numbering starts from 1).
        * Set PV with new value.
        * Return new value.

        Parameters:

        _md: dict
            Metadata dict provided by the RE caller.  Ignored here.

        Raises:

        ophyd.signal.ConnectionTimeoutError:
            If PV is not connected when next ``bps.open_run()`` is called.
        """
        new_scan_id = max(self.signal.get(), 0) + 1
        self.signal.put(new_scan_id)
        return new_scan_id


def connect_scan_id_pv(RE: Any, pv: Optional[str] = None) -> None:
    """
    Define a PV to use for the RunEngine's `scan_id`.
    """
    from ophyd import EpicsSignal

    if pv is None:
        return

    try:
        scan_id_epics = EpicsSignal(pv, name="scan_id_epics")
    except TypeError:  # when Sphinx substitutes EpicsSignal with _MockModule
        return
    logger.info("Using EPICS PV %r for RunEngine 'scan_id'", pv)

    # Setup the RunEngine to call epics_scan_id_source()
    # which uses the EPICS PV to provide the scan_id.
    source = EpicsScanIdSource(scan_id_epics)
    RE.scan_id_source = source.epics_scan_id_source

    scan_id_epics.wait_for_connection()
    try:
        RE.md["scan_id_pv"] = scan_id_epics.pvname
        RE.md["scan_id"] = scan_id_epics.get()  # set scan_id from EPICS
    except TypeError:
        pass  # Ignore PersistentDict errors that only raise when making the docs


def set_control_layer(control_layer: str = DEFAULT_CONTROL_LAYER):
    """
    Communications library between ophyd and EPICS Channel Access.

    Choices are: PyEpics (default) or caproto.

    OPHYD_CONTROL_LAYER is an application of "lessons learned."

    Only used in a couple rare cases where PyEpics code was failing.
    It's defined here since it was difficult to find how to do this
    in the ophyd documentation.
    """

    ophyd.set_cl(control_layer.lower())

    logger.info("using ophyd control layer: %r", ophyd.cl.name)


def set_timeouts(timeouts: dict[str, float]) -> None:
    """Set default timeout for all EpicsSignal connections & communications."""
    if not EpicsSignalBase._EpicsSignalBase__any_instantiated:
        # Only BEFORE any EpicsSignalBase (or subclass) are created!
        EpicsSignalBase.set_defaults(
            auto_monitor=True,
            timeout=timeouts.get("PV_READ", DEFAULT_TIMEOUT),
            write_timeout=timeouts.get("PV_WRITE", DEFAULT_TIMEOUT),
            connection_timeout=timeouts.get("PV_CONNECTION", DEFAULT_TIMEOUT),
        )
