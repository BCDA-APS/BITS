Startup Configuration Guide
=========================

This guide explains the configuration and setup of the Bluesky Data Acquisition startup process.

Overview
--------

The startup.py file initializes and configures the Bluesky Data Acquisition environment. It supports various execution contexts including:

* Python scripts
* IPython console
* Jupyter notebook
* Bluesky queueserver

Configuration Blocks
------------------

Import Block
~~~~~~~~~~~

The file begins with necessary imports organized into several categories:

* Standard Library imports
* Core functionality imports (BEC, catalog, instrument initialization)
* Utility function imports
* Configuration-related imports

Configuration Loading
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    instrument_path = Path(__file__).parent
    iconfig_path = instrument_path / "configs" / "iconfig.yml"
    iconfig = load_config(iconfig_path)

This block:
* Determines the instrument package path
* Loads the main configuration file (iconfig.yml)
* Configures additional logging if needed

Logging Setup
~~~~~~~~~~~~

.. code-block:: python

    extra_logging_configs_path = instrument_path / "configs" / "extra_logging.yml"
    configure_logging(extra_logging_configs_path=extra_logging_configs_path)

Tips:
* Create an extra_logging.yml file if you need custom logging configuration
* The default logging setup from apsbits will be used if no extra configuration is provided

Data Management Setup
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    aps_dm_setup(iconfig.get("DM_SETUP_FILE"))

Configures the data management system. Make sure to:
* Set the DM_SETUP_FILE path in your iconfig.yml
* Configure appropriate data storage locations

Bluesky Initialization
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    bec, peaks = init_bec_peaks(iconfig)
    cat = init_catalog(iconfig)
    RE, sd = init_RE(iconfig, bec_instance=bec, cat_instance=cat)

This block initializes:
* Best Effort Callback (BEC) and peak finding
* Data catalog
* Run Engine (RE) and Supplemental Data (sd)

Optional Callbacks
~~~~~~~~~~~~~~~~

Nexus Data File Writer
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    if iconfig.get("NEXUS_DATA_FILES", {}).get("ENABLE", False):
        from .callbacks.nexus_data_file_writer import nxwriter_init
        nxwriter = nxwriter_init(RE)

To enable:
* Set NEXUS_DATA_FILES.ENABLE to True in iconfig.yml
* Configure appropriate Nexus file settings

SPEC Data File Writer
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    if iconfig.get("SPEC_DATA_FILES", {}).get("ENABLE", False):
        from .callbacks.spec_data_file_writer import init_specwriter_with_RE
        # ... additional imports ...

To enable:
* Set SPEC_DATA_FILES.ENABLE to True in iconfig.yml
* Configure SPEC file settings as needed

Queue Server Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

The file handles two different import scenarios:

1. Queue Server Mode:
   * Imports all standard plans
   * Uses specific lineup2 import

2. Standard Mode:
   * Imports apstools plans and utilities
   * Imports bluesky plan stubs and plans with conventional prefixes

Device Loading
~~~~~~~~~~~~

.. code-block:: python

    RE(make_devices(clear=False, file="devices.yml"))
    if host_on_aps_subnet():
        RE(make_devices(clear=False, file="device_aps_only.yml"))

This block:
* Loads the main device configuration from devices.yml
* Optionally loads APS-specific devices from devices_aps_only.yml if running on APS subnet
* Uses clear=False to preserve existing devices

Tips:
* Create a devices.yml file with your instrument's device configurations
* Optionally create device_aps_only.yml for APS-specific devices
* The make_devices function will automatically register devices with the ophyd registry

Baseline Device Setup
~~~~~~~~~~~~~~~~~~~

The baseline device setup allows you to track and record the state of specific devices during each scan. This is particularly useful for monitoring environmental conditions or instrument parameters that might affect your measurements.

To configure baseline devices:

1. In your devices.yml file, add a `label: baseline` to any device you want to track:

   .. code-block:: yaml

       apstools.devices.ApsMachineParametersDevice:
       - name: aps
         labels:
         - baseline

       ophyd.EpicsSignalRO:
       - name: temperature_monitor
         prefix: "IOC:TEMP"
         labels:
         - baseline

2. The baseline devices will be automatically included in the metadata of each scan through the setup_baseline_stream function:

   .. code-block:: python

       setup_baseline_stream(sd, oregistry, connect=False)

3. You can access baseline device values in your analysis using the scan metadata.

Tips:
* Use baseline devices for monitoring critical environmental parameters
* Consider including timestamps, temperature, pressure, or other relevant measurements
* Baseline devices should be read-only to avoid accidental modifications
* Keep the number of baseline devices reasonable to avoid excessive data collection

Configuration Tips
----------------

1. iconfig.yml Structure
   ~~~~~~~~~~~~~~~~~~~~

   Essential sections:

   .. code-block:: yaml

       DM_SETUP_FILE: "path/to/dm_setup.yml"
       NEXUS_DATA_FILES:
         ENABLE: false
       SPEC_DATA_FILES:
         ENABLE: false

2. Logging Configuration
   ~~~~~~~~~~~~~~~~~~~~

   Create extra_logging.yml for custom logging:

   .. code-block:: yaml

       version: 1
       handlers:
         console:
           class: logging.StreamHandler
           level: INFO
       root:
         level: INFO
         handlers: [console]
