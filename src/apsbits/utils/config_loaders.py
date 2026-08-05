"""
Configuration management for the instrument.

This module serves as the single source of truth for instrument configuration.
It loads and validates the configuration from the iconfig.yml file and provides
access to the configuration throughout the application.
"""

import logging
import pathlib
import tomllib
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

# Global configuration instance
_iconfig: dict[str, Any] = {}


def load_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """
    Load configuration from a YAML or TOML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        The loaded configuration dictionary.

    Raises:
        ValueError: If config_path is None or if the file extension is not supported.
        FileNotFoundError: If the configuration file does not exist.
    """
    global _iconfig

    if config_path is None:
        raise ValueError("config_path must be provided")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    suffix = config_path.suffix.lower()
    if suffix == ".yml":
        config = load_config_yaml(config_path)
    elif suffix == ".toml":
        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            logger.error(
                "TOML parsing error in configuration file %s: %s", config_path, str(e)
            )
            raise
    else:
        raise ValueError(
            f"Unsupported configuration file format: {config_path.suffix}. "
            "Supported formats: .yml, .toml"
        )

    # Replace global state (not merge) so keys from a previous load don't leak.
    _iconfig.clear()
    _iconfig.update(config)

    _iconfig["ICONFIG_PATH"] = str(config_path)
    _iconfig["INSTRUMENT_PATH"] = str(config_path.parent)
    _iconfig["INSTRUMENT_FOLDER"] = str(config_path.parent.name)

    return _iconfig


def get_config() -> Mapping[str, Any]:
    """
    Get the current configuration.

    Returns a read-only view of the global configuration; use ``load_config`` or
    ``update_config`` to modify it.

    Returns:
        A read-only view of the current configuration dictionary.
    """
    return MappingProxyType(_iconfig)


def update_config(updates: dict[str, Any]) -> None:
    """
    Update the current configuration.

    Args:
        updates: Dictionary of configuration updates.
    """
    _iconfig.update(updates)


def reset_config() -> None:
    """Clear the global configuration (primarily for test isolation)."""
    _iconfig.clear()


def load_config_yaml(config_obj) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        The loaded configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """

    if config_obj is None:
        raise ValueError("config_path must be provided")

    try:
        # If it's a path, open it first
        if isinstance(config_obj, (str, pathlib.Path)):
            config_path = pathlib.Path(config_obj)
            if not config_path.exists():
                raise FileNotFoundError(
                    f"YAML configuration file not found: {config_path}"
                )
            with open(config_path, "r") as f:
                content = f.read()
        # Otherwise assume it's a file-like object
        else:
            content = config_obj.read()

        if not content.strip():
            logger.warning("YAML configuration is empty")
            return {}

        iconfig = yaml.safe_load(content)
        return iconfig if iconfig is not None else {}
    except FileNotFoundError:
        logger.error("YAML configuration file not found: %s", config_obj)
        raise
    except PermissionError:
        logger.error("Permission denied reading YAML configuration: %s", config_obj)
        raise
    except yaml.YAMLError as e:
        logger.error("YAML parsing error in configuration: %s", str(e))
        raise
    except Exception as e:
        logger.error(
            "Unexpected error loading YAML configuration: %s (type: %s)",
            str(e),
            type(e).__name__,
        )
        raise
