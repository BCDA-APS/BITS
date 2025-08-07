"""
Databroker catalog
==================

.. autosummary::
    ~init_catalog
"""

import logging
from typing import Any

import databroker

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

TEMPORARY_CATALOG_NAME = "temporalcat"


def init_catalog(iconfig: dict[str, Any]) -> Any:
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
        logger.info("Successfully connected to databroker catalog: %s", catalog_name)
    except KeyError:
        logger.warning(
            "Databroker catalog '%s' not found, using temporary catalog", catalog_name
        )
        try:
            _cat = databroker.temp().v2
        except Exception as e:
            logger.error("Failed to create temporary databroker catalog: %s", str(e))
            raise
    except Exception as e:
        logger.error(
            "Unexpected error connecting to databroker catalog '%s': %s (type: %s)",
            catalog_name,
            str(e),
            type(e).__name__,
        )
        logger.warning("Falling back to temporary catalog")
        try:
            _cat = databroker.temp().v2
        except Exception as temp_error:
            logger.error(
                "Failed to create fallback temporary catalog: %s", str(temp_error)
            )
            raise

    logger.info("Databroker catalog initialized: %s", _cat.name)
    return _cat
