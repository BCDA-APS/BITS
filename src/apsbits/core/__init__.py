"""
Utility support to start bluesky sessions.

Also contains setup code that MUST run before other code in this directory.
"""

from apsbits.utils.helper_functions import debug_python
from apsbits.utils.helper_functions import mpl_setup


def prepare_bits():
    debug_python()
    mpl_setup()
