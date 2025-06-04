"""
Setup all configured ophyd items for the baseline stream.

.. autosummary::
    ~setup_baseline_stream
"""

import logging

import bluesky
import guarneri

from apsbits.utils.config_loaders import get_config

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


def setup_baseline_stream(
    sd: bluesky.SupplementalData,
    oregistry: guarneri.Instrument,
    connect: bool = False,
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
    oregistry guarneri.Instrument :
        Registry of ophyd objects.
    connect bool :
        When True (default: False), will wait for connection for all marked
        devices.  A warning will be logged for any devices which do not
        connect.

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

    iconfig = get_config()
    baseline_config = iconfig.get("BASELINE_LABEL")
    if baseline_config is None:
        logger.info("No baseline configuration found in iconfig.yml file.")
        return

    if not baseline_config.get("ENABLE", False):
        logger.info("Baseline stream is disabled in iconfig.yml file.")
        return

    candidates = oregistry.findall("baseline", allow_none=True)
    if candidates is None:
        logger.info("No baseline objects found in oregistry.")
        return

    if connect:
        # Wait for all objects in parallel.
        for item in candidates:
            try:
                item.wait_for_connection()
            except TimeoutError:
                pass  # Check for connection below.

        troubled = [item for item in candidates if not item.connected]
        for item in troubled:
            logger.warning("Could not connect baseline object: %s", item)
            candidates.remove(item)
            oregistry.pop(item)

    try:
        logger.info("Adding marked objects to 'baseline' stream.")
        sd.baseline.extend(candidates)
    except Exception as excuse:
        logger.warning(
            "Problem extending 'baseline' stream: %s",
            excuse,
        )
