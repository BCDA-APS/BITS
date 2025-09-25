.. _creating_instrument:

Creating BITS Instruments
==========================

This guide shows how to create new instruments with BITS, from simple single-instrument setups to complex multi-beamline deployments.

Quick Start: Create Your First Instrument
------------------------------------------

**Create an instrument in 3 commands:**

.. code-block:: bash

    python -m apsbits.api.create_new_instrument my_instrument
    pip install -e .
    python -c "from my_instrument.startup import *; print('Instrument ready!')"

This creates a complete instrument package with:

- Main instrument module (``src/my_instrument/``)
- Queue server configuration (``src/my_instrument_qserver/``)
- Ready-to-use startup script and configuration files

Complete Instrument Creation Guide
-----------------------------------

Understanding BITS Instrument Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BITS instruments follow a standardized directory structure:

.. code-block:: text

    your-project/
    ├── pyproject.toml              # Package configuration
    ├── README.md                   # Project documentation
    └── src/
        ├── my_instrument/          # Main instrument package
        │   ├── startup.py          # Entry point (REQUIRED)
        │   ├── configs/            # Configuration files (REQUIRED)
        │   │   └── iconfig.yml     # Main instrument config
        │   ├── devices/            # Custom device implementations
        │   ├── plans/              # Custom scan plans
        │   ├── callbacks/          # Data writing and processing
        │   ├── utils/              # Helper functions
        │   └── suspenders/         # Safety interlocks
        └── my_instrument_qserver/  # Queue server configuration
            ├── qs-config.yml       # Queue server settings
            ├── qs_host.sh          # Startup script
            └── user_group_permissions.yaml

Creating Different Types of Instruments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Single Instrument (Basic):**

Most instruments start with a single package:

.. code-block:: bash

    # Create basic instrument
    python -m apsbits.api.create_new_instrument beamline_endstation

    # Example: 8-ID Instrument
    python -m apsbits.api.create_new_instrument id8_i

**Multi-Endstation Beamline:**

For beamlines with multiple experimental stations:

.. code-block:: bash

    # Create common package for shared components
    mkdir -p src/id12_common/{devices,plans}

    # Create individual endstations
    python -m apsbits.api.create_new_instrument id12_b  # Branch B
    python -m apsbits.api.create_new_instrument id12_e  # Branch E

**Complex Multi-Technique Beamline:**

For beamlines with many experimental techniques:

.. code-block:: bash

    # Create common infrastructure
    mkdir -p src/common_9id

    # Create technique-specific instruments
    python -m apsbits.api.create_new_instrument gisaxs
    python -m apsbits.api.create_new_instrument giwaxs
    python -m apsbits.api.create_new_instrument gixpcs
    python -m apsbits.api.create_new_instrument cssi

Customizing Instrument Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Manual Directory Creation:**

For advanced control over instrument structure:

.. code-block:: bash

    # Create directory structure manually
    mkdir -p src/my_instrument/{configs,devices,plans,callbacks,utils,suspenders}

    # Copy template files
    cp -r $(python -c "import apsbits; print(apsbits.__path__[0])")/demo_instrument/* src/my_instrument/

    # Customize as needed

**Template Customization:**

Modify the demo_instrument template for organization-specific defaults:

.. code-block:: python

    # In your custom template
    from apsbits.core.instrument_init import make_devices
    from your_organization.common_devices import StandardDetector

    # Add organization-specific imports
    # Customize default configurations

Configuration and Setup
~~~~~~~~~~~~~~~~~~~~~~~

**pyproject.toml Configuration:**

Each instrument needs proper package configuration:

.. code-block:: toml

    [project]
    name = "12id-bits"
    version = "0.0.1"
    description = "BITS Instrument Package"
    dependencies = ["apsbits"]

    [tool.copyright]
    copyright = "2024, Your Organization"

**iconfig.yml Basics:**

The main instrument configuration file:

.. code-block:: yaml

    # Configuration for the Bluesky instrument package.
    ICONFIG_VERSION: 2.0.0

    # Databroker catalog configuration
    DATABROKER_CATALOG: &databroker_catalog your_catalog

    # RunEngine configuration
    RUN_ENGINE:
        DEFAULT_METADATA:
            beamline_id: your_beamline
            instrument_name: "Your Instrument Name"
            proposal_id: commissioning
            databroker_catalog: *databroker_catalog

        # Optional: EPICS PV for scan_id
        # SCAN_ID_PV: "IOC:bluesky_scan_id"

        MD_PATH: .re_md_dict.yml
        USE_PROGRESS_BAR: false

Installation and Testing
~~~~~~~~~~~~~~~~~~~~~~~~

**Install the New Instrument:**

.. code-block:: bash

    # Development installation (editable)
    pip install -e .

    # Or for production
    pip install .

**Test the Installation:**

.. code-block:: python

    # Test instrument import
    from my_instrument.startup import *

    # Verify components loaded
    print(f"RunEngine: {RE}")
    print(f"Catalog: {cat}")

    # Test with simulation plans
    RE(sim_print_plan())

**Test Queue Server (Optional):**

.. code-block:: bash

    # Start queue server
    cd src/my_instrument_qserver
    ./qs_host.sh

    # In another terminal, test connection
    qserver-console-monitor

Deployment Patterns and Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common Package Pattern:**

When multiple instruments share hardware:

.. code-block:: python

    # In src/beamline_common/devices/shared_optics.py
    from apstools.devices import SlitDevice

    class BeamlineSlits(SlitDevice):
        """Shared slit system for all endstations"""
        pass

    # In src/endstation_a/startup.py
    from beamline_common.devices.shared_optics import BeamlineSlits

    slits = BeamlineSlits("SLIT_PV:", name="slits")

**Environment-Specific Configuration:**

Handle development vs production deployments:

.. code-block:: python

    # In startup.py
    from apsbits.utils.aps_functions import host_on_aps_subnet

    if host_on_aps_subnet():
        # Load production device configurations
        load_config(instrument_path / "configs" / "devices_aps_only.yml")
    else:
        # Use simulation devices for development
        print("Development mode: using simulated devices")

**Multi-Instrument Package Management:**

For projects with multiple related instruments:

.. code-block:: toml

    # In pyproject.toml
    [project]
    name = "beamline-instruments"
    dependencies = ["apsbits"]

    [project.optional-dependencies]
    endstation_a = ["specific-detector-package"]
    endstation_b = ["different-detector-package"]
    all = ["beamline-instruments[endstation_a,endstation_b]"]

Troubleshooting Instrument Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common Issues:**

1. **Import errors after creation:**

   .. code-block:: bash

       # Ensure proper installation
       pip install -e .

       # Check Python path
       python -c "import sys; print('\\n'.join(sys.path))"

2. **EPICS connection failures:**

   Check network configuration and EPICS environment variables:

   .. code-block:: bash

       echo $EPICS_CA_ADDR_LIST
       echo $EPICS_CA_AUTO_ADDR_LIST

3. **Configuration file errors:**

   Validate YAML syntax:

   .. code-block:: bash

       python -c "import yaml; yaml.safe_load(open('src/my_instrument/configs/iconfig.yml'))"

4. **Queue server startup issues:**

   Check permissions and environment:

   .. code-block:: bash

       chmod +x src/my_instrument_qserver/qs_host.sh
       conda list bluesky-queueserver

**AI-Assisted Troubleshooting:**

BITS instruments are compatible with bAIt (Bluesky AI Tools) for automated analysis:

.. code-block:: python

    # Use bAIt to analyze instrument structure
    from bait_base.analyzers import DeploymentAnalyzer

    analyzer = DeploymentAnalyzer()
    result = analyzer.analyze("path/to/your-project")

    # Get recommendations for improvements
    print(result.recommendations)

Next Steps
~~~~~~~~~~

After creating your instrument:

1. :doc:`Configure devices and hardware <creating_devices>`
2. :doc:`Create custom scan plans <creating_plans>`
3. :doc:`Set up data management integration <dm>`
4. :doc:`Configure queue server for production <qserver>`
5. :doc:`Deploy with best practices <deployment_patterns>`

Advanced Topics
~~~~~~~~~~~~~~~

- :doc:`Multi-beamline architectures <common_instruments>`
- :doc:`Custom device patterns <area_detectors>`
- :doc:`Advanced scanning strategies <advanced_scanning>`
- :doc:`Integration with facility systems <facility_integration>`
