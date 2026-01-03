.. _troubleshooting:

BITS Troubleshooting Guide
===========================

Comprehensive troubleshooting guide for BITS instruments, covering common issues across apstools, guarneri, and deployment patterns.

Quick Issue Resolution
----------------------

**Most Common Problems:**

.. code-block:: bash

    # 1. Import errors after adding devices
    pip install -e .              # Reinstall package

    # 2. EPICS connection timeouts
    # Use SIM: prefix for testing without hardware

    # 3. Queue server won't start
    chmod +x qs_host.sh           # Fix permissions
    conda activate bits_env       # Check environment

    # 4. Device not found after configuration
    python -c "from my_instrument.startup import *; print(globals().keys())"

Installation and Environment Issues
-----------------------------------

Package Installation Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem: Missing dependencies after installation**

.. code-block:: bash

    # Symptoms
    ImportError: No module named 'apstools'
    ModuleNotFoundError: No module named 'apsbits'

.. code-block:: bash

    # Solution: Complete environment setup
    conda create -y -n bits_env python=3.11 pyepics
    conda activate bits_env
    pip install apsbits[all]  # Install with all dependencies

**Problem: Development installation not working**

.. code-block:: bash

    # Symptoms
    python -c "import my_instrument" fails
    Changes to code not reflected

.. code-block:: bash

    # Solution: Proper editable installation
    cd /path/to/my_instrument
    pip install -e .

    # Verify installation
    python -c "import my_instrument; print(my_instrument.__file__)"

**Problem: Version conflicts between packages**

.. code-block:: bash

    # Symptoms
    ImportError: cannot import name 'Device' from 'ophyd'
    AttributeError: module 'bluesky' has no attribute 'plans'

.. code-block:: bash

    # Solution: Check and fix version compatibility
    pip install --upgrade bluesky ophyd apstools

    # Check versions
    python -c "import bluesky, ophyd, apstools; print(f'BS: {bluesky.__version__}, Ophyd: {ophyd.__version__}, APS: {apstools.__version__}')"

EPICS and Device Connection Issues
----------------------------------

EPICS Connection Problems
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem: EPICS PV connection timeouts**

.. code-block:: python

    # Symptoms
    EpicsMotor('IOC:MOTOR', name='motor') times out
    ophyd.utils.errors.TimeoutError: Unable to connect to PV 'IOC:MOTOR.RBV'

.. code-block:: python

    # Diagnosis: Check PV existence
    import epics

    # Test PV connectivity
    pv = epics.PV('IOC:MOTOR.RBV')
    if pv.connected:
        print(f"PV connected: {pv.value}")
    else:
        print("PV not available")

    # Check EPICS environment
    import os
    print(f"EPICS_CA_ADDR_LIST: {os.getenv('EPICS_CA_ADDR_LIST', 'Not set')}")
    print(f"EPICS_CA_AUTO_ADDR_LIST: {os.getenv('EPICS_CA_AUTO_ADDR_LIST', 'YES')}")

.. code-block:: bash

    # Solution: EPICS environment setup
    export EPICS_CA_ADDR_LIST="164.54.160.255"  # APS broadcast address
    export EPICS_CA_AUTO_ADDR_LIST="NO"

    # Or use simulation for development
    # In configs/devices.yml, use prefix: "SIM:MOTOR" instead

**Problem: Intermittent connection failures**

.. code-block:: python

    # Solution: Robust connection with retries
    from ophyd import EpicsMotor
    import time
    import logging

    logger = logging.getLogger(__name__)

    def create_motor_with_retry(prefix, name, max_retries=3):
        """Create motor with connection retry logic."""

        for attempt in range(max_retries):
            try:
                motor = EpicsMotor(prefix, name=name)
                motor.wait_for_connection(timeout=5)
                logger.info(f"Motor {name} connected on attempt {attempt + 1}")
                return motor

            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    logger.error(f"Failed to connect {name} after {max_retries} attempts")
                    raise

**Problem: Slow device connection during startup**

.. code-block:: python

    # Solution: Parallel device connection with Guarneri
    from guarneri import Instrument
    import asyncio

    async def fast_device_loading():
        """Load devices in parallel for faster startup."""

        instrument = Instrument(device_classes)
        instrument.load("configs/devices.toml")

        # Connect all devices in parallel
        start_time = time.time()
        await instrument.connect(timeout=30)
        end_time = time.time()

        print(f"Connected {len(instrument.devices)} devices in {end_time - start_time:.1f} seconds")

Device Configuration Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem: Device not appearing in startup namespace**

.. code-block:: python

    # Symptoms
    NameError: name 'my_motor' is not defined
    # After adding device to configs/devices.yml

.. code-block:: python

    # Diagnosis: Check device registration
    from apsbits.utils.device_registry import device_registry

    print("Registered devices:")
    for name, device in device_registry.items():
        print(f"  {name}: {device}")

.. code-block:: python

    # Solution: Verify device configuration and imports
    # 1. Check devices/__init__.py imports
    from .my_devices import MyMotor  # Must be imported

    # 2. Check configs/devices.yml syntax
    # Correct format:
    my_instrument.devices.MyMotor:
    - name: my_motor
      prefix: "IOC:MOTOR"

    # 3. Reinstall package
    # pip install -e .

**Problem: Motor factory not creating expected axes**

.. code-block:: python

    # Symptoms
    AttributeError: 'MB_Device' object has no attribute 'x'
    # When using mb_creator

.. code-block:: python

    # Diagnosis and solution
    from apstools.devices import mb_creator

    # Check motor bundle creation
    stage = mb_creator(
        prefix="IOC:STAGE:",
        motors={"x": "X", "y": "Y"},  # Ensure correct mapping
        name="xy_stage"
    )

    print(f"Available axes: {[attr for attr in dir(stage) if not attr.startswith('_')]}")
    print(f"Motor x: {hasattr(stage, 'x')}")
    print(f"Motor y: {hasattr(stage, 'y')}")

Area Detector Issues
~~~~~~~~~~~~~~~~~~~~

**Problem: Area detector file writing not working**

.. code-block:: python

    # Symptoms
    Area detector doesn't save files
    HDF5 plugin not writing data

.. code-block:: python

    # Solution: Proper area detector configuration
    from apstools.devices import AD_EpicsHdf5FileName, ensure_AD_plugin_primed

    # Ensure HDF5 plugin is properly configured
    ensure_AD_plugin_primed(detector.hdf5, True, 5.0)  # Prime with timeout

    # Configure file writing
    detector.hdf5.file_path.put("/data/detector/")
    detector.hdf5.file_name.put("test_image")
    detector.hdf5.file_template.put("%s%s_%06d.h5")
    detector.hdf5.enable.put("Enable")
    detector.hdf5.capture.put("Capture")

**Problem: Area detector version compatibility**

.. code-block:: python

    # Symptoms
    AttributeError: 'CamBase' object has no attribute 'pool_max_buffers'
    # When using Area Detector 3.4+

.. code-block:: python

    # Solution: Use version-specific mixins
    from apstools.devices import CamMixin_V34
    from ophyd.areadetector import CamBase

    class ModernCam(CamMixin_V34, CamBase):
        """Area Detector cam for AD 3.4+"""
        pass

    # Or use area detector factory
    from apstools.devices import ad_creator

    detector = ad_creator(
        prefix="IOC:AD:",
        name="area_detector",
        plugins=["image", "hdf5", "stats"],
        version="3.4"  # Specify AD version
    )

Plan and Execution Issues
-------------------------

Plan Execution Problems
~~~~~~~~~~~~~~~~~~~~~~~

**Problem: Plans not found or import errors**

.. code-block:: python

    # Symptoms
    NameError: name 'my_scan_plan' is not defined
    ImportError: cannot import name 'my_scan_plan'

.. code-block:: python

    # Solution: Check plan imports
    # 1. Verify plans/__init__.py
    from .my_plans import my_scan_plan
    __all__ = ["my_scan_plan"]

    # 2. Check plan definition
    def my_scan_plan(detector, motor):
        """Proper plan with yield from."""
        yield from count([detector], 1)

    # 3. Reinstall if needed
    # pip install -e .

**Problem: Plans failing with motor movement errors**

.. code-block:: python

    # Symptoms
    FailedStatus: EpicsMotor(prefix='IOC:MOTOR', name='motor') is not done moving
    ophyd.status.StatusTimeoutError: Status object timed out

.. code-block:: python

    # Solution: Check motor limits and status
    def diagnose_motor_issues(motor):
        """Diagnose motor problems."""

        print(f"Motor: {motor.name}")
        print(f"Position: {motor.position}")
        print(f"Connected: {motor.connected}")
        print(f"Moving: {motor.moving}")
        print(f"Limits: {motor.limits}")
        print(f"Low limit switch: {motor.low_limit_switch.get()}")
        print(f"High limit switch: {motor.high_limit_switch.get()}")

        # Check for common issues
        if not motor.connected:
            print("❌ Motor not connected")
        if motor.position == motor.high_limit:
            print("⚠️  Motor at high limit")
        if motor.position == motor.low_limit:
            print("⚠️  Motor at low limit")

    # Use in plan for debugging
    yield from bps.call(diagnose_motor_issues, motor)

**Problem: Alignment plans not finding peaks**

.. code-block:: python

    # Symptoms
    apstools lineup2 plan doesn't find optimal position
    TuneAxis returns to original position

.. code-block:: python

    # Solution: Check signal and tune parameters
    from apstools.plans import lineup2, TuneAxis
    from bluesky import plan_stubs as bps

    def debug_alignment(detector, motor):
        """Debug alignment plan issues."""

        # Check current signal level
        signal_pv = detector.stats1.total
        current_signal = yield from bps.rd(signal_pv)
        print(f"Current signal: {current_signal}")

        # Manual scan to check signal variation
        positions = []
        signals = []
        for pos in [-1, -0.5, 0, 0.5, 1.0]:
            yield from bps.mv(motor, pos)
            signal = yield from bps.rd(signal_pv)
            positions.append(pos)
            signals.append(signal)
            print(f"Position {pos}: Signal {signal}")

        # Check if there's sufficient signal variation
        signal_range = max(signals) - min(signals)
        if signal_range < 10:  # Adjust threshold as needed
            print("⚠️  Low signal variation - check detector setup")

Queue Server Issues
-------------------

Queue Server Startup Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem: Queue server fails to start**

.. code-block:: bash

    # Symptoms
    ./qs_host.sh fails
    Permission denied errors
    Port already in use errors

.. code-block:: bash

    # Solution: Check startup script and environment
    chmod +x qs_host.sh                    # Fix permissions

    # Check if ports are available
    netstat -tuln | grep 60615            # Control port
    netstat -tuln | grep 60616            # Data port

    # Kill existing queue server if needed
    pkill -f queueserver

    # Check conda environment
    conda activate bits_env
    which qserver                          # Verify qserver available

**Problem: Queue server environment not starting**

.. code-block:: bash

    # Symptoms
    Environment startup fails
    Import errors in queue server environment

.. code-block:: bash

    # Solution: Check startup script
    # In src/my_instrument_qserver/qs_host.sh
    export CONDA_ENV_NAME="bits_env"
    export QSERVER_STARTUP_SCRIPT="startup.py"

    # Verify startup script works independently
    cd src/my_instrument_qserver
    python startup.py  # Should work without errors

Data Management and Workflow Issues
-----------------------------------

Data Management Integration Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem: Data management workflow not starting**

.. code-block:: python

    # Symptoms
    DM workflow connector not responding
    Workflow status remains 'unknown'

.. code-block:: python

    # Solution: Check DM workflow configuration
    from apstools.devices import DM_WorkflowConnector
    from bluesky import plan_stubs as bps

    def check_dm_workflow():
        """Check data management workflow status."""

        dm_workflow = DM_WorkflowConnector(name="dm_workflow")

        # Check connection
        try:
            yield from bps.rd(dm_workflow.workflow)
            print("DM workflow connected")
        except Exception as e:
            print(f"DM workflow connection failed: {e}")

        # Check available workflows
        try:
            workflows = yield from bps.rd(dm_workflow.workflows_available)
            print(f"Available workflows: {workflows}")
        except Exception as e:
            print(f"Could not get workflows: {e}")

**Problem: File writing permissions**

.. code-block:: python

    # Symptoms
    Permission denied when writing data files
    HDF5 file creation fails

.. code-block:: bash

    # Solution: Check directory permissions
    ls -la /data/detector/                 # Check directory permissions
    sudo chmod 755 /data/detector/         # Fix if needed
    sudo chown detector:users /data/detector/  # Fix ownership

    # Create test file
    touch /data/detector/test_file.txt
    rm /data/detector/test_file.txt

Performance and Resource Issues
-------------------------------

Memory and Performance Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem: High memory usage during scans**

.. code-block:: python

    # Symptoms
    System becomes slow during large scans
    Out of memory errors

.. code-block:: python

    # Solution: Monitor and optimize memory usage
    import psutil
    import gc

    def monitor_memory_usage():
        """Monitor memory usage during scans."""

        process = psutil.Process()
        memory_info = process.memory_info()

        print(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
        print(f"Virtual memory: {memory_info.vms / 1024 / 1024:.1f} MB")

        # Force garbage collection
        gc.collect()

        return memory_info.rss

**Problem: Slow device communication**

.. code-block:: python

    # Solution: Optimize device communication
    from ophyd import EpicsMotor

    # Use faster polling for critical devices
    motor = EpicsMotor('IOC:MOTOR', name='motor')
    motor.poll_rate = 0.1  # Poll every 100ms instead of default

    # Use read-only signals where appropriate
    motor.user_readback.subscribe(lambda **kwargs: None)  # Remove unnecessary subscriptions

AI Integration and Development Tools
------------------------------------

bAIt Integration Issues
~~~~~~~~~~~~~~~~~~~~~~~

**Problem: bAIt analysis not finding deployment**

.. code-block:: bash

    # Symptoms
    bait-analyze fails to find instrument configuration
    "No deployment found" errors

.. code-block:: bash

    # Solution: Check bAIt deployment configuration
    # Verify deployment structure
    ls -la bait_deployments/my_beamline/
    cat bait_deployments/my_beamline/config.json

    # Update deployment configuration
    bait-update-deployment my_beamline

**Problem: AI recommendations not relevant**

.. code-block:: python

    # Solution: Improve AI context with better metadata
    # Add comprehensive metadata to devices and plans
    motor.labels = ["sample", "alignment", "critical"]  # Better labeling

    # Document device purpose in docstrings
    class SampleMotor(EpicsMotor):
        """Sample positioning motor for X-ray alignment.

        Critical for beam-sample alignment procedures.
        Used in automated alignment workflows.
        """

Advanced Debugging Techniques
-----------------------------

Comprehensive Debugging Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # utils/debug_tools.py - Comprehensive debugging utilities
    import logging
    import sys
    import traceback
    from functools import wraps

    # Enhanced logging setup
    def setup_debug_logging(level=logging.DEBUG):
        """Setup comprehensive debug logging."""

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler('instrument_debug.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        # Enable ophyd debug logging
        logging.getLogger('ophyd').setLevel(logging.DEBUG)
        logging.getLogger('bluesky').setLevel(logging.INFO)

    def debug_plan(func):
        """Decorator to add debug information to plans."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)

            try:
                logger.info(f"Starting plan {func.__name__} with args={args}, kwargs={kwargs}")
                result = yield from func(*args, **kwargs)
                logger.info(f"Plan {func.__name__} completed successfully")
                return result

            except Exception as e:
                logger.error(f"Plan {func.__name__} failed: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

        return wrapper

**System Health Check:**

.. code-block:: python

    def comprehensive_health_check():
        """Comprehensive system health check."""

        health_report = []

        # Check Python environment
        health_report.append(f"Python version: {sys.version}")

        # Check critical packages
        try:
            import bluesky, ophyd, apstools
            health_report.append(f"✓ Bluesky {bluesky.__version__}")
            health_report.append(f"✓ Ophyd {ophyd.__version__}")
            health_report.append(f"✓ apstools {apstools.__version__}")
        except ImportError as e:
            health_report.append(f"❌ Package import failed: {e}")

        # Check EPICS environment
        import os
        epics_vars = ['EPICS_CA_ADDR_LIST', 'EPICS_CA_AUTO_ADDR_LIST', 'EPICS_CA_MAX_ARRAY_BYTES']
        for var in epics_vars:
            value = os.getenv(var, 'Not set')
            health_report.append(f"EPICS {var}: {value}")

        # Check device connections
        from apsbits.utils.device_registry import device_registry
        connected_devices = sum(1 for device in device_registry.values() if device.connected)
        total_devices = len(device_registry)
        health_report.append(f"Device connections: {connected_devices}/{total_devices}")

        # Memory usage
        import psutil
        memory = psutil.virtual_memory()
        health_report.append(f"Memory usage: {memory.percent}% ({memory.used // 1024 // 1024} MB used)")

        return '\n'.join(health_report)

Getting Help and Support
------------------------

**Resources:**

1. **Documentation**: Complete BITS guides at :doc:`index`
2. **Examples**: Working examples in `apsbits/demo_instrument/`
3. **Issues**: Report problems at https://github.com/BCDA-APS/BITS/issues
4. **Community**: APS Bluesky user community and beamline staff

**Before Reporting Issues:**

1. Run comprehensive health check
2. Enable debug logging
3. Test with simulated devices
4. Check similar reported issues
5. Include complete error messages and logs

**Emergency Debugging Commands:**

.. code-block:: bash

    # Quick system check
    python -c "import my_instrument.startup; print('✓ Instrument loads')"

    # Check device registry
    python -c "from apsbits.utils.device_registry import device_registry; print(f'{len(device_registry)} devices registered')"

    # Test EPICS connectivity
    python -c "import epics; pv = epics.PV('SIM:detector:cam1:Acquire'); print(f'EPICS test: {pv.connected}')"
