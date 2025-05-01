"""
BestEffortCallback: simple real-time visualizations, provides ``bec``.
======================================================================

.. autosummary::
    ~init_bec_peaks
"""

import logging

from bluesky.callbacks.best_effort import BestEffortCallback

from apsbits.utils.helper_functions import running_in_queueserver

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


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
