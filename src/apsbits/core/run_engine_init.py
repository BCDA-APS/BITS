"""
Setup and initialize the Bluesky RunEngine.
===========================================

This module provides the function init_RE to create and configure a
Bluesky RunEngine with metadata storage, subscriptions, and various
settings based on a configuration dictionary.

.. autosummary::
    init_RE
    setup_baseline_stream
"""

import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

import bluesky
import guarneri
import ophyd
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


def setup_baseline_stream(
    sd: bluesky.SupplementalData,
    iconfig: dict[str, ophyd.OphydObject],
    oregistry: guarneri.Instrument,
) -> None:
    """
    Add ophyd objects with 'baseline' label to baseline stream.

    Call :func:`~apsbits.core.run_engine_init.setup_baseline_stream(sd, iconfig,
    oregistry)` in the startup code after all ophyd objects have been created.
    It is safe to call this function even when no objects are labeled; there are
    checks that return early if not configured.  This function should part of
    every startup.

    To include any ophyd object created after startup has completed, append it
    to the 'sd.baseline' list, such as: ``sd.baseline.append(new_ophyd_object)``

    Parameters:

    sd bluesky.SupplementalData :
        Object which contains the list of baseline objects to be published.
    iconfig (Dict[str, Any]) :
        Configuration dictionary with keys.  See
        :func:`~apsbits.core.run_engine_init.init_RE()` for more details.
    oregistry guarneri.Instrument :
        Registry of ophyd objects.

    .. rubric:: Background

    The baseline stream records the values of ophyd objects:

    * at the start and end of a run
    * that are not intended as detectors (or other readables) for the primary stream
    * that may not be suitable to record in the run's metadata
    * for use by post-acquisition processing

    To enable the assignment of an ophyd object to the baseline stream, add
    "baseline" to its labels kwarg list. On startup, after all the objects have
    been created, use the oregistry to find all the objects with the "baseline"
    label and append each to the sd.baseline list.

    To learn more about baseline readings and the baseline stream in bluesky, see:

    * https://blueskyproject.io/bluesky/main/plans.html#supplemental-data
    * https://blueskyproject.io/bluesky/main/metadata.html#recording-metadata
    * https://nsls-ii.github.io/bluesky/tutorial.html#baseline-readings-and-other-supplemental-data
    """
    baseline_config = iconfig.get("BASELINE_LABEL")
    if baseline_config is None:
        return  # No baseline configuration found in iconfig.yml file.

    if not baseline_config.get("ENABLE", False):
        return  # baseline stream is not enabled in iconfig.yml file.

    label = baseline_config.get("LABEL", "baseline")
    logger.info(
        "Adding objects with %r label to 'baseline' stream.",
        label,
    )

    try:
        sd.baseline.extend(oregistry.findall(label, allow_none=True) or [])
    except Exception:
        logger.warning(
            "Could not add objects with %r label to 'baseline' stream",
            label,
        )
