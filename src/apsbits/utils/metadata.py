"""
RunEngine Metadata
==================

.. autosummary::
    ~get_md_path
    ~re_metadata
"""

import collections
import logging
import os
import pathlib
import sys
from typing import Any

logger = logging.getLogger(__name__)


DEFAULT_MD_PATH = pathlib.Path.home() / ".config" / "Bluesky_RunEngine_md"

# Cached metadata, computed lazily on first call to _collect_metadata()
_cached_metadata = None


def _collect_metadata():
    """Collect version and host metadata. Cached after first call."""
    global _cached_metadata
    if _cached_metadata is not None:
        return _cached_metadata

    import getpass
    import socket

    import bluesky
    import databroker
    import epics
    import h5py
    import matplotlib
    import numpy
    import ophyd
    import pyRestTable
    import pysumreg

    import apsbits

    try:
        import apstools

        apstools_version = apstools.__version__
    except ImportError:
        apstools_version = "(not installed)"

    hostname = socket.gethostname() or "localhost"
    username = getpass.getuser() or "Bluesky user"
    versions = dict(
        apsbits=apsbits.__version__,
        apstools=apstools_version,
        bluesky=bluesky.__version__,
        databroker=databroker.__version__,
        epics=epics.__version__,
        h5py=h5py.__version__,
        matplotlib=matplotlib.__version__,
        numpy=numpy.__version__,
        ophyd=ophyd.__version__,
        pyRestTable=pyRestTable.__version__,
        pysumreg=pysumreg.__version__,
        python=sys.version.split(" ")[0],
    )

    _cached_metadata = {
        "hostname": hostname,
        "username": username,
        "versions": versions,
    }
    return _cached_metadata


def get_md_path(iconfig: collections.abc.Mapping[str, Any] | None = None) -> str | None:
    """
    Get path for RE metadata.

    ==============  ==============================================
    support         path
    ==============  ==============================================
    PersistentDict  Directory where dictionary keys are stored in separate files.
    StoredDict      File where dictionary is stored as YAML.
    ==============  ==============================================

    In either case, the 'path' can be relative or absolute.  Relative
    paths are with respect to the present working directory when the
    bluesky session is started.
    """
    if iconfig is None:
        return None
    RE_CONFIG = iconfig.get("RUN_ENGINE", {})
    md_path_name = RE_CONFIG.get("MD_PATH", DEFAULT_MD_PATH)
    path = pathlib.Path(md_path_name)
    logger.info("RunEngine metadata saved to: %s", str(path))
    return str(path)


def re_metadata(iconfig: collections.abc.Mapping[str, Any] = {}) -> dict[str, Any]:
    """Programmatic metadata for the RunEngine."""
    meta = _collect_metadata()
    md = {
        "login_id": f"{meta['username']}@{meta['hostname']}",
        "versions": meta["versions"],
        "pid": os.getpid(),
        "iconfig": iconfig,
    }

    RE_CONFIG = iconfig.get("RUN_ENGINE", {})
    md.update(RE_CONFIG.get("DEFAULT_METADATA", {}))

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix is not None:
        md["conda_prefix"] = conda_prefix
    return md
