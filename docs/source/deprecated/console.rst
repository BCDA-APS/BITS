IPython console
===============

An IPython console session provides direct interaction with the
various parts of the bluesky (and other Python) packages and tools.

Start the console session with the environment with your bluesky installation,
including the `instrument` package you installed.  Here, ``$`` is a bash
command prompt.  You don't type the command prompt.

.. code-block:: bash

    $ ipython
    Python 3.12.4 | packaged by Anaconda, Inc. | (main, Jun 18 2024, 15:12:24) [GCC 11.2.0]
    Type 'copyright', 'credits' or 'license' for more information
    IPython 8.27.0 -- An enhanced Interactive Python. Type '?' for help.

When ready to load the bluesky data acquisition for use, type this command.
Note that ``In [1]:`` and ``In [2]:`` are numbered command prompts from IPython.

.. code-block:: ipy

    In [1]: from apsbits.demo_instrument.startup import *
    I Mon-12:02:54.126: **************************************** startup
    I Mon-12:02:54.126: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/logging_setup.py
    I Mon-12:02:54.126: Log file: /home/prjemian/Documents/projects/prjemian/model_instrument/.logs/logging.log
    Activating auto-logging. Current session state plus future input saved.
    Filename       : /home/prjemian/Documents/projects/prjemian/model_instrument/.logs/ipython_log.py
    Mode           : rotate
    Output logging : True
    Raw input log  : False
    Timestamping   : True
    State          : active
    I Mon-12:02:54.127: Console logging: /home/prjemian/Documents/projects/prjemian/model_instrument/.logs/ipython_log.py
    I Mon-12:02:54.127: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/startup.py
    I Mon-12:02:54.127: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/aps_functions.py
    I Mon-12:02:54.444: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/helper_functions.py
    Exception reporting mode: Minimal
    I Mon-12:02:54.444: xmode exception level: 'Minimal'
    W Mon-12:02:54.516: APS DM setup file does not exist: '/home/dm/etc/dm.setup.sh'
    I Mon-12:02:54.642: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/core/best_effort_init.py
    I Mon-12:02:55.245: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/core/catalog_init.py
    I Mon-12:02:55.643: Databroker catalog: temp
    I Mon-12:02:55.644: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/controls_setup.py
    I Mon-12:02:55.718: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/metadata.py
    I Mon-12:02:55.718: RunEngine metadata saved in directory: /home/prjemian/.config/Bluesky_RunEngine_md
    I Mon-12:02:55.718: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/core/run_engine_init.py
    I Mon-12:02:55.720: using ophyd control layer: 'pyepics'
    I Mon-12:02:55.779: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/callbacks/spec_data_file_writer.py
    I Mon-12:02:55.780: SPEC data file: /home/prjemian/Documents/projects/prjemian/model_instrument/20241014-120255.dat
    I Mon-12:02:55.813: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/tests/sim_plans.py

    In [2]:

Shortcut
========

Here's a shortcut that combines both steps:

.. code-block::

    ipython -i -c "from apsbits.demo_instrument.startup import *"
