Python scripts
==============

Bluesky data acquisition can be written as Python command programs (scripts).
This example program shows the RunEngine's metadata.  Save it to a file (perhaps
named ``example.py``).  Be sure to make the file executable. [#]_

.. code-block:: py
    :linenos:

    #!/usr/bin/env python
    from apsbits.demo_instrument.startup import RE

    print(f"{dict(RE.md)=!r}")

Assuming you named this file ``example.py``, then run it (in the environment
with your bluesky installation).  Note that ``$`` is a command prompt.  You don't
type that.

.. code-block:: bash
    :linenos:

    $ example.py
    I Mon-12:05:21.749: **************************************** startup
    I Mon-12:05:21.749: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/logging_setup.py
    I Mon-12:05:21.749: Log file: /home/prjemian/Documents/projects/prjemian/model_instrument/.logs/logging.log
    I Mon-12:05:21.898: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/startup.py
    I Mon-12:05:21.898: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/aps_functions.py
    I Mon-12:05:22.212: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/helper_functions.py
    W Mon-12:05:22.284: APS DM setup file does not exist: '/home/dm/etc/dm.setup.sh'
    I Mon-12:05:22.411: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/core/best_effort_init.py
    I Mon-12:05:23.002: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/core/catalog_init.py
    I Mon-12:05:23.404: Databroker catalog: temp
    I Mon-12:05:23.405: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/controls_setup.py
    I Mon-12:05:23.479: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/utils/metadata.py
    I Mon-12:05:23.479: RunEngine metadata saved in directory: /home/prjemian/.config/Bluesky_RunEngine_md
    I Mon-12:05:23.479: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/core/run_engine_init.py
    I Mon-12:05:23.482: using ophyd control layer: 'pyepics'
    I Mon-12:05:23.541: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/callbacks/spec_data_file_writer.py
    I Mon-12:05:23.541: SPEC data file: /home/prjemian/Documents/projects/prjemian/model_instrument/20241014-120523.dat
    I Mon-12:05:23.574: /home/prjemian/Documents/projects/prjemian/model_instrument/src/instrument/tests/sim_plans.py
    dict(RE.md)={'scan_id': 70, 'instrument_name': 'Most Glorious Scientific Instrument', 'login_id': 'prjemian@arf.jemian.org', 'conda_prefix': '/home/prjemian/.conda/envs/model_instrument_env', 'versions': {'apstools': '1.7.0', 'bluesky': '1.13', 'databroker': '1.2.5', 'epics': '3.5.7', 'h5py': '3.12.1', 'intake': '0.6.4', 'matplotlib': '3.9.2', 'numpy': '1.26.4', 'ophyd': '1.9.0', 'pyRestTable': '2020.0.10', 'python': '3.12.7', 'pysumreg': '1.0.6', 'spec2nexus': '2021.2.6'}, 'databroker_catalog': 'temp', 'iconfig': {'ICONFIG_VERSION': '2.0.0', 'DATABROKER_CATALOG': 'temp', 'RUN_ENGINE': {'DEFAULT_METADATA': {'beamline_id': 'instrument', 'instrument_name': 'Most Glorious Scientific Instrument', 'proposal_id': 'commissioning', 'databroker_catalog': 'temp'}, 'USE_PROGRESS_BAR': False}, 'AREA_DETECTOR': {'ALLOW_PLUGIN_WARMUP': True, 'BLUESKY_FILES_ROOT': '/path/to/data/', 'IMAGE_DIR': 'sub/directory/path', 'HDF5_FILE_TEMPLATE': '%s%s_%6.6d.h5'}, 'SPEC_DATA_FILES': {'FILE_EXTENSION': 'dat'}, 'DM_SETUP_FILE': '/home/dm/etc/dm.setup.sh', 'OPHYD': {'TIMEOUTS': {'PV_READ': 5, 'PV_WRITE': 5, 'PV_CONNECTION': 5}}, 'XMODE_DEBUG_LEVEL': 'Minimal'}, 'proposal_id': 'commissioning', 'pid': 3865585, 'beamline_id': 'instrument'}

.. note:: The first line is a linux *shebang* [#]_ that tells the
    linux command processor to start this script with the
    default ``python`` executable in the current environment.

.. [#] https://linuxhandbook.com/make-file-executable/
.. [#] https://en.wikipedia.org/wiki/Shebang_(Unix)
