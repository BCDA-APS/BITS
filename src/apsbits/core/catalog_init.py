"""
Databroker catalog
==================

.. autosummary::
    ~init_catalog
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

# The httpx (via tiled) logger is set too noisy.  Make it quieter.
logging.getLogger("httpx").setLevel(logging.WARNING)


def init_catalog(iconfig: dict[str, Any]) -> Any:
    """
    Setup for a catalog to record bluesky run documents.

    Return only one catalog object, depending on the keys in 'iconfig'.
    The object returned is the first successful match, in this order:

    * tiled catalog: requires TILED_PROFILE_NAME and optional TILED_PATH_NAME
    * databroker catalog: requires DATABROKER_CATALOG
    * temporary databroker catalog: fallback is the above are not successful
    * (TODO) temporary tiled catalog: replaces temporary databroker fallback
    """
    handlers = [  # try these, in order
        _tiled_profile_client,
        _databroker_named_catalog,
        # fallbacks
        _databroker_temporary_catalog,
        # _tiled_temporary_catalog,  # TODO: see below
    ]
    for handler in handlers:
        try:
            cat = handler(iconfig)
            if cat is None:
                continue
            return cat
        except Exception as exinfo:
            logger.error(
                "%s() Failed to create catalog: %s",
                handler.__name__,
                str(exinfo),
            )
    raise RuntimeError("Could not create a catalog for Bluesky run documents.")


def _databroker_named_catalog(iconfig: dict[str, Any]) -> Any:
    """Connect with a named databroker catalog."""
    import databroker

    cat = None
    catalog_name = iconfig.get("DATABROKER_CATALOG")
    if catalog_name is not None:
        cat = databroker.catalog[catalog_name].v2
    logger.debug("%s: cat=%s", type(cat).__name__, str(cat))
    if cat is not None:
        logger.info("Databroker catalog initialized: %s", cat.name)
    return cat


def _databroker_temporary_catalog(iconfig: dict[str, Any]) -> Any:
    """Connect with a temporary databroker catalog."""
    import databroker

    cat = databroker.temp().v2
    logger.debug("%s: cat=%s", type(cat).__name__, str(cat))
    logger.info("Databroker temporary catalog initialized")
    return cat


def _tiled_profile_client(iconfig: dict[str, Any]) -> Any:
    """Connect with a tiled server using a profile."""
    from tiled.client import from_profile

    cat = None
    profile = iconfig.get("TILED_PROFILE_NAME")
    path = iconfig.get("TILED_PATH_NAME")
    if profile is not None:
        client = from_profile(profile)
        cat = client if path is None else client[path]

    logger.debug("%s: cat=%s", type(cat).__name__, str(cat))
    logger.info("Tiled server (catalog) connected, profile=%r, path=%r", profile, path)

    return cat


# To run a temporary tiled server, the SimpleTiledWriter is used. This server
# must remain running after it is created (such as in a context), yet must
# delete it\self when the client disconnects (so the process will terminate
# gracefully).  This needs to be worked out for BITS instrument sessions
# that use a temporary tiled server, such as CI workflows.
# The concerns to be addressed are described in this GitHub issue:
# See https://github.com/bluesky/tiled/issues/1246 for more details.
#
# FIXME: this instance does not terminate gracefull when session exits
# _tiled_temporary_server = None  # must persist
#
# def _tiled_temporary_catalog(iconfig: dict[str, Any]) -> Any:
#     """Connect with a temporary tiled catalog."""
#     from tiled.client import from_uri
#     from tiled.server import SimpleTiledServer
#
#     global _tiled_temporary_server
#
#     # SimpleTiledServer("my_data/"), default is temporary storage
#     _tiled_temporary_server = SimpleTiledServer()  # api_key="secret"
#     client = from_uri(_tiled_temporary_server.uri)
#     logger.debug("%s: client=%s", type(client).__name__, str(client))
#     logger.info("Tiled server (temporary catalog) connectedr")
#
#     return client
