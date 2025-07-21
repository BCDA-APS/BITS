"""
APS utility helper functions
============================

.. autosummary::
    ~host_on_aps_subnet
"""

import socket


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
