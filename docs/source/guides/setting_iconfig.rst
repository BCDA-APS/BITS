Setting up your instrument
================================

The iconfig file is a YAML file that contains the configuration for your instrument.
It is used to set up the instrument preferences and settings. The iconfig file is
located in the ``configs`` directory of your instrument package. Below we go through the settings available in the iconfig file.

CATALOG
----------------

A *catalog* is where the data from a bluesky *run* (documents published by the
bluesky RunEngine) is saved.

APS is in the process of changing catalogs at beamlines to use Tiled servers
(backed by a PostgreSQL database) instead of Databroker (backed by a MongoDB
database).  The Tiled server needs one or two parameters: ``TILED_PROFILE_NAME``
(and optionally ``TILED_PATH_NAME``).  The older databroker needs one:
``DATABROKER_CATALOG``.

While the Tiled server configuration is preferred, it may not yet be available
for your BITS installation.

``TILED_PROFILE_NAME`` (preferred)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Name of the Tiled profile to use.

If ``TILED_PROFILE_NAME`` is set, it takes precedence over ``DATABROKER_CATALOG``.

The tiled profile is a special file (see ``tiled profile --help``).  It defines
a simple shortcut to the full Tiled server URI and API key necessary for write
access to the catalog.  A full list of the profile names available to you
can be obtained with the command: ``tiled profile list``.

``TILED_PATH_NAME`` (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Optional *server-defined* path name provided by the Tiled server.

Important notes:

* ``TILED_PATH_NAME`` is a path provided by the tiled server. It is not a filesystem directory path.
* If your server only defines the tiled catalog at ``/``, do not define ``TILED_PATH_NAME``.
* Different Tiled server deployments may provide different path names.
* If omitted, the Tiled server default path is used.
* Setting ``TILED_PATH_NAME: "/"`` has been observed to cause a server error.
  In that case, do **not** define ``TILED_PATH_NAME``.

Example
++++++++++++++

Example excerpt from ``configs/iconfig.yml``:


.. code-block:: yaml
    :linenos:

    # Preferred Tiled configuration
    TILED_PROFILE_NAME: raw
    # Only set this if your server requires a non-default path:
    TILED_PATH_NAME: /raw

Legacy configuration
+++++++++++++++++++++++++++++++++

``DATABROKER_CATALOG`` (legacy)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``DATABROKER_CATALOG`` is supported for backward compatibility, but
``TILED_PROFILE_NAME`` (and optionally ``TILED_PATH_NAME``) is preferred.

If both are set, ``TILED_PROFILE_NAME`` is used.

RUN_ENGINE
-----------------------------
The ``RUN_ENGINE`` section contains the configuration for the run engine. The run engine is responsible for executing the data acquisition plans.

.. code-block:: yaml

    RUN_ENGINE:
        DEFAULT_METADATA:
            beamline_id: demo_instrument
            instrument_name: Most Glorious Scientific Instrument
            proposal_id: commissioning

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
