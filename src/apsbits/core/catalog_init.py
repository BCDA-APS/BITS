"""
Databroker catalog, provides ``cat``
====================================

.. autosummary::
    ~cat
"""

import logging

import databroker

from apsbits.utils.config_loaders import iconfig

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

TEMPORARY_CATALOG_NAME = "temp"


def init_catalog():
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


# Initialize cat at the module level with the iconfig
cat = init_catalog()
