"""Tests for init_RE in apsbits.core.run_engine_init."""

import bluesky

from apsbits.core.run_engine_init import init_RE
from apsbits.utils.stored_dict import StoredDict


def _minimal_iconfig(tmp_path):
    """Return an iconfig sufficient for init_RE without EPICS (no SCAN_ID_PV)."""
    return {
        "RUN_ENGINE": {"MD_PATH": str(tmp_path / "md.yml")},
        "OPHYD": {"CONTROL_LAYER": "PyEpics", "TIMEOUTS": {}},
    }


def test_init_re_returns_runengine_and_supplemental_data(tmp_path):
    """init_RE returns a configured RunEngine and SupplementalData."""
    RE, sd = init_RE(_minimal_iconfig(tmp_path))
    assert isinstance(RE, bluesky.RunEngine)
    assert isinstance(sd, bluesky.SupplementalData)


def test_init_re_persists_metadata_with_stored_dict(tmp_path):
    """With MD_PATH set, RE.md is a StoredDict (dead PersistentDict branch removed)."""
    RE, _ = init_RE(_minimal_iconfig(tmp_path))
    assert isinstance(RE.md, StoredDict)
