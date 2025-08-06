"""
Nexus data file writer callback.

This module provides callbacks for writing data to Nexus data files.
"""

import logging
from typing import Any

from apstools.utils import host_on_aps_subnet

from apsbits.utils.config_loaders import get_config

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

# Get the configuration
iconfig = get_config()


if host_on_aps_subnet():
    from apstools.callbacks import NXWriterAPS as NXWriter
else:
    from apstools.callbacks import NXWriter


class MyNXWriter(NXWriter):
    """Patch to get sample title from metadata, if available."""

    def get_sample_title(self) -> str:
        """
        Get the title from the metadata or modify the default.

        default title: S{scan_id}-{plan_name}-{short_uid}
        """
        try:
            title = self.metadata["title"]
        except KeyError:
            # title = super().get_sample_title()  # the default title
            title = f"S{self.scan_id:05d}-{self.plan_name}-{self.uid[:7]}"
        return title


def nxwriter_init(RE: Any) -> Any:
    """Initialize the Nexus data file writer callback."""
    nxwriter = MyNXWriter()  # create the callback instance
    """The NeXus file writer object."""

    if iconfig.get("NEXUS_DATA_FILES", {}).get("ENABLE", False):
        RE.subscribe(nxwriter.receiver)  # write data to NeXus files

    nxwriter.file_extension = iconfig.get("NEXUS_DATA_FILES", {}).get(
        "FILE_EXTENSION", "hdf"
    )

    print(nxwriter.file_extension)
    warn_missing = iconfig.get("NEXUS_DATA_FILES", {}).get("WARN_MISSING", False)
    nxwriter.warn_on_missing_content = warn_missing

    return nxwriter
