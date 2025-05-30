"""
Test the configuration management module.
"""

import pathlib
import tempfile
from typing import TYPE_CHECKING

import pytest
import tomli_w
import yaml

from apsbits.utils.config_loaders import load_config

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
