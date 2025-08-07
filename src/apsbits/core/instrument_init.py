"""
Make devices from YAML files
=============================

Construct ophyd-style devices from simple specifications in YAML files.

.. autosummary::
    :nosignatures:

    ~make_devices
    ~Instrument
"""

import asyncio
import logging
import pathlib
import sys
import time

import guarneri
import yaml
from ophyd_async.core import NotConnected

from apsbits.utils.config_loaders import get_config

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

MAIN_NAMESPACE = "__main__"


def make_devices(
    *,
    pause: float = 1,
    clear: bool = True,
    file: str,
    path: str | pathlib.Path | None = None,
):
    """
    (plan stub) Create the ophyd-style controls for this instrument.

    EXAMPLE::

        RE(make_devices(file="custom_devices.yml"))  #Use custom devices file
        RE(make_devices(path="custom_device_path",
                        file="custom_devices.yml")) #Use custom path to find device file

    PARAMETERS

    pause : float
        Wait 'pause' seconds (default: 1) for slow objects to connect.
    clear : bool
        Clear 'oregistry' first if True (the default).
    file : str | pathlib.Path | None
        Optional path to a custom YAML/TOML file containing device configurations.
        If provided, this file will be used instead of the default iconfig.yml.
        If None (default), uses the standard iconfig.yml configuration.

    path: str | pathlib.Path | None
    """

    logger.debug("(Re)Loading local control objects.")

    if file is None:
        logger.error("No custom device file provided.")
        return

    if path is None:
        iconfig = get_config()
        instrument_path = pathlib.Path(iconfig.get("INSTRUMENT_PATH")).parent
        configs_path = instrument_path / "configs"
        logger.info(
            f"No custom path provided.\n\nUsing default configs path: {configs_path}"
        )

    else:
        logger.info(f"Using custom path for device files: {path}")
        configs_path = pathlib.Path(path)

    if clear:
        main_namespace = sys.modules[MAIN_NAMESPACE]

        # Clear the oregistry and remove any devices registered previously.
        for dev_name in oregistry.device_names:
            # Remove from __main__ namespace any devices registered previously.
            if hasattr(main_namespace, dev_name):
                logger.info("Removing %r from %r", dev_name, MAIN_NAMESPACE)

                delattr(main_namespace, dev_name)

        oregistry.clear()

    logger.debug("Loading device files: %r", file)

    # Load each device file
    device_path = configs_path / file
    if not device_path.exists():
        logger.error("Device file not found: %s", device_path)

    else:
        logger.info("Loading device file: %s", device_path)
        try:
            asyncio.run(namespace_loader(yaml_device_file=device_path, main=True))
        except Exception as e:
            logger.error("Error loading device file %s: %s", device_path, str(e))

    if pause > 0:
        logger.debug(
            "Waiting %s seconds for slow objects to connect.",
            pause,
        )
        time.sleep(pause)


async def namespace_loader(yaml_device_file, main=True):
    """
    Load our ophyd-style controls as described in a YAML file into the main namespace.

    PARAMETERS

    yaml_device_file : str or pathlib.Path
        YAML file describing ophyd-style controls to be created.
    main : bool
        If ``True`` add these devices to the ``__main__`` namespace.

    """
    logger.debug("Devices file %r.", str(yaml_device_file))
    t0 = time.time()

    current_devices = oregistry.device_names

    instrument.load(yaml_device_file)

    try:
        await instrument.connect()
    except NotConnected as exc:
        logger.exception(exc)

    logger.info("Devices loaded in %.3f s.", time.time() - t0)
    if main:
        main_namespace = sys.modules[MAIN_NAMESPACE]
        for label in sorted(oregistry.device_names):
            if label in current_devices:
                continue
            logger.info("Adding ophyd device %r to main namespace", label)
            setattr(main_namespace, label, oregistry[label])


class Instrument(guarneri.Instrument):
    """Custom YAML loader for guarneri."""

    def parse_yaml_file(self, config_file: pathlib.Path | str) -> list[dict]:
        """Read device configurations from YAML format file."""
        if isinstance(config_file, str):
            config_file = pathlib.Path(config_file)

        def yaml_parser(creator, specs):
            if creator not in self.device_classes:
                try:
                    self.device_classes[creator] = dynamic_import(creator)
                except ImportError as e:
                    logger.error(
                        "Failed to import device creator '%s': %s", creator, str(e)
                    )
                    raise
                except AttributeError as e:
                    logger.error(
                        "Device creator '%s' not found in module: %s", creator, str(e)
                    )
                    raise
            entries = [
                {
                    "device_class": creator,
                    "args": (),  # ALL specs are kwargs!
                    "kwargs": table,
                }
                for table in specs
            ]
            return entries

        try:
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            logger.error("Device configuration file not found: %s", config_file)
            raise
        except PermissionError:
            logger.error("Permission denied reading device file: %s", config_file)
            raise
        except yaml.YAMLError as e:
            logger.error(
                "YAML parsing error in device file %s: %s", config_file, str(e)
            )
            raise

        if not isinstance(config_data, dict):
            logger.error(
                "Invalid device file format in %s: expected dictionary, got %s",
                config_file,
                type(config_data).__name__,
            )
            raise ValueError(f"Invalid device file format in {config_file}")

        try:
            devices = [
                device
                # parse the file using already loaded config data
                for k, v in config_data.items()
                # each support type (class, factory, function, ...)
                for device in yaml_parser(k, v)
            ]
        except Exception as e:
            logger.error(
                "Error parsing device specifications in %s: %s", config_file, str(e)
            )
            raise
        return devices


def dynamic_import(full_path: str) -> type:
    """
    Import the object given its import path as text.

    Motivated by specification of class names for plugins
    when using ``apstools.devices.ad_creator()``.

    EXAMPLES::

        obj = dynamic_import("ophyd.EpicsMotor")
        m1 = obj("gp:m1", name="m1")

        IocStats = dynamic_import("instrument.devices.ioc_stats.IocInfoDevice")
        gp_stats = IocStats("gp:", name="gp_stats")
    """
    from importlib import import_module

    import_object = None

    if "." not in full_path:
        # fmt: off
        raise ValueError(
            "Must use a dotted path, no local imports."
            f" Received: {full_path!r}"
        )
        # fmt: on

    if full_path.startswith("."):
        # fmt: off
        raise ValueError(
            "Must use absolute path, no relative imports."
            f" Received: {full_path!r}"
        )
        # fmt: on

    module_name, object_name = full_path.rsplit(".", 1)
    module_object = import_module(module_name)
    import_object = getattr(module_object, object_name)

    return import_object


instrument = Instrument({})  # singleton
oregistry = instrument.devices
"""Registry of all ophyd-style Devices and Signals."""
