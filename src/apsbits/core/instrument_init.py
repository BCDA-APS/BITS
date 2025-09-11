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
import functools
import logging
import pathlib
import sys
import time
from typing import Callable

import guarneri
from ophyd_async.core import NotConnected

from apsbits.utils.config_loaders import get_config

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

MAIN_NAMESPACE = "__main__"

_instrument = None


def make_devices(
    *,
    pause: float = 1,
    clear: bool = True,
    file: str,
    path: str | pathlib.Path | None = None,
    device_manager=None,
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
    # oregistry = instrument.devices
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

    if clear and isinstance(device_manager, guarneri.Instrument):
        main_namespace = sys.modules[MAIN_NAMESPACE]

        # Clear the oregistry and remove any devices registered previously.
        for dev_name in device_manager.devices.device_names:
            # Remove from __main__ namespace any devices registered previously.
            if hasattr(main_namespace, dev_name):
                logger.info("Removing %r from %r", dev_name, MAIN_NAMESPACE)

                delattr(main_namespace, dev_name)

        device_manager.devices.clear()

    logger.debug("Loading device files: %r", file)

    # Load each device file
    device_path = configs_path / file
    if not device_path.exists():
        logger.error("Device file not found: %s", device_path)

    else:
        logger.info("Loading device file: %s", device_path)
        if isinstance(device_manager, guarneri.Instrument):
            try:
                asyncio.run(
                    guarneri_namespace_loader(
                        yaml_device_file=device_path,
                        instrument=device_manager,
                        oregistry=device_manager.devices,
                        main=True,
                    )
                )
            except Exception as e:
                logger.error("Error loading device file %s: %s", device_path, str(e))
        elif device_manager == "happi":
            pass
        elif device_manager is None:
            logger.error("No device_manager provided.")
            return
    if pause > 0:
        logger.debug(
            "Waiting %s seconds for slow objects to connect.",
            pause,
        )
        time.sleep(pause)


async def guarneri_namespace_loader(
    yaml_device_file, instrument=None, oregistry=None, main=True
):
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
    # Convert pathlib.Path to string - this fixes the guarneri bug
    yaml_file_path = str(yaml_device_file)
    instrument.load(yaml_file_path)
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


def set_instrument(instrument):
    """Set the global instrument instance"""
    global _instrument
    _instrument = instrument


def with_registry(func: Callable) -> Callable:
    """
    Decorator that provides access to the instrument's device registry.
    Injects 'oregistry' as the first argument to the decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if _instrument is None:
            raise RuntimeError("Instrument not set. Call set_instrument() first.")
        return func(_instrument.devices, *args, **kwargs)

    return wrapper


def with_devices(*device_names: str):
    """
    Decorator that injects specific devices as keyword arguments.

    Usage:
    @with_devices("sim_det", "sim_motor")
    def my_plan(span=5, **devices):
        sim_det = devices["sim_det"]
        sim_motor = devices["sim_motor"]
        # ... your plan code

    Or with unpacking:
    @with_devices("sim_det", "sim_motor")
    def my_plan(span=5, sim_det=None, sim_motor=None, **kwargs):
        # sim_det and sim_motor are automatically injected
        # ... your plan code
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if _instrument is None:
                raise RuntimeError("Instrument not set. Call set_instrument() first.")

            # Inject devices as keyword arguments
            for device_name in device_names:
                if device_name in _instrument.devices:
                    kwargs[device_name] = _instrument.devices[device_name]
                else:
                    print(f"Warning: Device '{device_name}' not found in registry")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def auto_inject_devices(func: Callable) -> Callable:
    """
    Decorator that automatically injects all devices from the registry
    that match parameter names in the function signature.

    Usage:
    @auto_inject_devices
    def my_plan(span=5, sim_det=None, sim_motor=None):
        # sim_det and sim_motor are automatically injected if they exist in registry
        # ... your plan code
    """
    import inspect

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if _instrument is None:
            raise RuntimeError("Instrument not set. Call set_instrument() first.")

        # Get function signature
        sig = inspect.signature(func)

        # Inject devices that match parameter names
        for param_name in sig.parameters:
            if param_name in _instrument.devices and param_name not in kwargs:
                kwargs[param_name] = _instrument.devices[param_name]

        return func(*args, **kwargs)

    return wrapper
