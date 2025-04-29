"""Tests for the make_devices functionality."""

from __future__ import annotations

import logging
import pathlib
from typing import TYPE_CHECKING

import pytest
from ophydregistry import Registry

from apsbits.core.instrument_init import make_devices

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def mock_registry(mocker: MockerFixture) -> None:
    """Mock the oregistry to avoid actual device creation."""
    registry = Registry(auto_register=True)
    mocker.patch("apsbits.core.instrument_init.oregistry", registry)
    return registry


@pytest.fixture
def mock_config(mocker: MockerFixture) -> None:
    """Mock the config loader to return test configuration."""
    mock_config = {
        "MAKE_DEVICES": {"LOG_LEVEL": "info"},
        "INSTRUMENT_PATH": "/test/path",
    }
    mocker.patch("apsbits.utils.config_loaders.get_config", return_value=mock_config)


@pytest.fixture
def mock_namespace(mocker: MockerFixture) -> None:
    """Mock the main namespace to track device additions/removals."""
    mock_ns = {}
    mocker.patch.dict("sys.modules", {"__main__": type("MockModule", (), mock_ns)})


@pytest.fixture
def mock_instrument(mocker: MockerFixture) -> None:
    """Mock the Instrument class to avoid actual device creation."""
    mock_instr = mocker.MagicMock()
    mocker.patch("apsbits.core.instrument_init._instr", mock_instr)
    return mock_instr


@pytest.fixture
def mock_run_blocking_function(mocker: MockerFixture) -> None:
    """Mock the run_blocking_function to avoid additional sleep calls."""

    def mock_run(func, *args, **kwargs):
        func(*args, **kwargs)
        yield from []  # Empty generator

    mocker.patch("apsbits.core.instrument_init.run_blocking_function", mock_run)


def test_make_devices_basic(
    mock_registry: Registry,
    mock_config: None,
    mock_namespace: None,
    mock_instrument: None,
    mock_run_blocking_function: None,
    caplog: LogCaptureFixture,
    tmp_path: pathlib.Path,
) -> None:
    """Test basic make_devices functionality."""
    caplog.set_level(logging.INFO)

    # Create a temporary device file in the configs directory
    configs_path = tmp_path / "configs"
    configs_path.mkdir()
    test_file = configs_path / "test_devices.yml"
    test_file.write_text("""
    ophyd.sim.SynGauss:
      - name: test_device
        center: 0
        sigma: 1
        noise: 0.1
    """)

    # Mock the config path resolution
    mock_instrument.load.return_value = None

    # Run make_devices
    list(make_devices(file=str(test_file.name), path=str(configs_path)))

    # Check that the device was added to the registry
    assert mock_instrument.load.called
    assert "Loading device file" in caplog.text


def test_make_devices_with_custom_path(
    mock_registry: Registry,
    mock_config: None,
    mock_namespace: None,
    mock_instrument: None,
    mock_run_blocking_function: None,
    tmp_path: pathlib.Path,
) -> None:
    """Test make_devices with custom path."""
    # Create a custom path and device file
    custom_path = tmp_path / "custom_configs"
    custom_path.mkdir()
    device_file = custom_path / "custom_devices.yml"
    device_file.write_text("""
    ophyd.sim.SynGauss:
      - name: custom_device
        center: 0
        sigma: 1
        noise: 0.1
    """)

    # Mock the config path resolution
    mock_instrument.load.return_value = None

    # Run make_devices with custom path
    list(make_devices(file=str(device_file.name), path=str(custom_path)))

    # Check that the device was loaded
    assert mock_instrument.load.called
    assert str(device_file) in str(mock_instrument.load.call_args[0])


def test_make_devices_clear_option(
    mock_registry: Registry,
    mock_config: None,
    mock_namespace: None,
    mock_instrument: None,
    mock_run_blocking_function: None,
    tmp_path: pathlib.Path,
) -> None:
    """Test make_devices clear option."""
    # Create a test device file
    configs_path = tmp_path / "configs"
    configs_path.mkdir()
    test_file = configs_path / "test_devices.yml"
    test_file.write_text("""
    ophyd.sim.SynGauss:
      - name: test_device
        center: 0
        sigma: 1
        noise: 0.1
    """)

    # Mock the config path resolution
    mock_instrument.load.return_value = None

    # First run with clear=True
    list(make_devices(file=str(test_file.name), path=str(configs_path), clear=True))
    assert mock_instrument.load.called

    # Reset the mock for the second call
    mock_instrument.load.reset_mock()

    # Second run with clear=True
    list(make_devices(file=str(test_file.name), path=str(configs_path), clear=True))
    assert mock_instrument.load.called


def test_make_devices_invalid_file(
    mock_registry: Registry,
    mock_config: None,
    mock_namespace: None,
    mock_instrument: None,
    mock_run_blocking_function: None,
    caplog: LogCaptureFixture,
) -> None:
    """Test make_devices with invalid file path."""
    caplog.set_level(logging.ERROR)

    # Run with non-existent file
    list(make_devices(file="nonexistent.yml"))

    # Check error message
    assert "Device file not found" in caplog.text


def test_make_devices_pause_option(
    mock_registry: Registry,
    mock_config: None,
    mock_namespace: None,
    mock_instrument: None,
    mock_run_blocking_function: None,
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
) -> None:
    """Test make_devices pause option."""
    # Mock sleep to verify it's called
    mock_sleep = mocker.patch("apsbits.core.instrument_init.bps.sleep")
    mock_sleep.side_effect = lambda x: iter([None])  # Make it a generator

    # Create a test device file
    configs_path = tmp_path / "configs"
    configs_path.mkdir()
    test_file = configs_path / "test_devices.yml"
    test_file.write_text("""
    ophyd.sim.SynGauss:
      - name: test_device
        center: 0
        sigma: 1
        noise: 0.1
    """)

    # Mock the config path resolution
    mock_instrument.load.return_value = None

    # Run with custom pause
    list(make_devices(file=str(test_file.name), path=str(configs_path), pause=2.5))

    # Verify sleep was called with correct duration
    mock_sleep.assert_called_once_with(2.5)
