"""
Tests for create_new_instrument.py failure modes.

Makes the create-path defects first-class: the end-to-end happy path, the
rollback of partial state on failure (N5), and the create_qserver_script
guards (N6). test_delete_instrument.py already covers the mocked create path.
"""

import sys

import pytest

from apsbits.api import create_new_instrument
from apsbits.api.create_new_instrument import create_qserver_script
from apsbits.api.create_new_instrument import main as create_main


def _prepare_workspace(tmp_path, monkeypatch, name):
    """Point the create CLI at a scratch workspace (src/ + scripts/) as cwd."""
    (tmp_path / "scripts").mkdir()
    monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["bits-create", name])


def test_create_happy_path(tmp_path, monkeypatch):
    """A full create leaves src/<name> and scripts/<name>_qs_host.sh in place."""
    name = "probe_instrument"
    _prepare_workspace(tmp_path, monkeypatch, name)

    create_main()

    assert (tmp_path / "src" / name / "startup.py").exists()
    assert (tmp_path / "scripts" / f"{name}_qs_host.sh").exists()
    # startup_module was rewritten in the copied qs-config.yml.
    qs_config = (tmp_path / "src" / name / "qserver" / "qs-config.yml").read_text()
    assert f"startup_module: {name}.startup" in qs_config


def test_create_rollback_on_failure(tmp_path, monkeypatch):
    """N5: a failure after the copy removes the half-created instrument + script."""
    name = "probe_instrument"
    _prepare_workspace(tmp_path, monkeypatch, name)

    def boom(*args, **kwargs):
        raise RuntimeError("simulated failure")

    # Fail the last step, after copy_instrument + create_qserver_script succeed.
    monkeypatch.setattr(create_new_instrument, "edit_qserver_folder", boom)

    with pytest.raises(SystemExit) as excinfo:
        create_main()

    assert excinfo.value.code == 1
    assert not (tmp_path / "src" / name).exists()
    assert not (tmp_path / "scripts" / f"{name}_qs_host.sh").exists()


def test_create_qserver_script_missing_template(tmp_path, monkeypatch):
    """N6: a clear error when the template qs_host.sh is absent."""
    pkg = tmp_path / "empty_pkg"
    (pkg / "api").mkdir(parents=True)
    (pkg / "demo_scripts").mkdir()  # exists but has no qs_host.sh
    monkeypatch.setattr(
        create_new_instrument, "__file__", str(pkg / "api" / "create_new_instrument.py")
    )
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="Template qserver script not found"):
        create_qserver_script(scripts_dir, "probe")


def test_create_qserver_script_refuses_overwrite(tmp_path):
    """N6: refuse to overwrite an existing {name}_qs_host.sh (no data loss)."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    existing = scripts_dir / "probe_qs_host.sh"
    existing.write_text("do not clobber")

    with pytest.raises(FileExistsError, match="already exists"):
        create_qserver_script(scripts_dir, "probe")

    assert existing.read_text() == "do not clobber"  # untouched
