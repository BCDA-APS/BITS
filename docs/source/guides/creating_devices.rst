.. _creating_devices:

Creating and Managing BITS Devices
===================================

This comprehensive guide covers device creation in BITS, from simple custom devices to advanced patterns using apstools.

Quick Start: Add a Device in 3 Steps
-------------------------------------

**Add a new device to your instrument:**

.. code-block:: python

    # 1. Create device in devices/my_device.py
    from ophyd import Device, EpicsMotor
    from ophyd import Component as Cpt

    class StageXY(Device):
        x = Cpt(EpicsMotor, ':X')
        y = Cpt(EpicsMotor, ':Y')

.. code-block:: yaml

    # 2. Add to configs/devices.yml
    my_instrument.devices.StageXY:
    - name: stage
      prefix: "IOC:STAGE"
      labels: ["motors"]

.. code-block:: bash

    # 3. Restart instrument to load
    python -c "from my_instrument.startup import *; print(stage.x.position)"

Complete Device Creation Guide
-------------------------------

Understanding BITS Device Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BITS devices follow a three-layer architecture:

1. **Device Classes** - Python classes defining device behavior
2. **Configuration Files** - YAML files specifying device instances
3. **Runtime Objects** - Actual device objects created at startup

.. code-block:: text

    src/my_instrument/
    ├── devices/              # Layer 1: Device class definitions
    │   ├── __init__.py       # Import device classes
    │   ├── motors.py         # Motor device classes
    │   ├── detectors.py      # Detector device classes
    │   └── custom.py         # Instrument-specific devices
    ├── configs/              # Layer 2: Device configurations
    │   ├── devices.yml       # General device instances
    │   └── devices_aps_only.yml  # APS subnet-specific devices
    └── startup.py            # Layer 3: Runtime instantiation

Using apstools Devices (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**apstools provides 50+ pre-built device classes for common APS hardware:**

.. code-block:: yaml

    # configs/devices.yml - Use apstools devices directly
    apstools.synApps.Optics2Slit2D_HV:
    - name: primary_slits
      prefix: "IOC:SLIT1"
      labels: ["slits", "optics"]

    apstools.devices.ApsMachineParametersDevice:
    - name: aps_status
      labels: ["baseline", "machine"]

    apstools.devices.EpicsMotorDevice:
    - name: sample_x
      prefix: "IOC:SAMPLE:X"
      labels: ["motors", "sample"]

**Motor Bundle Factory (Recommended for Multi-Axis Systems):**

.. code-block:: python

    # devices/stages.py - Using apstools motor factory
    from apstools.devices import mb_creator

    # Create multi-axis stage using factory
    xy_stage = mb_creator(
        prefix="IOC:STAGE:",
        motors={"x": "X", "y": "Y"},
        name="xy_stage"
    )

    # Advanced motor bundle with mixed types
    complex_stage = mb_creator(
        prefix="IOC:",
        motors={
            "x": "SAMPLE:X",      # EpicsMotor
            "y": "SAMPLE:Y",      # EpicsMotor
            "z": {"class": "SoftPositioner", "init": {"initial": 0}}  # Simulated
        },
        name="sample_stage"
    )

**Advanced Motor Factory Patterns (from apstools):**

.. code-block:: python

    # Per-axis configuration with different motor types
    advanced_stage = mb_creator(
        prefix="255idc:m",
        motors={
            # Simple motor - just PV suffix
            "x": "21",

            # Motor with custom parameters
            "y": {
                "prefix": "22",
                "class": "ophyd.EpicsMotor",
                "kind": "hinted",
                "labels": ["sample", "alignment"]
            },

            # Simulated motor for development
            "z": {
                "class": "ophyd.SoftPositioner",
                "init_pos": 0.0,
                "labels": ["sample", "simulated"]
            },

            # Motor with factory function
            "theta": {
                "factory": {
                    "function": "my_package.create_special_motor",
                    "encoder_resolution": 0.001,
                    "backlash": 0.05
                }
            }
        },
        class_bases=["ophyd.Device"],  # Use Device instead of MotorBundle
        class_name="AdvancedStage",
        name="sample_stage"
    )

**Custom Base Classes and Mixins:**

.. code-block:: python

    # Using apstools motor mixins for enhanced functionality
    from apstools.devices import mb_creator, EpicsMotorDialMixin

    # Stage with dial coordinate access
    dial_stage = mb_creator(
        prefix="IOC:STAGE:",
        motors={"x": "X", "y": "Y", "z": "Z"},
        class_bases=["ophyd.MotorBundle", "apstools.devices.EpicsMotorDialMixin"],
        class_name="DialStage",
        name="sample_stage_with_dial"
    )

    # Access both user and dial coordinates
    print(f"User X: {dial_stage.x.position}")
    print(f"Dial X: {dial_stage.x.dial_position}")

**Dynamic Motor Configuration:**

.. code-block:: python

    # Factory function for configurable motor systems
    def create_motor_bundle_from_config(config_dict):
        """Create motor bundle from configuration dictionary."""

        return mb_creator(
            prefix=config_dict.get("prefix", ""),
            motors=config_dict.get("motors", {}),
            name=config_dict.get("name", "motor_bundle"),
            labels=config_dict.get("labels", ["motors"]),
            class_bases=config_dict.get("base_classes", ["ophyd.MotorBundle"])
        )

    # Example: Load from instrument configuration
    from apsbits.utils.config_loaders import get_config

    iconfig = get_config()
    stage_config = iconfig.get("SAMPLE_STAGE", {
        "prefix": "IOC:SAMPLE:",
        "name": "sample_manipulator",
        "motors": {
            "x": {"prefix": "X", "labels": ["horizontal"]},
            "y": {"prefix": "Y", "labels": ["vertical"]},
            "z": {"prefix": "Z", "labels": ["depth"]},
            "rx": {"prefix": "RX", "labels": ["rotation"]},
            "ry": {"prefix": "RY", "labels": ["rotation"]}
        }
    })

    sample_stage = create_motor_bundle_from_config(stage_config)

**Area Detector Factory:**

.. code-block:: python

    # devices/detectors.py - Using apstools area detector factory
    from apstools.devices import ad_creator

    pilatus = ad_creator(
        "IOC:PILATUS:",
        name="pilatus",
        detector_class="PilatusDetectorCam",
        plugins=["image", "stats", "roi"]
    )

Creating Custom Devices
~~~~~~~~~~~~~~~~~~~~~~~~

**Simple Custom Devices:**

When apstools doesn't have what you need:

.. code-block:: python

    # devices/sample_environment.py
    from ophyd import Device, EpicsMotor, EpicsSignal
    from ophyd import Component as Cpt
    import logging

    logger = logging.getLogger(__name__)
    logger.info(__file__)  # BITS logging convention

    class SampleEnvironment(Device):
        """Custom sample environment controller."""

        # Temperature control
        temperature = Cpt(EpicsSignal, ":TEMP:RBV", write_pv=":TEMP:SP")
        temp_status = Cpt(EpicsSignal, ":TEMP:STATUS")

        # Sample positioning
        x = Cpt(EpicsMotor, ":X")
        y = Cpt(EpicsMotor, ":Y")
        theta = Cpt(EpicsMotor, ":THETA")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Custom initialization
            self.temperature.limits = (5, 300)  # Celsius

**Version Compatibility with Mixins:**

Handle EPICS version differences using apstools mixins:

.. code-block:: python

    # devices/area_detector.py - Version compatibility pattern
    from apstools.devices import CamMixin_V34
    from ophyd.areadetector import CamBase
    from ophyd.areadetector.cam import PilatusDetectorCam

    class CamUpdates_V34(CamMixin_V34, CamBase):
        """Updates to CamBase for Area Detector 3.4+"""
        pool_max_buffers = None  # Removed in AD 3.4

    class BeamlinePilatusCam_V34(CamUpdates_V34, PilatusDetectorCam):
        """Pilatus detector optimized for this beamline."""

        def stage(self):
            # Custom staging logic
            self.acquire_time.put(0.1)  # Default exposure
            super().stage()

**Advanced Device Patterns:**

.. code-block:: python

    # devices/complex_device.py - Advanced patterns
    from apstools.devices import AxisTunerDevice
    from apstools.synApps import SscanDevice
    from ophyd import Device, Component as Cpt

    class OptimizedBeamlineDevice(Device):
        """Complex device with auto-alignment capabilities."""

        # Motor with auto-alignment
        motor = Cpt(EpicsMotor, ":MOTOR")
        tuner = Cpt(AxisTunerDevice, ":TUNE")

        # EPICS sscan record integration
        sscan1 = Cpt(SscanDevice, ":SSCAN1")

        def auto_align(self, detector, range_mm=2.0):
            """Auto-alignment using apstools tuner."""
            return self.tuner.tune(
                detector=detector,
                axis=self.motor,
                range_mm=range_mm
            )

Device Configuration Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Basic Configuration:**

.. code-block:: yaml

    # configs/devices.yml
    my_instrument.devices.SampleEnvironment:
    - name: sample_env
      prefix: "IOC:SAMPLE"
      labels: ["environment", "baseline"]

    # External package devices
    apstools.devices.EpicsMotorDevice:
    - name: theta
      prefix: "IOC:THETA"
      labels: ["motors", "sample"]

**Environment-Specific Configuration:**

.. code-block:: yaml

    # configs/devices_aps_only.yml - Only loaded on APS subnet
    apstools.devices.ApsMachineParametersDevice:
    - name: aps_status
      labels: ["baseline", "machine"]

    # Production detector (real hardware)
    my_instrument.devices.RealDetector:
    - name: detector
      prefix: "IOC:DETECTOR"
      labels: ["detectors", "primary"]

.. code-block:: python

    # startup.py - Environment detection
    from apsbits.utils.aps_functions import host_on_aps_subnet

    if host_on_aps_subnet():
        # Load production devices
        make_devices(device_file="configs/devices_aps_only.yml")
    else:
        # Development mode uses simulated devices
        print("Development mode: using simulation devices")

**Advanced Configuration Options:**

.. code-block:: yaml

    # configs/devices.yml - Advanced patterns
    apstools.devices.mb_creator:
    - name: sample_stage
      # Motor bundle factory configuration
      prefix: "IOC:STAGE:"
      motors:
        x: "X"
        y: "Y"
        z: "Z"
      labels: ["motors", "sample"]

    # Custom initialization arguments
    my_instrument.devices.CustomDetector:
    - name: special_detector
      prefix: "IOC:DET"
      # Pass custom arguments to __init__
      init_kwargs:
        exposure_time: 0.1
        roi_size: [512, 512]
      labels: ["detectors", "custom"]

Device Import and Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Device Module Organization:**

.. code-block:: python

    # devices/__init__.py - Import pattern
    """Device definitions for instrument."""

    # Import custom devices
    from .motors import SampleStage, GoniometerDevice
    from .detectors import CustomPilatus, FastCCD
    from .environment import SampleHeater, CryoController

    # Import from common packages
    from beamline_common.devices import SharedOptics

    # Re-export for easy access
    __all__ = [
        "SampleStage", "GoniometerDevice",
        "CustomPilatus", "FastCCD",
        "SampleHeater", "CryoController",
        "SharedOptics"
    ]

**Conditional Imports:**

.. code-block:: python

    # devices/optional.py - Handle optional dependencies
    try:
        from specialized_package import SpecialDetector
        HAS_SPECIAL_DETECTOR = True
    except ImportError:
        logger.warning("specialized_package not available")
        HAS_SPECIAL_DETECTOR = False

        # Provide fallback
        class SpecialDetector:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("specialized_package not installed")

Device Testing and Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Testing Device Creation:**

.. code-block:: python

    # Test device instantiation
    from my_instrument.devices import SampleEnvironment

    # Test with simulated PV (no EPICS required)
    device = SampleEnvironment("SIM:SAMPLE", name="test_sample")

    # Verify components
    print(f"Temperature signal: {device.temperature}")
    print(f"Motor components: {device.x}, {device.y}")

**Validation in Startup:**

.. code-block:: python

    # startup.py - Device validation
    def validate_devices():
        """Check that all devices are properly connected."""

        failed_devices = []
        for name, device in oregistry.findall():
            try:
                # Test connection
                device.wait_for_connection(timeout=1.0)
            except Exception as e:
                failed_devices.append((name, str(e)))

        if failed_devices:
            logger.warning(f"Failed to connect to devices: {failed_devices}")

    # Run validation after device creation
    validate_devices()

Baseline and Metadata Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Baseline Devices:**

Automatically tracked during scans:

.. code-block:: yaml

    # configs/devices.yml - Baseline tracking
    apstools.devices.ApsMachineParametersDevice:
    - name: aps_status
      labels: ["baseline"]  # Automatically included in scan metadata

    my_instrument.devices.SampleEnvironment:
    - name: sample_env
      labels: ["environment", "baseline"]

**Custom Metadata:**

.. code-block:: python

    # devices/metadata.py - Custom metadata collection
    from ophyd import Device, Component as Cpt, Signal

    class InstrumentMetadata(Device):
        """Collect instrument-specific metadata."""

        # Software versions
        bluesky_version = Cpt(Signal, value="", kind="config")
        instrument_version = Cpt(Signal, value="", kind="config")

        # Environmental conditions
        hutch_temperature = Cpt(EpicsSignal, ":TEMP:HUTCH")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Set software versions
            import bluesky
            self.bluesky_version.put(bluesky.__version__)

Troubleshooting Device Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common Issues:**

1. **Import Errors:**

   .. code-block:: python

       # Check device class is importable
       from my_instrument.devices import MyDevice
       print(MyDevice)

2. **EPICS Connection Failures:**

   .. code-block:: bash

       # Test EPICS connectivity
       caget IOC:DEVICE:PV

       # Check EPICS environment
       echo $EPICS_CA_ADDR_LIST

3. **Configuration Errors:**

   .. code-block:: python

       # Validate YAML syntax
       import yaml
       config = yaml.safe_load(open("configs/devices.yml"))
       print(config)

4. **Device Instantiation Failures:**

   .. code-block:: python

       # Debug device creation
       import logging
       logging.basicConfig(level=logging.DEBUG)

       from my_instrument.startup import *

**AI-Assisted Device Analysis:**

Use bAIt for device validation:

.. code-block:: python

    # bAIt device analysis
    from bait_base.analyzers import DeviceAnalyzer

    analyzer = DeviceAnalyzer()
    result = analyzer.analyze("src/my_instrument/devices/")

    # Get recommendations
    for recommendation in result.recommendations:
        print(f"💡 {recommendation}")

Advanced Topics
~~~~~~~~~~~~~~~

**Device Factory Patterns:**

.. code-block:: python

    # devices/factories.py - Custom device factories
    def create_motor_bundle(prefix, motor_names):
        """Factory for creating motor bundles."""
        return mb_creator(
            prefix=prefix,
            motors={name: name.upper() for name in motor_names},
            name=f"{prefix.lower()}_motors"
        )

**Plugin Architecture:**

.. code-block:: python

    # devices/plugins.py - Extensible device architecture
    class DevicePlugin:
        """Base class for device plugins."""
        def configure(self, device):
            pass

    class AutoAlignPlugin(DevicePlugin):
        """Add auto-alignment to any motor."""
        def configure(self, device):
            device.auto_align = lambda: align_motor(device)

**Asynchronous Device Operations:**

.. code-block:: python

    # devices/async_device.py - Async device patterns
    from ophyd.status import StatusBase

    class AsyncDevice(Device):
        """Device with asynchronous operations."""

        def trigger(self):
            """Non-blocking trigger operation."""
            status = StatusBase()

            # Simulate async operation
            import threading
            def complete_later():
                time.sleep(1.0)
                status._finished()

            threading.Thread(target=complete_later).start()
            return status

Best Practices Summary
~~~~~~~~~~~~~~~~~~~~~~

**DO:**
- Use apstools devices when available (50+ pre-built classes)
- Follow BITS logging conventions (``logger.info(__file__)``)
- Include version compatibility patterns
- Test device creation without hardware dependencies
- Use baseline labels for automatic metadata collection

**DON'T:**
- Create custom devices when apstools has equivalent functionality
- Hardcode EPICS PV names in device classes (use configuration files)
- Skip error handling in device initialization
- Forget to handle EPICS version compatibility

**Next Steps:**

1. :doc:`Create scan plans using your devices <creating_plans>`
2. :doc:`Set up area detector configurations <area_detectors>`
3. :doc:`Integrate with data management systems <dm>`
4. :doc:`Deploy with queue server support <qserver>`
