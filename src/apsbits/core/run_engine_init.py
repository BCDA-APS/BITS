"""
Setup and initialize the Bluesky RunEngine.
===========================================

This module provides the function init_RE to create and configure a
Bluesky RunEngine with metadata storage, subscriptions, and various
settings based on a configuration dictionary.

.. autosummary::
    ~init_RE
"""

import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

import bluesky
from bluesky.utils import ProgressBarManager

from apsbits.utils.controls_setup import connect_scan_id_pv
from apsbits.utils.controls_setup import set_control_layer
from apsbits.utils.controls_setup import set_timeouts
from apsbits.utils.metadata import get_md_path
from apsbits.utils.metadata import re_metadata
from apsbits.utils.stored_dict import StoredDict

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


def init_RE(
    iconfig: Dict[str, Any],
    bec_instance: Optional[Any] = None,
    cat_instance: Optional[Any] = None,
    **kwargs: Any,
) -> Tuple[bluesky.RunEngine, bluesky.SupplementalData]:
    """
    Initialize and configure a Bluesky RunEngine instance.

    This function creates a Bluesky RunEngine, sets up metadata storage,
    subscriptions, and various preprocessors based on the provided
    configuration dictionary. It configures the control layer and timeouts,
    attaches supplemental data for baselines and monitors, and optionally
    adds a progress bar and metadata updates from a catalog or BestEffortCallback.

    Parameters:
        iconfig (Dict[str, Any]): Configuration dictionary with keys including:
            - "RUN_ENGINE": A dict containing RunEngine-specific settings.
            - "DEFAULT_METADATA": (Optional) Default metadata for the RunEngine.
            - "USE_PROGRESS_BAR": (Optional) Boolean flag to enable the progress bar.
            - "OPHYD": A dict for control layer settings
            (e.g., "CONTROL_LAYER" and "TIMEOUTS").
        bec_instance (Optional[Any]): Instance of BestEffortCallback for subscribing
            to the RunEngine. Defaults to None.
        cat_instance (Optional[Any]): Instance of a databroker catalog for subscribing
            to the RunEngine. Defaults to None.
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
            else:
                RE.md = StoredDict(MD_PATH)
        except Exception as error:
            print(
                "\n"
                f"Could not create {handler_name} for RE metadata. Continuing "
                f"without saving metadata to disk. {error=}\n"
            )
            logger.warning("%s('%s') error:%s", handler_name, MD_PATH, error)

    if cat_instance is not None:
        RE.md.update(re_metadata(iconfig, cat_instance))  # programmatic metadata
        RE.md.update(re_config.get("DEFAULT_METADATA", {}))
        RE.subscribe(cat_instance.v1.insert)
    if bec_instance is not None:
        RE.subscribe(bec_instance)

    scan_id_pv = iconfig.get("RUN_ENGINE", {}).get("SCAN_ID_PV")
    connect_scan_id_pv(RE, pv=scan_id_pv)

    if re_config.get("USE_PROGRESS_BAR", True):
        # Add a progress bar.
        pbar_manager = ProgressBarManager()
        RE.waiting_hook = pbar_manager

    return RE, sd
