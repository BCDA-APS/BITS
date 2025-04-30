"""
Initialize Bluesky functionality for your instrument this includes: Databroker catalog,
BestEffortCallback: simple real-time visualizations, and Setup and initialization of the
Bluesky RunEngine.
==================

.. autosummary::
    ~init_catalog
    ~init_bec_peaks
    ~init_RE

"""

import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

import bluesky
import databroker
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import ProgressBarManager

from apsbits.utils.controls_setup import connect_scan_id_pv
from apsbits.utils.controls_setup import set_control_layer
from apsbits.utils.controls_setup import set_timeouts
from apsbits.utils.helper_functions import running_in_queueserver
from apsbits.utils.metadata import get_md_path
from apsbits.utils.metadata import re_metadata
from apsbits.utils.stored_dict import StoredDict

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

TEMPORARY_CATALOG_NAME = "temporalcat"


def init_bec_peaks(iconfig):
    """
    Create and configure a BestEffortCallback object based on the provided iconfig.

    Parameters:
        iconfig (dict): Configuration dictionary.

    Returns:
        tuple: A tuple containing the configured BestEffortCallback object (bec)
               and its peaks dictionary.
    """

    bec = BestEffortCallback()
    """BestEffortCallback object, creates live tables and plots."""

    bec_config = iconfig.get("BEC", {})

    if not bec_config.get("BASELINE", True):
        bec.disable_baseline()

    if not bec_config.get("HEADING", True):
        bec.disable_heading()

    if not bec_config.get("PLOTS", True) or running_in_queueserver():
        bec.disable_plots()

    if not bec_config.get("TABLE", True):
        bec.disable_table()

    peaks = bec.peaks
    """Dictionary with statistical analysis of LivePlots."""

    return bec, peaks


def init_catalog(iconfig):
    """
    Initialize the Databroker catalog using the provided iconfig.

    Parameters:
        iconfig: Configuration object to retrieve catalog name.

    Returns:
        Databroker catalog object.
    """
    catalog_name = iconfig.get("DATABROKER_CATALOG", TEMPORARY_CATALOG_NAME)
    try:
        _cat = databroker.catalog[catalog_name].v2
    except KeyError:
        _cat = databroker.temp().v2

    logger.info("Databroker catalog name: %s", _cat.name)
    return _cat


def init_RE(
    iconfig: Dict[str, Any],
    bec_instance: Optional[Any] = None,
    cat_instance: Optional[Any] = None,
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

    RE = bluesky.RunEngine()
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
    RE.preprocessors.append(sd)

    scan_id_pv = iconfig.get("RUN_ENGINE", {}).get("SCAN_ID_PV")
    connect_scan_id_pv(RE, pv=scan_id_pv)

    if re_config.get("USE_PROGRESS_BAR", True):
        # Add a progress bar.
        pbar_manager = ProgressBarManager()
        RE.waiting_hook = pbar_manager

    return RE, sd
