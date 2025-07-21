"""
Tests for the run_instrument.py script.

This module contains tests for the functionality of the run_instrument.py script,
which is responsible for running a package's startup module and returning the
ophyd registry information.
"""

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch

from apsbits.api.run_instrument import main
from apsbits.api.run_instrument import run_instrument_startup


@pytest.fixture
def mock_registry() -> Generator[MagicMock, None, None]:
    """
    Create a mock ophyd registry for testing.

    :yield: A mock ophyd registry.
    """
    with patch("apsbits.api.run_instrument.Registry") as mock_registry:
        # Create a mock registry with some devices
        mock_registry.registry = {
            "device1": MagicMock(
                __class__=MagicMock(__name__="Device1", __module__="module1")
            ),
            "device2": MagicMock(
                __class__=MagicMock(__name__="Device2", __module__="module2")
            ),
        }
        yield mock_registry


def test_run_instrument_startup_success(mock_registry: MagicMock) -> None:
    """
    Test the run_instrument_startup function with a successful run.

    :param mock_registry: Fixture providing a mock ophyd registry.
    """
    with patch("importlib.import_module") as mock_import:
        # Create a mock startup module with a main function
        mock_startup = MagicMock()
        mock_startup.main = MagicMock()
        mock_import.return_value = mock_startup

        # Run the function
        success, registry_info = run_instrument_startup("test_package")

        # Verify the function was called correctly
        mock_import.assert_called_once_with("test_package.startup")
        mock_startup.main.assert_called_once()

        # Verify the registry information was returned correctly
        assert success is True
        assert registry_info is not None
        assert len(registry_info) == 2
        assert registry_info["device1"]["type"] == "Device1"
        assert registry_info["device1"]["module"] == "module1"
        assert registry_info["device2"]["type"] == "Device2"
        assert registry_info["device2"]["module"] == "module2"


def test_run_instrument_startup_no_main(mock_registry: MagicMock) -> None:
    """
    Test the run_instrument_startup function with a startup module without a main
    function.

    :param mock_registry: Fixture providing a mock ophyd registry.
    """
    with patch("importlib.import_module") as mock_import:
        # Create a mock startup module without a main function
        mock_startup = MagicMock()
        mock_import.return_value = mock_startup

        # Run the function
        success, registry_info = run_instrument_startup("test_package")

        # Verify the function was called correctly
        mock_import.assert_called_once_with("test_package.startup")

        # Verify the registry information was returned correctly
        assert success is True
        assert registry_info is not None
        assert len(registry_info) == 2


def test_run_instrument_startup_import_error(mock_registry: MagicMock) -> None:
    """
    Test the run_instrument_startup function with an import error.

    :param mock_registry: Fixture providing a mock ophyd registry.
    """
    with patch("importlib.import_module") as mock_import:
        # Make the import raise an ImportError
        mock_import.side_effect = ImportError("Module not found")

        # Run the function
        success, registry_info = run_instrument_startup("test_package")

        # Verify the function was called correctly
        mock_import.assert_called_once_with("test_package.startup")

        # Verify the function returned an error
        assert success is False
        assert registry_info is None


def test_run_instrument_startup_runtime_error(mock_registry: MagicMock) -> None:
    """
    Test the run_instrument_startup function with a runtime error.

    :param mock_registry: Fixture providing a mock ophyd registry.
    """
    with patch("importlib.import_module") as mock_import:
        # Create a mock startup module with a main function that raises an exception
        mock_startup = MagicMock()
        mock_startup.main = MagicMock(side_effect=RuntimeError("Runtime error"))
        mock_import.return_value = mock_startup

        # Run the function
        success, registry_info = run_instrument_startup("test_package")

        # Verify the function was called correctly
        mock_import.assert_called_once_with("test_package.startup")
        mock_startup.main.assert_called_once()

        # Verify the function returned an error
        assert success is False
        assert registry_info is None


def test_main_success(
    mock_registry: MagicMock, monkeypatch: "MonkeyPatch", capsys: "CaptureFixture[str]"
) -> None:
    """
    Test the main function with a successful run.

    :param mock_registry: Fixture providing a mock ophyd registry.
    :param monkeypatch: Pytest fixture for patching.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Mock the run_instrument_startup function
    with patch("apsbits.api.run_instrument.run_instrument_startup") as mock_run:
        # Make the function return a successful result
        mock_run.return_value = (
            True,
            {
                "device1": {"type": "Device1", "module": "module1"},
                "device2": {"type": "Device2", "module": "module2"},
            },
        )

        # Mock argparse to return a valid package name
        monkeypatch.setattr(
            "argparse.ArgumentParser.parse_args",
            lambda _: type(
                "Args", (), {"package_name": "test_package", "output": None}
            )(),
        )

        # Run the main function
        main()

        # Verify the function was called correctly
        mock_run.assert_called_once_with("test_package")

        # Verify the output
        captured = capsys.readouterr()
        assert "Found 2 devices in the registry:" in captured.out
        assert "device1: Device1 from module1" in captured.out
        assert "device2: Device2 from module2" in captured.out


def test_main_success_with_output(
    mock_registry: MagicMock,
    monkeypatch: "MonkeyPatch",
    capsys: "CaptureFixture[str]",
    tmp_path: Path,
) -> None:
    """
    Test the main function with a successful run and output file.

    :param mock_registry: Fixture providing a mock ophyd registry.
    :param monkeypatch: Pytest fixture for patching.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    :param tmp_path: Pytest fixture providing a temporary directory.
    """
    # Create a temporary output file
    output_file = tmp_path / "output.json"

    # Mock the run_instrument_startup function
    with patch("apsbits.api.run_instrument.run_instrument_startup") as mock_run:
        # Make the function return a successful result
        mock_run.return_value = (
            True,
            {
                "device1": {"type": "Device1", "module": "module1"},
                "device2": {"type": "Device2", "module": "module2"},
            },
        )

        # Mock argparse to return a valid package name and output file
        monkeypatch.setattr(
            "argparse.ArgumentParser.parse_args",
            lambda _: type(
                "Args", (), {"package_name": "test_package", "output": str(output_file)}
            )(),
        )

        # Run the main function
        main()

        # Verify the function was called correctly
        mock_run.assert_called_once_with("test_package")

        # Verify the output
        captured = capsys.readouterr()
        assert "Found 2 devices in the registry:" in captured.out
        assert "device1: Device1 from module1" in captured.out
        assert "device2: Device2 from module2" in captured.out
        assert f"Registry information written to {output_file}" in captured.out

        # Verify the output file was created and contains the expected JSON
        assert output_file.exists()
        content = output_file.read_text()
        assert '"device1"' in content
        assert '"type": "Device1"' in content
        assert '"module": "module1"' in content
        assert '"device2"' in content
        assert '"type": "Device2"' in content
        assert '"module": "module2"' in content


def test_main_failure(
    mock_registry: MagicMock, monkeypatch: "MonkeyPatch", capsys: "CaptureFixture[str]"
) -> None:
    """
    Test the main function with a failed run.

    :param mock_registry: Fixture providing a mock ophyd registry.
    :param monkeypatch: Pytest fixture for patching.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Mock the run_instrument_startup function
    with patch("apsbits.api.run_instrument.run_instrument_startup") as mock_run:
        # Make the function return a failure result
        mock_run.return_value = (False, None)

        # Mock argparse to return a valid package name
        monkeypatch.setattr(
            "argparse.ArgumentParser.parse_args",
            lambda _: type(
                "Args", (), {"package_name": "test_package", "output": None}
            )(),
        )

        # Run the main function and expect it to exit with code 1
        with pytest.raises(SystemExit) as excinfo:
            main()

        # Verify the exit code
        assert excinfo.value.code == 1

        # Verify the function was called correctly
        mock_run.assert_called_once_with("test_package")


def test_main_no_devices(
    mock_registry: MagicMock, monkeypatch: "MonkeyPatch", capsys: "CaptureFixture[str]"
) -> None:
    """
    Test the main function with a successful run but no devices in the registry.

    :param mock_registry: Fixture providing a mock ophyd registry.
    :param monkeypatch: Pytest fixture for patching.
    :param capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Mock the run_instrument_startup function
    with patch("apsbits.api.run_instrument.run_instrument_startup") as mock_run:
        # Make the function return a successful result but with no devices
        mock_run.return_value = (True, {})

        # Mock argparse to return a valid package name
        monkeypatch.setattr(
            "argparse.ArgumentParser.parse_args",
            lambda _: type(
                "Args", (), {"package_name": "test_package", "output": None}
            )(),
        )

        # Run the main function
        main()

        # Verify the function was called correctly
        mock_run.assert_called_once_with("test_package")

        # Verify the output
        captured = capsys.readouterr()
        assert "No devices found in the registry." in captured.out
