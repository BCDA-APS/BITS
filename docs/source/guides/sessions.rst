.. _sessions:

Starting Data Acquisition Sessions
========================================

Bluesky Data Acquisition sessions can be conducted in various formats, including
Python scripts, IPython consoles, Jupyter notebooks, and the bluesky
queueserver.

IPython console
----------------------

An IPython console session provides direct interaction with the
various parts of the bluesky (and other Python) packages and tools.

Start the console session with the environment with your bluesky installation.

.. code-block:: bash

    ipython

Jupyter Notebook
--------------------------

There are several ways to run a notebook.
An example notebook is provided: :download:`Download Demo Notebook <../../resources/demo.ipynb>`

Once a notebook is opened, pick the kernel with your bluesky
installation.


Starting Your Instrument
----------------------------------
When ready to load the bluesky data acquisition for use, type this command. For the purpose of this tutorial we assume you have already used BITS to create an instrument called `new_instrument`.

.. code-block:: bash

    from demo_instrument.startup import *

.. note::
Change the demo_instrument to your instrument installed package name.

Adding BITS to ipython profile
----------------------------------

To add BITS to your ipython profile, first create a new profile:

.. code-block:: bash

    ipython profile create bits-xx

Then, add the following to your startup file:

.. code-block:: bash

    cat > ~/.ipython/profile_bits-xx/startup/00-start-bits.py  << EOF
    from new_instrument.startup import *
    EOF

For more detailed guidance on creating and configuring an ipython profile, see the `bluesky training documentation <https://github.com/BCDA-APS/bluesky_training/blob/304b8d02503044932afa5657cb43afd1f6be2f40/docs/source/instrument/_create_bluesky_ipython_profile.rst#L2>`_.
