"""
Setup and initialize the Bluesky RunEngine.
===========================================

This module provides the function init_RE to create and configure a
Bluesky RunEngine with metadata storage, subscriptions, and various
settings based on a configuration dictionary.

.. autosummary::
    ~init_RE
"""

import collections
import logging
from typing import Any
from typing import Optional

import bluesky
import databroker._drivers.mongo_normalized
import databroker._drivers.msgpack
import tiled
from bluesky.utils import ProgressBarManager
from bluesky_tiled_plugins import TiledWriter

from apsbits.utils.controls_setup import connect_scan_id_pv
from apsbits.utils.controls_setup import set_control_layer
from apsbits.utils.controls_setup import set_timeouts
from apsbits.utils.metadata import get_md_path
from apsbits.utils.metadata import re_metadata
from apsbits.utils.stored_dict import StoredDict

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


def init_RE(
    iconfig: collections.abc.Mapping[str, Any],
    subscribers: Optional[list[Any]] = None,
    **kwargs: Any,
) -> tuple[bluesky.RunEngine, bluesky.SupplementalData]:
    """
    Initialize and configure a Bluesky RunEngine instance.

    This function creates a Bluesky RunEngine, sets up metadata storage,
    subscriptions, and various preprocessors based on the provided
    configuration dictionary. It configures the control layer and timeouts,
    attaches supplemental data for baselines and monitors, and optionally
    adds a progress bar and metadata updates from a catalog or BestEffortCallback.

    Parameters:
        iconfig (collections.abc.Mapping[str, Any]): Configuration dictionary with keys:
            - "RUN_ENGINE": A dict containing RunEngine-specific settings.
            - "DEFAULT_METADATA": (Optional) Default metadata for the RunEngine.
            - "USE_PROGRESS_BAR": (Optional) Boolean flag to enable the progress bar.
            - "OPHYD": A dict for control layer settings
            (other keys are possible, such as: "CONTROL_LAYER", "TIMEOUTS", etc...).

        subscribers : Optional[list[Any]], default=None
            List of callback instances to subscribe to the RunEngine.
            The function auto-detects the type of each instance and subscribes
            it appropriately:
            - Tiled clients are wrapped in TiledWriter before subscription
            - Databroker catalogs subscribe via their v1.insert method
            - BestEffortCallback and other callbacks subscribe according to their
              documentation.
            Order in the list does not matter.

        **kwargs: Additional keyword arguments passed to the RunEngine constructor.
            For example, run_returns_result=True.

    Returns:
        Tuple[bluesky.RunEngine, bluesky.SupplementalData]: A tuple containing the
        configured RunEngine instance and its associated SupplementalData.

    Notes:
        The function attempts to set up persistent metadata storage in the RE.md attr.
        If an error occurs during the creation of the metadata storage handler,
        the error is logged and the function proceeds without persistent metadata.
        Subscriptions are added for the catalog and BestEffortCallback if provided, and
        additional configurations such as control layer, timeouts, and progress bar
        integration are applied.
    """
    re_config = iconfig.get("RUN_ENGINE", {})

    # Steps that must occur before any EpicsSignalBase (or subclass) is created.
    control_layer = iconfig.get("OPHYD", {}).get("CONTROL_LAYER", "PyEpics")
    set_control_layer(control_layer=control_layer)
    set_timeouts(timeouts=iconfig.get("OPHYD", {}).get("TIMEOUTS", {}))

    RE = bluesky.RunEngine(**kwargs)
    """The Bluesky RunEngine object."""

    sd = bluesky.SupplementalData()
    """Supplemental data providing baselines and monitors for the RunEngine."""
    RE.preprocessors.append(sd)

    MD_PATH = get_md_path(iconfig)
    # Save/restore RE.md dictionary in the specified order.
    if MD_PATH is not None:
        handler_name = StoredDict
        logger.debug(
            "Selected %r to store 'RE.md' dictionary in %s.",
            handler_name,
            MD_PATH,
        )
        try:
            if handler_name == "PersistentDict":
                RE.md = bluesky.utils.PersistentDict(MD_PATH)
            elif handler_name == "StoredDict":
                RE.md = StoredDict(MD_PATH)
        except Exception as error:
            print(
                "\n"
                f"Could not create {handler_name} for RE metadata. Continuing "
                f"without saving metadata to disk. {error=}\n"
            )

    RE.md.update(re_config.get("DEFAULT_METADATA", {}))
    RE.md.update(re_metadata(iconfig))  # programmatic metadata

    if subscribers:
        for instance in subscribers:
            if instance is None:
                continue

            # Check if it's a tiled client
            if isinstance(instance, tiled.client.container.Container):
                try:
                    tiled_writer = TiledWriter(instance, batch_size=1)
                    RE.subscribe(tiled_writer)
                except Exception:
                    logger.exception(
                        "Failed to subscribe TiledWriter for tiled client %r (type=%s)",
                        instance,
                        type(instance).__name__,
                    )
                    raise

            # Check if it's a databroker catalog
            elif isinstance(
                instance,
                (
                    databroker._drivers.msgpack.BlueskyMsgpackCatalog,
                    databroker._drivers.mongo_normalized.BlueskyMongoCatalog,
                ),
            ):
                try:
                    RE.subscribe(instance.v1.insert)
                except Exception:
                    logger.exception(
                        "Failed to subscribe databroker catalog insert for %r "
                        "(type=%s)",
                        instance,
                        type(instance).__name__,
                    )
                    raise

            # Default: subscribe directly (handles BEC and other callbacks)
            else:
                try:
                    RE.subscribe(instance)
                except Exception:
                    logger.exception(
                        "Failed to subscribe callback %r (type=%s)",
                        instance,
                        type(instance).__name__,
                    )
                    raise

    scan_id_pv = iconfig.get("RUN_ENGINE", {}).get("SCAN_ID_PV")
    connect_scan_id_pv(RE, pv=scan_id_pv)

    if re_config.get("USE_PROGRESS_BAR", True):
        # Add a progress bar.
        pbar_manager = ProgressBarManager()
        RE.waiting_hook = pbar_manager

    return RE, sd
