"""
RunEngine Metadata
==================

.. autosummary::
    ~get_md_path
    ~re_metadata
"""

import collections
import getpass
import logging
import os
import pathlib
import socket
import sys
from typing import Any

import bluesky
import databroker
import epics
import h5py
import matplotlib
import numpy
import ophyd
import pyRestTable
import pysumreg

try:
    import apstools

    APSTOOLS_VERSION = apstools.__version__
except ImportError:
    APSTOOLS_VERSION = "(not installed)"

import apsbits

logger = logging.getLogger(__name__)


DEFAULT_MD_PATH = pathlib.Path.home() / ".config" / "Bluesky_RunEngine_md"
HOSTNAME = socket.gethostname() or "localhost"
USERNAME = getpass.getuser() or "Bluesky user"
VERSIONS = dict(
    apsbits=apsbits.__version__,
    apstools=APSTOOLS_VERSION,
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
    md = {
        "login_id": f"{USERNAME}@{HOSTNAME}",
        "versions": VERSIONS,
        "pid": os.getpid(),
        "iconfig": iconfig,
    }

    RE_CONFIG = iconfig.get("RUN_ENGINE", {})
    md.update(RE_CONFIG.get("DEFAULT_METADATA", {}))

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix is not None:
        md["conda_prefix"] = conda_prefix
    return md
