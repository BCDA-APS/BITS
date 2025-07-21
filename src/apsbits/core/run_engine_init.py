"""
Setup the Bluesky RunEngine, provides ``RE`` and ``sd``.
========================================================

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
) -> Tuple[Any, Any]:
    """
    Initialize and configure a bluesky RunEngine (RE) instance.

    This function sets up the RunEngine with metadata storage, subscriptions,
    preprocessors, and other configurations based on the provided input
    parameters and configuration dictionary.

    Args:
        iconfig (dict): Configuration dictionary containing settings for the
            RunEngine. Expected keys include:
            - "RUN_ENGINE": A dictionary with RunEngine-specific settings.
            - "MD_STORAGE_HANDLER": (Optional) The handler for metadata storage
              (default is "StoredDict").
            - "DEFAULT_METADATA": (Optional) Default metadata to be added to
              the RunEngine.
            - "USE_PROGRESS_BAR": (Optional) Boolean to enable/disable the
              progress bar (default is True).
        bec_instance (object, optional): An instance of BestEffortCallback (BEC)
            for subscribing to the RunEngine. Defaults to `bec`.
        cat_instance (object, optional): An instance of a databroker catalog
            for subscribing to the RunEngine. Defaults to `cat`.

    Returns:
        tuple: A tuple containing the configured RunEngine instance and the
               SupplementalData instance.

    Raises:
        Exception: If there is an error creating the metadata storage handler.

    Notes:
        - The function ensures that the RE.md dictionary is saved/restored
          using the specified metadata storage handler.
        - Subscriptions to the catalog and BEC are added if the respective
          instances are provided.
        - Additional configurations such as control layer setup, timeouts,
          and progress bar are applied.
    """
    re_config = iconfig.get("RUN_ENGINE", {})

    # Steps which MUST happen before ANY EpicsSignalBase (or subclass) is created.
    control_layer = iconfig.get("OPHYD", {}).get("CONTROL_LAYER", "PyEpics")
    set_control_layer(control_layer=control_layer)
    set_timeouts(timeouts=iconfig.get("OPHYD", {}).get("TIMEOUTS", {}))

    RE = bluesky.RunEngine()
    """The bluesky RunEngine object."""

    sd = bluesky.SupplementalData()
    """Baselines & monitors for ``RE``."""
    RE.preprocessors.append(sd)

    MD_PATH = get_md_path(iconfig)
    # Save/restore RE.md dictionary, in this precise order.
    if MD_PATH is not None:
        handler_name = re_config.get("MD_STORAGE_HANDLER", "StoredDict")
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
            else:
                logger.error(
                    "Unknown metadata storage handler: %s. "
                    "Supported handlers: PersistentDict, StoredDict",
                    handler_name,
                )
                raise ValueError(f"Unknown metadata storage handler: {handler_name}")
        except PermissionError as error:
            logger.error(
                "Permission denied creating metadata storage at %s: %s",
                MD_PATH,
                error,
            )
            print(
                f"\nPermission denied creating {handler_name} for RE metadata "
                f"at {MD_PATH}. Continuing without saving metadata to disk. {error}\n"
            )
        except ImportError as error:
            logger.error(
                "Failed to import metadata storage handler %s: %s",
                handler_name,
                error,
            )
            print(
                f"\nFailed to import {handler_name} for RE metadata."
                f" Continuing without saving metadata to disk. {error}\n"
            )
        except Exception as error:
            logger.error(
                "Unexpected error creating %s at %s: %s (type: %s)",
                handler_name,
                MD_PATH,
                error,
                type(error).__name__,
            )
            print(
                f"\nCould not create {handler_name} for RE metadata at {MD_PATH}."
                f" Continuing without saving metadata to disk. {error}\n"
            )

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
