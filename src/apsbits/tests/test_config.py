"""
Test the configuration management module.
"""

import pathlib
import tempfile
from typing import TYPE_CHECKING

import pytest
import tomli_w
import yaml

from apsbits.utils.config_loaders import get_config
from apsbits.utils.config_loaders import load_config
from apsbits.utils.config_loaders import reset_config
from apsbits.utils.config_loaders import update_config

if TYPE_CHECKING:
    pass

ICONFIG_VERSION_NOW: str = "2.0.1"


@pytest.fixture
def yml_config_file():
    """Create a temporary YAML configuration file."""
    config = {
        "ICONFIG_VERSION": ICONFIG_VERSION_NOW,
        "DATABROKER_CATALOG": "temp",
        "test_key": "test_value",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(config, f)
        path = pathlib.Path(f.name)

    yield path
    path.unlink()


@pytest.fixture
def toml_config_file():
    """Create a temporary TOML configuration file."""
    config = {
        "ICONFIG_VERSION": ICONFIG_VERSION_NOW,
        "DATABROKER_CATALOG": "temp",
        "test_key": "test_value",
    }

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(tomli_w.dumps(config).encode("utf-8"))
        path = pathlib.Path(f.name)

    yield path
    path.unlink()


def test_load_yaml_config(yml_config_file: pathlib.Path) -> None:
    """
    Test loading configuration from a YAML file.

    Args:
        yml_config_file: Path to the temporary YAML configuration file.
    """
    config = load_config(yml_config_file)
    assert config["ICONFIG_VERSION"] == ICONFIG_VERSION_NOW
    assert config["DATABROKER_CATALOG"] == "temp"
    assert config["test_key"] == "test_value"


def test_load_toml_config(toml_config_file: pathlib.Path) -> None:
    """
    Test loading configuration from a TOML file.

    Args:
        toml_config_file: Path to the temporary TOML configuration file.
    """
    config = load_config(toml_config_file)
    assert config["ICONFIG_VERSION"] == ICONFIG_VERSION_NOW
    assert config["DATABROKER_CATALOG"] == "temp"
    assert config["test_key"] == "test_value"


def test_load_config_none_path() -> None:
    """Test loading configuration with None path."""
    with pytest.raises(ValueError, match="config_path must be provided"):
        load_config(None)


def test_load_config_invalid_file() -> None:
    """Test loading configuration from a non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_config(pathlib.Path("nonexistent.yml"))


def test_load_config_invalid_extension() -> None:
    """Test loading configuration with an unsupported file extension."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        path = pathlib.Path(f.name)

    try:
        with pytest.raises(ValueError, match="Unsupported configuration file format"):
            load_config(path)
    finally:
        path.unlink()


def test_load_config_invalid_content() -> None:
    """Test loading configuration with invalid content."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write("invalid: yaml: content:")
        path = pathlib.Path(f.name)

    try:
        with pytest.raises(Exception):  # noqa
            load_config(path)
    finally:
        path.unlink()


def test_load_config_injects_path_keys(yml_config_file: pathlib.Path) -> None:
    """load_config injects ICONFIG_PATH/INSTRUMENT_PATH/INSTRUMENT_FOLDER."""
    config = load_config(yml_config_file)
    assert config["ICONFIG_PATH"] == str(yml_config_file)
    assert config["INSTRUMENT_PATH"] == str(yml_config_file.parent)
    assert config["INSTRUMENT_FOLDER"] == str(yml_config_file.parent.name)


def test_load_config_get_config_round_trip(yml_config_file: pathlib.Path) -> None:
    """get_config returns the values load_config just populated."""
    load_config(yml_config_file)
    config = get_config()
    assert config["ICONFIG_VERSION"] == ICONFIG_VERSION_NOW
    assert config["test_key"] == "test_value"
    assert config["ICONFIG_PATH"] == str(yml_config_file)


def test_get_config_is_read_only(yml_config_file: pathlib.Path) -> None:
    """get_config returns a read-only view; writes must go through the loaders."""
    load_config(yml_config_file)
    with pytest.raises(TypeError):
        get_config()["test_key"] = "mutated"


def test_load_config_replaces_previous_keys(
    yml_config_file: pathlib.Path, toml_config_file: pathlib.Path
) -> None:
    """A second load_config replaces the first load's keys instead of merging."""
    load_config(yml_config_file)
    update_config({"STALE_KEY": "leftover"})
    assert "STALE_KEY" in get_config()

    load_config(toml_config_file)
    assert "STALE_KEY" not in get_config()


def test_reset_config_clears(yml_config_file: pathlib.Path) -> None:
    """reset_config empties the global configuration."""
    load_config(yml_config_file)
    assert len(get_config()) > 0
    reset_config()
    assert len(get_config()) == 0
