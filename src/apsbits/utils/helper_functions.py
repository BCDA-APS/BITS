"""
Generic utility helper functions
================================

.. autosummary::
    ~register_bluesky_magics
    ~running_in_queueserver
    ~debug_python
    ~mpl_setup
    ~is_notebook
"""

import collections.abc
import logging

import matplotlib as mpl
import matplotlib.pyplot as plt
from bluesky.magics import BlueskyMagics
from IPython import get_ipython

from apsbits.utils.config_loaders import get_config

logger = logging.getLogger(__name__)


def register_bluesky_magics() -> None:
    """Register Bluesky IPython magics."""
    try:
        ip = get_ipython()
        if ip is not None:
            ip.register_magics(BlueskyMagics)
            logger.info("Registered Bluesky IPython magics")
    except Exception as e:
        logger.warning("Could not register Bluesky IPython magics: %s", e)


def running_in_queueserver() -> bool:
    """
    Check if we are running in a Bluesky queueserver.

    Returns:
        True if running in a queueserver, False otherwise.
    """
    from bluesky_queueserver import is_re_worker_active

    return is_re_worker_active()


def get_xmode_level() -> str:
    """
    Get the current XMode debug level.

    Returns:
        The current XMode debug level.
    """
    iconfig = get_config()
    xmode_level: str = iconfig.get("XMODE_DEBUG_LEVEL", "Plain")
    return xmode_level


def debug_python(xmode_level: str = "Plain") -> None:
    """
    Enable detailed debugging for Python exceptions in the IPython environment.

    This function adjusts the xmode settings for exception tracebacks based on
    the provided xmode_level argument.

    Args:
        xmode_level (str): The level of detail for exception tracebacks.
                           Defaults to "Minimal".
    """
    ipython = get_ipython()
    if ipython is not None:
        current_xmode_level: str = get_xmode_level()
        ipython.run_line_magic("xmode", current_xmode_level)
        print("\nEnd of IPython settings\n")
        logger.bsdev("xmode exception level: '%s'", current_xmode_level)


def is_notebook() -> bool:
    """
    Detect if the current environment is a Jupyter Notebook.

    Returns:
        bool: True if running in a notebook (Jupyter notebook or qtconsole),
        False otherwise.
    """
    try:
        shell: str = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type
    except NameError:
        return False  # Standard Python interpreter


def mpl_setup() -> None:
    """
    Configure the Matplotlib backend based on the current environment.

    For non-queueserver and non-notebook environments, attempts to use the 'qtAgg'
      backend.
    If 'qtAgg' is not available due to missing dependencies, falls back to the 'Agg'
      backend.

    Returns:
        None
    """
    if not running_in_queueserver():
        if not is_notebook():
            try:
                mpl.use("qtAgg")
                plt.ion()
                logger.bsdev("Using qtAgg backend for matplotlib.")
            except Exception as exc:
                logger.error(
                    "qtAgg backend is not available, falling back to Agg backend. \
                    Error: %s",
                    exc,
                )
                mpl.use("Agg")


def dynamic_import(full_path: str) -> collections.abc.Callable:
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
