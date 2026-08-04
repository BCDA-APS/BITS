"""
Direct unit tests for previously-untested helper modules (N22).

Covers: helper_functions.dynamic_import, aps_functions.host_on_aps_subnet,
session_setup.prepare_bits, baseline_setup.setup_baseline_stream, and
run_engine_init.init_RE.
"""

import types

import bluesky
import pytest

from apsbits.core.run_engine_init import init_RE
from apsbits.core.session_setup import prepare_bits
from apsbits.utils.aps_functions import host_on_aps_subnet
from apsbits.utils.baseline_setup import setup_baseline_stream
from apsbits.utils.helper_functions import dynamic_import
from apsbits.utils.stored_dict import StoredDict

# --- dynamic_import ---------------------------------------------------------


def test_dynamic_import_happy_path():
    """A valid dotted path resolves to the target object."""
    from ophyd import EpicsMotor

    assert dynamic_import("ophyd.EpicsMotor") is EpicsMotor


def test_dynamic_import_requires_dotted_path():
    """A path with no dot is rejected."""
    with pytest.raises(ValueError, match="dotted path"):
        dynamic_import("nodot")


def test_dynamic_import_rejects_relative_path():
    """A leading-dot (relative) path is rejected."""
    with pytest.raises(ValueError, match="absolute path"):
        dynamic_import(".relative.path")


# --- host_on_aps_subnet -----------------------------------------------------


def test_host_on_aps_subnet_returns_bool():
    """The detector always returns a bool."""
    assert isinstance(host_on_aps_subnet(), bool)


def test_host_on_aps_subnet_falls_back_off_subnet(monkeypatch):
    """A socket failure falls back to loopback, i.e. reports off-subnet."""

    class _FakeSock:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def settimeout(self, timeout):
            pass

        def connect(self, address):
            raise OSError("no network")

        def getsockname(self):
            return ("127.0.0.1", 0)

    monkeypatch.setattr(
        "apsbits.utils.aps_functions.socket.socket",
        lambda *args, **kwargs: _FakeSock(),
    )
    assert host_on_aps_subnet() is False


# --- prepare_bits -----------------------------------------------------------


def test_prepare_bits_runs():
    """prepare_bits configures the session without raising in a headless run."""
    prepare_bits()


# --- setup_baseline_stream --------------------------------------------------


def test_setup_baseline_stream_no_config(monkeypatch):
    """No BASELINE_LABEL key -> no objects added."""
    monkeypatch.setattr("apsbits.utils.baseline_setup.get_config", lambda: {})
    sd = types.SimpleNamespace(baseline=[])
    setup_baseline_stream(sd, oregistry=None)
    assert sd.baseline == []


def test_setup_baseline_stream_disabled(monkeypatch):
    """BASELINE_LABEL.ENABLE false -> no objects added."""
    monkeypatch.setattr(
        "apsbits.utils.baseline_setup.get_config",
        lambda: {"BASELINE_LABEL": {"ENABLE": False}},
    )
    sd = types.SimpleNamespace(baseline=[])
    setup_baseline_stream(sd, oregistry=None)
    assert sd.baseline == []


def test_setup_baseline_stream_adds_candidates(monkeypatch):
    """Enabled + labeled candidates -> candidates extend the baseline stream."""
    monkeypatch.setattr(
        "apsbits.utils.baseline_setup.get_config",
        lambda: {"BASELINE_LABEL": {"ENABLE": True}},
    )
    marker = object()
    oregistry = types.SimpleNamespace(findall=lambda label, allow_none=True: [marker])
    sd = types.SimpleNamespace(baseline=[])
    setup_baseline_stream(sd, oregistry)
    assert marker in sd.baseline


# --- init_RE ----------------------------------------------------------------


def test_init_RE_returns_runengine_and_supplemental_data(tmp_path):
    """init_RE returns a RunEngine + SupplementalData with a StoredDict md."""
    iconfig = {
        "RUN_ENGINE": {
            "MD_PATH": str(tmp_path / "md.yml"),
            "USE_PROGRESS_BAR": False,
        },
        "OPHYD": {"CONTROL_LAYER": "PyEpics"},
    }
    RE, sd = init_RE(iconfig)
    assert isinstance(RE, bluesky.RunEngine)
    assert isinstance(sd, bluesky.SupplementalData)
    assert isinstance(RE.md, StoredDict)
    assert sd in RE.preprocessors
