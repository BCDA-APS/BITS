"""
Utility support to start bluesky sessions.

Also contains setup code that MUST run before other code in this directory.
"""

from apsbits.utils.helper_functions import debug_python
from apsbits.utils.helper_functions import mpl_setup


def prepare_bits():
    """Enable some conveniences to the current python session.

    - Better ipython logging
    - Configures the matplotlib backend

    """
    debug_python()
    mpl_setup()
