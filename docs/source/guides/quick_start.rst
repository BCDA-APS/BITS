.. _quick_start:

BITS Quick Start Guide
======================

Get your first BITS instrument running in under 10 minutes. This guide covers the essential steps with minimal explanation - see the complete guides for detailed information.

Prerequisites
-------------

- Python 3.11+
- conda or mamba package manager
- Basic familiarity with Python and command line

Step 1: Install BITS (2 minutes)
--------------------------------

.. code-block:: bash

    # Create environment and install
    conda create -y -n bits_env python=3.11 pyepics
    conda activate bits_env
    pip install apsbits

    # Verify installation
    python -c "import apsbits; print('✓ BITS installed')"

Step 2: Create Your First Instrument (1 minute)
OPTIONAL: Use BITS-Starter template
-----------------------------------------------

.. code-block:: bash

    # Create a new project directory
    mkdir my_beamline && cd my_beamline

    # Create instrument
    bits-create my_instrument

    # Install the instrument
    pip install -e .

**What this creates:**

.. code-block:: text

    my_beamline/
    ├── pyproject.toml
    └── src/
        ├── my_instrument/          # Main instrument
        │   ├── startup.py          # Entry point
        │   ├── configs/iconfig.yml # Configuration
        │   ├── devices/            # Device definitions
        │   └── plans/              # Scan plans
        └── my_instrument_qserver/  # Queue server setup

Step 3: Test Your Instrument (1 minute)
---------------------------------------

.. code-block:: python

    # Start Python and import your instrument
    from my_instrument.startup import *

    # Verify components loaded
    print(f"RunEngine: {RE}")
    print(f"Catalog: {cat}")

    # Test with simulation plans
    RE(sim_print_plan())        # Print scan information
    RE(sim_count_plan())        # Simulate data collection
    RE(sim_rel_scan_plan())     # Simulate a scan

**Expected output:**
.. code-block:: text

    RunEngine: <bluesky.run_engine.RunEngine object>
    Catalog: <intake_bluesky.jsonl.BlueskyJSONLCatalog object>

    # Simulation plans will show scan progress and simulated data

Step 4: Add a Simple Device (2 minutes)
---------------------------------------

Create a custom device:

.. code-block:: python

    # src/my_instrument/devices/my_device.py
    from ophyd import Device, EpicsMotor
    from ophyd import Component as Cpt

    class SampleStage(Device):
        """XY stage for sample positioning."""
        x = Cpt(EpicsMotor, ':X')
        y = Cpt(EpicsMotor, ':Y')

Configure the device:

.. code-block:: yaml

    # src/my_instrument/configs/devices.yml
    # Add this to the file:
    my_instrument.devices.my_device.SampleStage:
    - name: sample_stage
      prefix: "SIM:STAGE"  # Use SIM: for testing without hardware
      labels: ["motors", "sample"]


Test your device:

.. code-block:: python

    # Restart iPython and reload
    from my_instrument.startup import *

    # See all your loaded devices
    listobjects()

    # Your new device should be available
    print(sample_stage)
    print(f"X position: {sample_stage.x.position}")

Step 5: Create a Simple Plan (2 minutes)
-----------------------------------------

Create a custom scan plan:

.. code-block:: python

    # src/my_instrument/plans/my_plans.py
    from bluesky.plans import count, rel_scan
    from bluesky import plan_stubs as bps

    def quick_count(detector, num=1):
        """Simple counting plan."""
        yield from count([detector], num=num)

    def scan_sample_x(detector, motor, range_mm=5.0):
        """Scan sample X position."""
        yield from rel_scan([detector], motor, -range_mm, range_mm, 21)

Import and test your plan at the end of your startup script:

.. code-block:: python

    # src/my_instrument/startup.py
    from .plans.my_plans import quick_count, scan_sample_x

.. code-block:: python

    # Restart Python and test
    from my_instrument.startup import *

    # Test your plans
    RE(quick_count(sim_det, num=3))
    RE(scan_sample_x(sim_det, sim_motor, range_mm=2.0))

Step 6: Optional - Start Queue Server (2 minutes)
-------------------------------------------------

For remote operation and multi-user access:

.. code-block:: bash

    # In one terminal - start queue server
    cd src/my_instrument_qserver
    ./qs_host.sh start
    
    # Check status using:
    ./qs_host.sh status

    # In another terminal - connect and test
    queue-monitor

.. code-block:: python

    # Using queue server API
    from bluesky_queueserver_api import REManagerAPI

    RM = REManagerAPI(zmq_control_addr="tcp://localhost:60615")
    RM.environment_open()
    RM.queue_item_add(plan={"name": "sim_count_plan", "args": []})
    RM.queue_start()

What You've Accomplished
------------------------

In under 10 minutes, you've:

✅ **Installed BITS** with full Bluesky ecosystem
✅ **Created an instrument** with proper structure
✅ **Added custom devices** with configuration
✅ **Created scan plans** for data collection
✅ **Tested everything** with simulation
✅ **Optional: Set up queue server** for production use

Next Steps
----------

**Immediate (next 30 minutes):**

1. :doc:`Add real hardware devices <creating_devices>` - Connect to EPICS PVs
2. :doc:`Configure area detectors <area_detectors>` - Set up cameras and file writing
3. :doc:`Create alignment plans <creating_plans>` - Use apstools alignment tools

**Short term (next few hours):**

4. :doc:`Set up data management <dm>` - Integrate with facility data systems
5. :doc:`Configure production settings <setting_iconfig>` - Environment detection
6. :doc:`Deploy with queue server <qserver>` - Multi-user production setup

**Advanced (next few days):**

7. :doc:`Multi-beamline architecture <common_instruments>` - Shared components
8. :doc:`Production deployment <deployment_patterns>` - Best practices
9. :doc:`AI integration <bait_integration>` - Automated analysis with bAIt

Common First Issues and Solutions
--------------------------------

**Problem: Import errors after creating devices**

.. code-block:: bash

    # Solution: Reinstall the package
    pip install -e .

**Problem: EPICS connection timeouts**

.. code-block:: python

    # Solution: Use SIM: prefix for testing
    # In devices.yml, use "SIM:DEVICE" instead of real PV names

**Problem: Plans not found after creation**

.. code-block:: python

    # Solution: Check imports in plans/__init__.py
    from .my_plans import my_plan_name

**Problem: Queue server won't start**

.. code-block:: bash

    # Solution: Check permissions and conda environment
    chmod +x qs_host.sh
    conda activate bits_env

Getting Help
------------

- **Documentation**: :doc:`Complete guides <index>` for detailed information
- **Examples**: Look in `apsbits/demo_instrument/` for working examples
- **Issues**: Report problems at https://github.com/BCDA-APS/BITS/issues
- **Community**: APS Bluesky user community and beamline staff

**Ready to dive deeper?** Start with :doc:`creating_instrument` for comprehensive instrument development patterns.
