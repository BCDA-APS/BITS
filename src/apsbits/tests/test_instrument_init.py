"""Tests for init_instrument and make_devices in apsbits.core.instrument_init."""

import logging

import guarneri
import pytest

from apsbits.core import instrument_init
from apsbits.core.instrument_init import init_instrument
from apsbits.core.instrument_init import make_devices


def test_init_instrument_guarneri():
    """'guarneri' returns an Instrument and its device registry."""
    inst, oreg = init_instrument("guarneri")
    assert isinstance(inst, guarneri.Instrument)
    assert oreg is inst.devices


def test_init_instrument_none():
    """None is handled explicitly and returns (None, None)."""
    assert init_instrument(None) == (None, None)


def test_init_instrument_unknown():
    """An unknown manager string returns (None, None), not an implicit None."""
    assert init_instrument("bogus") == (None, None)


def test_init_instrument_happi():
    """The not-yet-implemented 'happi' manager returns (None, None)."""
    assert init_instrument("happi") == (None, None)


def test_make_devices_missing_file_returns(tmp_path):
    """A missing device file logs an error and returns without loading."""
    inst = guarneri.Instrument({})
    result = make_devices(
        file="does_not_exist.yml",
        path=str(tmp_path),
        device_manager=inst,
        clear=False,
        pause=0,
    )
    assert result is None


def test_make_devices_reraises_on_load_error(monkeypatch, tmp_path):
    """A failure while loading the device file propagates (no silent swallow)."""
    inst = guarneri.Instrument({})
    (tmp_path / "devices.yml").write_text("[]\n")

    async def _boom(*args, **kwargs):
        raise RuntimeError("load failed")

    monkeypatch.setattr(instrument_init, "guarneri_namespace_loader", _boom)
    with pytest.raises(RuntimeError, match="load failed"):
        make_devices(
            file="devices.yml",
            path=str(tmp_path),
            device_manager=inst,
            clear=False,
            pause=0,
        )


def test_make_devices_rejects_string_manager(tmp_path):
    """Passing the string 'guarneri' (not an Instrument instance) is rejected."""
    (tmp_path / "devices.yml").write_text("[]\n")
    with pytest.raises(ValueError, match="Unrecognized device_manager"):
        make_devices(
            file="devices.yml",
            path=str(tmp_path),
            device_manager="guarneri",
            clear=False,
            pause=0,
        )


def test_make_devices_warns_when_clear_ignored(tmp_path, caplog):
    """clear=True with a non-Instrument manager logs a warning."""
    (tmp_path / "devices.yml").write_text("[]\n")
    with caplog.at_level(logging.WARNING):
        make_devices(
            file="devices.yml",
            path=str(tmp_path),
            device_manager="happi",
            clear=True,
            pause=0,
        )
    assert "clear=True ignored" in caplog.text
