"""
APS utility helper functions
============================

.. autosummary::
    ~host_on_aps_subnet
    ~aps_dm_setup
"""

import logging
import os
import pathlib
import socket

logger = logging.getLogger(__name__)


def aps_dm_setup(dm_setup_file_path):
    """
    APS Data Management setup
    =========================

    Read the bash shell script file used by DM to setup the environment. Parse any
    ``export`` lines and add their environment variables to this session.  This is
    done by brute force here since the APS DM environment setup requires different
    Python code than bluesky and the two often clash.

    This setup must be done before any of the DM package libraries are called.

    """
    if dm_setup_file_path is not None:
        bash_script = pathlib.Path(dm_setup_file_path)
        if bash_script.exists():
            logger.info("APS DM environment file: %s", str(bash_script))
            # parse environment variables from bash script
            environment = {}
            for line in open(bash_script).readlines():
                if not line.startswith("export "):
                    continue
                export_part = line.strip().split("export ", 1)[-1]
                if not export_part:
                    continue
                if "=" in export_part:
                    k, v = export_part.split("=", 1)
                    k = k.strip()
                    v = v.strip()  # Default to empty string
                else:
                    k = export_part.strip()
                    v = ""  # This is what bash does
                environment[k] = v
            os.environ.update(environment)

            workflow_owner = os.environ["DM_STATION_NAME"].lower()
            logger.info("APS DM workflow owner: %s", workflow_owner)
        else:
            logger.warning("APS DM setup file does not exist: '%s'", bash_script)


def host_on_aps_subnet():
    """Detect if this host is on an APS subnet."""
    LOOPBACK_IP4 = "127.0.0.1"
    PUBLIC_IP4_PREFIX = "164.54."
    PRIVATE_IP4_PREFIX = "10.54."
    TEST_IP = "10.254.254.254"  # does not have to be reachable
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0)
        try:
            sock.connect((TEST_IP, 1))
            ip4 = sock.getsockname()[0]
        except Exception:
            ip4 = LOOPBACK_IP4
    return True in [
        ip4.startswith(PUBLIC_IP4_PREFIX),
        ip4.startswith(PRIVATE_IP4_PREFIX),
    ]
