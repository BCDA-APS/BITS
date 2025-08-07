"""
custom callbacks
================

.. autosummary::
    :nosignatures:

    ~newSpecFile
    ~spec_comment
    ~specwriter
"""

import datetime
import logging
import pathlib
from typing import Any
from typing import Optional

import apstools.callbacks
import apstools.utils

from apsbits.utils.config_loaders import get_config

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

iconfig = get_config()
file_extension = iconfig.get("SPEC_DATA_FILES", {}).get("FILE_EXTENSION", "dat")


def spec_comment(comment: str, doc: Optional[Any] = None) -> None:
    """Make it easy for user to add comments to the data file."""
    apstools.callbacks.spec_comment(comment, doc, specwriter)


def newSpecFile(
    title: str, scan_id: Optional[int] = None, RE: Optional[Any] = None
) -> None:
    """
    User choice of the SPEC file name.

    Cleans up title, prepends month and day and appends file extension.
    If ``RE`` is passed, then resets ``RE.md["scan_id"] = scan_id``.

    If the SPEC file already exists, then ``scan_id`` is ignored and
    ``RE.md["scan_id"]`` is set to the last scan number in the file.
    """
    kwargs = {}
    if RE is not None:
        kwargs["RE"] = RE

    mmdd = str(datetime.datetime.now()).split()[0][5:].replace("-", "_")
    clean = apstools.utils.cleanupText(title)
    fname = pathlib.Path(f"{mmdd}_{clean}.{file_extension}")
    if fname.exists():
        logger.warning(">>> file already exists: %s <<<", fname)
        handled = "appended"
    else:
        kwargs["scan_id"] = scan_id or 1
        handled = "created"

    specwriter.newfile(fname, **kwargs)

    logger.info("SPEC file name : %s", specwriter.spec_filename)
    logger.info("File will be %s at end of next bluesky scan.", handled)


# Add this function to specwriter.py
def init_specwriter_with_RE(RE: Any) -> None:
    """Initialize specwriter with the run engine."""

    # make the SPEC file in current working directory (assumes is writable)
    specwriter.newfile(specwriter.spec_filename)

    if iconfig.get("SPEC_DATA_FILES", {}).get("ENABLE", False):
        RE.subscribe(specwriter.receiver)  # write data to SPEC files
        logger.info("SPEC data file: %s", specwriter.spec_filename.resolve())

    try:
        # feature new in apstools 1.6.14
        from apstools.plans import label_stream_wrapper

        def motor_start_preprocessor(plan):
            """Record motor positions at start of each run."""
            return label_stream_wrapper(plan, "motor", when="start")

        RE.preprocessors.append(motor_start_preprocessor)
    except Exception:
        logger.warning("Could not load support to log motors positions.")


# write scans to SPEC data file
try:
    # apstools >=1.6.21
    _specwriter = apstools.callbacks.SpecWriterCallback2()
except AttributeError:
    # apstools <1.6.21
    _specwriter = apstools.callbacks.SpecWriterCallback()

specwriter = _specwriter
"""The SPEC file writer object."""
