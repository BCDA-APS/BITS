Setting up your instrument
================================

The iconfig file is a YAML file that contains the configuration for your instrument.
It is used to set up the instrument preferences and settings. The iconfig file is
located in the ``configs`` directory of your instrument package. Below we go through the settings available in the iconfig file.


RUN_ENGINE
-----------------------------
The ``RUN_ENGINE`` section contains the configuration for the run engine. The run engine is responsible for executing the data acquisition plans.

.. code-block:: yaml

    RUN_ENGINE:
        DEFAULT_METADATA:
            beamline_id: demo_instrument
            instrument_name: Most Glorious Scientific Instrument
            proposal_id: commissioning
            databroker_catalog: *databroker_catalog

        ### EPICS PV to use for the `scan_id`.
        ### Default: `RE.md["scan_id"]` (not using an EPICS PV)
        # SCAN_ID_PV: "IOC:bluesky_scan_id"

        ### Where to "autosave" the RE.md dictionary.
        ### Defaults:
        MD_PATH: .re_md_dict.yml

        ### The progress bar is nice to see,
        ### except when it clutters the output in Jupyter notebooks.
        ### Default: False
        USE_PROGRESS_BAR: false

.. _iconfig:

- ``beamline_id`` the metadata id you want saved for the beamline associated with the data aquosition runs you are about to conduct
- ``instrument_name`` the metadata name you want saved for your instrument associated with the data aquosition runs you are about to conduct
- ``proposal_id`` the metadata id you want saved for the proposal associated with the data aquosition runs you are about to conduct
- ``MD_PATH`` the path to the file where the metadata dictionary will be saved
- ``USE_PROGRESS_BAR`` whether to use a progress bar or not to showcase the progress the run engine is making with the data aquisition
- ``SCAN_ID_PV`` can be uncommented if you need a PV to be used for the scan id.

BEC
-----------------------------

.. code-block:: yaml

    BEC:
        BASELINE: true
        HEADING: true
        PLOTS: false
        TABLE: true

- ``BASELINE`` Print hinted fields from the ‘baseline’ stream.
- ``HEADING`` Print timestamp and IDs at the top of a run.
- ``PLOTS`` Outputs a matplotlib plot of your data aquisition at the end of stream
- ``TABLE`` If your data gets tabulated or not


Callbacks
-----------------------------
.. code-block:: yaml

    NEXUS_DATA_FILES:
    ENABLE: false
    FILE_EXTENSION: hdf

    SPEC_DATA_FILES:
        ENABLE: true
        FILE_EXTENSION: dat

The ``enable`` fields allow for data to be outputted within a NEXUS or SPEC file format. The file extension is the file type you want to save your data as.
If the callback is enabled, the data will be stored from where you initialized the ipython session or notebook.

DM_SETUP_FILE Path
-----------------------------
.. code-block:: yaml

    ### APS Data Management
    ### Use bash shell, deactivate all conda environments, source this file:
    DM_SETUP_FILE: "/home/dm/etc/dm.setup.sh"

The above file is a bash script that sets up the environment for the APS Data Management system. It is used to set up the environment variables to access the APS Data Management system.
The path should reference where this bash script lives.

Devices
-----------------------------
.. code-block:: yaml

    ### Local OPHYD Device Control Yaml
    DEVICES_FILES:
    - devices.yml
    APS_DEVICES_FILES:
    - devices_aps_only.yml

    # Log when devices are added to console (__main__ namespace)
    MAKE_DEVICES:
        LOG_LEVEL: info

- ``DEVICES_FILES`` the name to the yaml file that contains the devices you want to use in your data aquisition. This file has to be stored in the configs folder of your instrument
- ``APS_DEVICES_FILES`` the name to the yaml file that contains the devices you want to use in your data aquisition. This file is for devices that work exclusively on the APS network.
- ``LOG_LEVEL`` the log level for the devices you want to use in your data aquisition. The default is info.

OPHYD SETTINGS
----------------------------------
.. code-block:: yaml

    OPHYD:
        ### Control layer for ophyd to communicate with EPICS.
        ### Default: PyEpics
        ### Choices: "PyEpics" or "caproto" # caproto is not yet supported
        CONTROL_LAYER: PyEpics

        ### default timeouts (seconds)
        TIMEOUTS:
            PV_READ: &TIMEOUT 5
            PV_WRITE: *TIMEOUT
            PV_CONNECTION: *TIMEOUT

- ``CONTROL_LAYER`` the control layer you want to use to communicate with EPICS. The default is PyEpics, the other option would be caproto
- ``TIMEOUTS`` the timeouts for the different types of communication with EPICS. The default is 5 seconds for all types of communication.

Logging levels
-----------------------------
.. code-block:: yaml

    XMODE_DEBUG_LEVEL: Plain

The options for the debugging levels in your iconfig file are:

- ``Plain``: Displays basic traceback information with error type and message. No additional context or special formatting is included.
- ``Context``: Shows code surrounding the error line for better understanding. Includes several lines before and after the problematic code.
- ``Verbose``: Provides comprehensive debugging information including variable values and system details. Best for complex debugging scenarios where maximum information is needed.
-  ``Minimal``: Shows only the exception type and error message without traceback. Cleanest output for quick error identification or production environments.
- ``Docs``: Enhances error messages with relevant documentation for the exception type. Helpful in learning environments or when working with unfamiliar code.


Full Iconfig file
-----------------------------


.. literalinclude:: ../../../src/apsbits/demo_instrument/configs/iconfig.yml
   :language: yaml
