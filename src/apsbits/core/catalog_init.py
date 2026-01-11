"""
Databroker catalog
==================

.. autosummary::
    ~init_catalog
"""

import logging
import weakref
from typing import Any
from typing import Union

import databroker
from bluesky_tiled_plugins.clients.catalog_of_bluesky_runs import CatalogOfBlueskyRuns
from databroker._drivers.mongo_normalized import BlueskyMongoCatalog
from databroker._drivers.msgpack import BlueskyMsgpackCatalog
from tiled.client import from_profile
from tiled.client import from_uri
from tiled.client.container import Container
from tiled.server import SimpleTiledServer

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

# The httpx (via tiled) logger is set too noisy.  Make it quieter.
logging.getLogger("httpx").setLevel(logging.WARNING)

DATABROKER_CATALOG_TYPE = Union[BlueskyMongoCatalog, BlueskyMsgpackCatalog]
TILED_CATALOG_TYPE = Union[CatalogOfBlueskyRuns, Container]
ANY_CATALOG_TYPE = Union[DATABROKER_CATALOG_TYPE, TILED_CATALOG_TYPE]


def init_catalog(iconfig: dict[str, Any]) -> ANY_CATALOG_TYPE:
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
        # TODO: promote once `del client` is not needed for exit
        _tiled_temporary_catalog,
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


def _databroker_named_catalog(
    iconfig: dict[str, Any],
) -> Union[
    DATABROKER_CATALOG_TYPE,
    None,
]:
    """Connect with a named databroker catalog."""
    cat = None
    catalog_name = iconfig.get("DATABROKER_CATALOG")
    if catalog_name is not None:
        cat = databroker.catalog[catalog_name].v2
    logger.debug("%s: cat=%s", type(cat).__name__, str(cat))
    if cat is not None:
        logger.info("Databroker catalog initialized: %s", cat.name)
    return cat


def _databroker_temporary_catalog(iconfig: dict[str, Any]) -> BlueskyMsgpackCatalog:
    """Connect with a temporary databroker catalog."""
    cat = databroker.temp().v2
    logger.debug("%s: cat=%s", type(cat).__name__, str(cat))
    logger.info("Databroker temporary catalog initialized")
    return cat


def _tiled_profile_client(iconfig: dict[str, Any]) -> Union[None, TILED_CATALOG_TYPE]:
    """Connect with a tiled server using a profile."""
    cat = None
    profile = iconfig.get("TILED_PROFILE_NAME")
    path = iconfig.get("TILED_PATH_NAME")
    if profile is not None:
        client = from_profile(profile)
        cat = client if path is None else client[path]

    logger.debug("%s: cat=%s", type(cat).__name__, str(cat))
    if cat is not None:
        logger.info(
            "Tiled server (catalog) connected, profile=%r, path=%r",
            profile,
            path,
        )

    return cat


def _tiled_temporary_catalog(iconfig: dict[str, Any]) -> Container:
    """Connect with a temporary tiled catalog.

    WARNING: The SimpleTiledServer creates background threads that may prevent
    clean process exit. For interactive use, explicitly delete the returned
    client when done: `del client`
    """
    save_path = iconfig.get("TILED_SAVE_PATH")  # testing only?
    server = SimpleTiledServer(save_path)

    try:
        client = from_uri(server.uri)
        logger.info("Tiled server (temporary catalog) connected")

        # Store server reference for cleanup when client is deleted
        client._tiled_server = server

        # Cleanup when client is garbage collected
        def cleanup():
            try:
                server.close()
            except Exception:
                pass

        weakref.finalize(client, cleanup)

        return client
    except Exception:
        server.close()
        raise
