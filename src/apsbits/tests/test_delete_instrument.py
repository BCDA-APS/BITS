"""
Tests for the delete_instrument.py and create_new_instrument.py scripts.

This module contains tests for the functionality of both scripts,
which are responsible for creating and deleting instruments and their
associated qserver configurations.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Generator

import pytest

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

from apsbits.api.create_new_instrument import copy_instrument
from apsbits.api.create_new_instrument import create_qserver
from apsbits.api.create_new_instrument import main as create_main
from apsbits.api.delete_instrument import delete_instrument
from apsbits.api.delete_instrument import get_instrument_paths
from apsbits.api.delete_instrument import main as delete_main
from apsbits.api.delete_instrument import validate_instrument_name


@pytest.fixture
def temp_instrument_dirs(tmp_path: Path) -> Generator[tuple[Path, Path], None, None]:
    """
    Create temporary instrument and qserver directories for testing.

    :param tmp_path: Pytest fixture providing a temporary directory.
    :yield: A tuple containing the instrument directory path and qserver directory path.
    """
    instrument_dir = tmp_path / "src" / "test_instrument"
    qserver_dir = tmp_path / "src" / "test_instrument_qserver"

    # Create the directories
    instrument_dir.mkdir(parents=True, exist_ok=True)
    qserver_dir.mkdir(parents=True, exist_ok=True)

    # Create some dummy files
    (instrument_dir / "dummy.py").write_text("print('Hello')")
    (qserver_dir / "qs-config.yml").write_text("config: test")

    yield instrument_dir, qserver_dir


@pytest.fixture
def mock_demo_dirs(
    tmp_path: Path, monkeypatch: "MonkeyPatch"
) -> Generator[tuple[Path, Path], None, None]:
    """
    Create mock demo directories for testing the create_new_instrument script.

    :param tmp_path: Pytest fixture providing a temporary directory.
    :param monkeypatch: Pytest fixture for patching.
    :yield: A tuple containing the mock demo instrument directory path and mock demo
           qserver directory path.
    """
    # Create mock demo directories
    demo_instrument_dir = tmp_path / "demo_instrument"
    demo_qserver_dir = tmp_path / "demo_qserver"

    # Create the directories
    demo_instrument_dir.mkdir(parents=True, exist_ok=True)
    demo_qserver_dir.mkdir(parents=True, exist_ok=True)

    # Create some dummy files
    (demo_instrument_dir / "startup.py").write_text("print('Demo startup')")
    (demo_qserver_dir / "qs-config.yml").write_text(
        "startup_module: demo_instrument.startup"
    )
    (demo_qserver_dir / "qs_host.sh").write_text("python -m demo_instrument.startup")

    # Patch the paths in the create_new_instrument module
    monkeypatch.setattr(
        "apsbits.api.create_new_instrument.Path",
        lambda *args: Path(*args)
        if args[0] != __file__
        else tmp_path / "create_new_instrument.py",
    )

    yield demo_instrument_dir, demo_qserver_dir


# Tests for delete_instrument.py


def test_validate_instrument_name() -> None:
    """
    Test the validate_instrument_name function with various inputs.
    """
    assert validate_instrument_name("valid_name") is True
    assert validate_instrument_name("valid_name123") is True
    assert validate_instrument_name("invalid-name") is False
    assert validate_instrument_name("InvalidName") is False
    assert validate_instrument_name("123invalid") is False


def test_get_instrument_paths(monkeypatch: "MonkeyPatch", tmp_path: Path) -> None:
    """
    Test the get_instrument_paths function.

    :param monkeypatch: Pytest fixture for patching.
    :param tmp_path: Pytest fixture providing a temporary directory.
    """
    # Patch os.getcwd to return our temporary directory
    monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))

    instrument_dir, qserver_dir = get_instrument_paths("test_instrument")

    assert instrument_dir == tmp_path / "src" / "test_instrument"
    assert qserver_dir == tmp_path / "src" / "test_instrument_qserver"


def test_delete_instrument(temp_instrument_dirs: tuple[Path, Path]) -> None:
    """
    Test the delete_instrument function.

    :param temp_instrument_dirs: Fixture providing temporary instrument directories.
    """
    instrument_dir, qserver_dir = temp_instrument_dirs

    # Verify directories exist before deletion
    assert instrument_dir.exists()
    assert qserver_dir.exists()

    # Delete the directories
    delete_instrument(instrument_dir, qserver_dir)

    # Verify directories no longer exist in their original location
    assert not instrument_dir.exists()
    assert not qserver_dir.exists()

    # Verify directories exist in .deleted directory
    deleted_dir = Path(os.getcwd()).resolve() / ".deleted"
    assert deleted_dir.exists()

    # Check that at least one directory with the instrument name exists in .deleted
    instrument_name = instrument_dir.name
    qserver_name = qserver_dir.name

    # Find directories in .deleted that start with the instrument or qserver name
    instrument_in_deleted = any(
        d.name.startswith(instrument_name) for d in deleted_dir.iterdir() if d.is_dir()
    )
    qserver_in_deleted = any(
        d.name.startswith(qserver_name) for d in deleted_dir.iterdir() if d.is_dir()
    )

    assert (
        instrument_in_deleted
    ), f"No directory starting with '{instrument_name}' found in .deleted"
    assert (
        qserver_in_deleted
    ), f"No directory starting with '{qserver_name}' found in .deleted"


def test_delete_instrument_nonexistent(tmp_path: Path) -> None:
    """
    Test the delete_instrument function with nonexistent directories.

    :param tmp_path: Pytest fixture providing a temporary directory.
    """
    nonexistent_instrument = tmp_path / "nonexistent_instrument"
    nonexistent_qserver = tmp_path / "nonexistent_qserver"

    # Should not raise an exception
    delete_instrument(nonexistent_instrument, nonexistent_qserver)


def test_delete_main_invalid_name(capsys: "CaptureFixture[str]") -> None:
    """
    Test the main function with an invalid instrument name.

    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    with pytest.raises(SystemExit) as excinfo:
        delete_main()

    assert excinfo.value.code == 2  # argparse exits with code 2 for missing arguments
    captured = capsys.readouterr()
    # Check for either the missing argument error or the unrecognized arguments error
    assert any(
        error in captured.err
        for error in [
            "error: the following arguments are required: name",
            "error: unrecognized arguments:",
        ]
    )


def test_delete_main_nonexistent_instrument(
    monkeypatch: "MonkeyPatch", capsys: "CaptureFixture[str]"
) -> None:
    """
    Test the main function with a nonexistent instrument.

    :param monkeypatch: Pytest fixture for patching.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Mock argparse to return a valid name
    monkeypatch.setattr(
        "argparse.ArgumentParser.parse_args",
        lambda _: type("Args", (), {"name": "nonexistent", "force": False})(),
    )

    with pytest.raises(SystemExit) as excinfo:
        delete_main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert (
        "Error: Neither instrument 'nonexistent' nor its qserver configuration exist"
        in captured.err
    )


def test_delete_main_successful_deletion(
    monkeypatch: "MonkeyPatch",
    mocker: "MockerFixture",
    temp_instrument_dirs: tuple[Path, Path],
    capsys: "CaptureFixture[str]",
) -> None:
    """
    Test the main function with a successful deletion.

    :param monkeypatch: Pytest fixture for patching.
    :param mocker: Pytest fixture for mocking.
    :param temp_instrument_dirs: Fixture providing temporary instrument directories.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    instrument_dir, qserver_dir = temp_instrument_dirs

    # Mock get_instrument_paths to return our test directories
    mocker.patch(
        "apsbits.api.delete_instrument.get_instrument_paths",
        return_value=(instrument_dir, qserver_dir),
    )

    # Mock argparse to return a valid name and force=True
    monkeypatch.setattr(
        "argparse.ArgumentParser.parse_args",
        lambda _: type("Args", (), {"name": "test_instrument", "force": True})(),
    )

    # Mock input to return 'y'
    monkeypatch.setattr("builtins.input", lambda _: "y")

    delete_main()

    captured = capsys.readouterr()
    assert (
        "Instrument 'test_instrument' and its qserver configuration have been "
        "moved to .deleted directory" in captured.out
    )
    assert not instrument_dir.exists()
    assert not qserver_dir.exists()

    # Verify directories exist in .deleted directory
    deleted_dir = Path(os.getcwd()).resolve() / ".deleted"
    assert deleted_dir.exists()

    # Check that at least one directory with the instrument name exists in .deleted
    instrument_name = instrument_dir.name
    qserver_name = qserver_dir.name

    # Find directories in .deleted that start with the instrument or qserver name
    instrument_in_deleted = any(
        d.name.startswith(instrument_name) for d in deleted_dir.iterdir() if d.is_dir()
    )
    qserver_in_deleted = any(
        d.name.startswith(qserver_name) for d in deleted_dir.iterdir() if d.is_dir()
    )

    assert (
        instrument_in_deleted
    ), f"No directory starting with '{instrument_name}' found in .deleted"
    assert (
        qserver_in_deleted
    ), f"No directory starting with '{qserver_name}' found in .deleted"


def test_delete_main_cancelled_deletion(
    monkeypatch: "MonkeyPatch",
    mocker: "MockerFixture",
    temp_instrument_dirs: tuple[Path, Path],
    capsys: "CaptureFixture[str]",
) -> None:
    """
    Test the main function with a cancelled deletion.

    :param monkeypatch: Pytest fixture for patching.
    :param mocker: Pytest fixture for mocking.
    :param temp_instrument_dirs: Fixture providing temporary instrument directories.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    instrument_dir, qserver_dir = temp_instrument_dirs

    # Mock get_instrument_paths to return our test directories
    mocker.patch(
        "apsbits.api.delete_instrument.get_instrument_paths",
        return_value=(instrument_dir, qserver_dir),
    )

    # Mock argparse to return a valid name and force=False
    monkeypatch.setattr(
        "argparse.ArgumentParser.parse_args",
        lambda _: type("Args", (), {"name": "test_instrument", "force": False})(),
    )

    # Mock input to return 'n'
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with pytest.raises(SystemExit) as excinfo:
        delete_main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Operation cancelled" in captured.out
    assert instrument_dir.exists()
    assert qserver_dir.exists()


# Tests for create_new_instrument.py


def test_copy_instrument(tmp_path: Path, mock_demo_dirs: tuple[Path, Path]) -> None:
    """
    Test the copy_instrument function.

    :param tmp_path: Pytest fixture providing a temporary directory.
    :param mock_demo_dirs: Fixture providing mock demo directories.
    """
    demo_instrument_dir, _ = mock_demo_dirs
    destination_dir = tmp_path / "new_instrument"

    # Copy the instrument
    copy_instrument(destination_dir)

    # Verify the directory was created
    assert destination_dir.exists()

    # Verify the file was copied and contains expected content
    startup_file = destination_dir / "startup.py"
    assert startup_file.exists()
    content = startup_file.read_text()
    assert "Start Bluesky Data Acquisition sessions of all kinds." in content
    assert "from apsbits.core.best_effort_init import init_bec_peaks" in content
    assert 'RE(make_devices(clear=False, file="devices.yml"))' in content


def test_create_qserver(tmp_path: Path, mock_demo_dirs: tuple[Path, Path]) -> None:
    """
    Test the create_qserver function.

    :param tmp_path: Pytest fixture providing a temporary directory.
    :param mock_demo_dirs: Fixture providing mock demo directories.
    """
    _, demo_qserver_dir = mock_demo_dirs
    qserver_dir = tmp_path / "new_qserver"
    name = "new_instrument"

    # Create the qserver
    create_qserver(qserver_dir, name)

    # Verify the directory was created
    assert qserver_dir.exists()

    # Verify the files were copied
    assert (qserver_dir / "qs-config.yml").exists()
    assert (qserver_dir / "qs_host.sh").exists()

    # Verify the startup module was updated
    config_content = (qserver_dir / "qs-config.yml").read_text()
    assert "startup_module: new_instrument.startup" in config_content

    # Verify the script was updated
    script_content = (qserver_dir / "qs_host.sh").read_text()
    assert "#!/bin/bash" in script_content
    assert "start-re-manager" in script_content
    assert "CONFIGS_DIR=$(readlink -f" in script_content
    assert "new_instrument/configs" in script_content

    # Verify the script is executable
    assert (qserver_dir / "qs_host.sh").stat().st_mode & 0o755 == 0o755


def test_create_main_invalid_name(capsys: "CaptureFixture[str]") -> None:
    """
    Test the main function with an invalid instrument name.

    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    with pytest.raises(SystemExit) as excinfo:
        create_main()

    assert excinfo.value.code == 2  # argparse exits with code 2 for missing arguments
    captured = capsys.readouterr()
    # Check for either the missing argument error or the unrecognized arguments error
    assert any(
        error in captured.err
        for error in [
            "error: the following arguments are required: name",
            "error: unrecognized arguments:",
        ]
    )


def test_create_main_existing_instrument(
    monkeypatch: "MonkeyPatch", tmp_path: Path, capsys: "CaptureFixture[str]"
) -> None:
    """
    Test the main function with an existing instrument.

    :param monkeypatch: Pytest fixture for patching.
    :param tmp_path: Pytest fixture providing a temporary directory.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Create an existing instrument directory
    existing_dir = tmp_path / "src" / "existing_instrument"
    existing_dir.mkdir(parents=True, exist_ok=True)

    # Patch os.getcwd to return our temporary directory
    monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))

    # Mock argparse to return a valid name
    monkeypatch.setattr(
        "argparse.ArgumentParser.parse_args",
        lambda _: type("Args", (), {"name": "existing_instrument"})(),
    )

    with pytest.raises(SystemExit) as excinfo:
        create_main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Destination" in captured.err
    assert "exists" in captured.err


def test_create_main_successful_creation(
    monkeypatch: "MonkeyPatch",
    mocker: "MockerFixture",
    tmp_path: Path,
    mock_demo_dirs: tuple[Path, Path],
    capsys: "CaptureFixture[str]",
) -> None:
    """
    Test the main function with a successful creation.

    :param monkeypatch: Pytest fixture for patching.
    :param mocker: Pytest fixture for mocking.
    :param tmp_path: Pytest fixture providing a temporary directory.
    :param mock_demo_dirs: Fixture providing mock demo directories.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Patch os.getcwd to return our temporary directory
    monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))

    # Mock argparse to return a valid name
    monkeypatch.setattr(
        "argparse.ArgumentParser.parse_args",
        lambda _: type("Args", (), {"name": "new_instrument"})(),
    )

    # Mock the copy_instrument and create_qserver functions
    mock_copy = mocker.patch("apsbits.api.create_new_instrument.copy_instrument")
    mock_qserver = mocker.patch("apsbits.api.create_new_instrument.create_qserver")

    create_main()

    # Verify the functions were called with the correct arguments
    mock_copy.assert_called_once_with(tmp_path / "src" / "new_instrument")
    mock_qserver.assert_called_once_with(
        tmp_path / "src" / "new_instrument_qserver", "new_instrument"
    )

    captured = capsys.readouterr()
    assert "Creating instrument 'new_instrument'" in captured.out
    assert "Template copied to" in captured.out
    assert "Qserver config created in" in captured.out
    assert "Instrument 'new_instrument' created" in captured.out
