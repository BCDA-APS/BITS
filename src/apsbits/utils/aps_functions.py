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
import re

logger = logging.getLogger(__name__)


def aps_dm_setup(dm_setup_file_path: str | None) -> None:
    """
    APS Data Management setup.
    =========================

    Read the bash shell script file used by DM to setup the environment. Parse any
    ``export`` lines and add their environment variables to this session. This is
    done by brute force here since the APS DM environment setup requires different
    Python code than bluesky and the two often clash.

    This setup must be done before any of the DM package libraries are called.

    Parameters
    ----------
    dm_setup_file_path : str | None
        Path to the bash shell script file to parse for environment variables.
    """
    if dm_setup_file_path is not None:
        bash_script = pathlib.Path(dm_setup_file_path)
        if bash_script.exists():
            logger.info("APS DM environment file: %s", str(bash_script))
            # parse environment variables from bash script
            environment: dict[str, str] = {}
            for line in open(bash_script).readlines():
                match = re.match(r'^export\s+(\w+)=(.*)$', line.strip())
                if not match:
                    continue
                k, v = match.groups()
                environment[k] = v
            os.environ.update(environment)

            workflow_owner = os.environ.get("DM_STATION_NAME", "").lower()
            if workflow_owner:
                logger.info("APS DM workflow owner: %s", workflow_owner)
            else:
                logger.warning("DM_STATION_NAME not set in environment.")
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
