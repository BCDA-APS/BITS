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

    from new_instrument.startup import *
