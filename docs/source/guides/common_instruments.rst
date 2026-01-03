.. _common_instruments:

Common Instrument Patterns
===========================

This guide explains how to create "common" instrument packages for shared components across multiple beamline instruments, based on successful deployment patterns at APS.

Quick Start: When to Use Common Packages
-----------------------------------------

**Use common packages when you have:**

- Multiple endstations sharing hardware (slits, monochromators, detectors)
- Standardized procedures across experimental techniques
- Beamline-wide calibration and alignment protocols

**Create a common package in 4 commands:**

.. code-block:: bash

    mkdir -p src/beamline_common/{devices,plans}
    echo '"""Support for beamline instruments."""' > src/beamline_common/__init__.py
    touch src/beamline_common/devices/__init__.py
    touch src/beamline_common/plans/__init__.py

**Use the common package:**

.. code-block:: python

    # In src/endstation_a/startup.py
    from beamline_common.devices import SharedOptics
    from beamline_common.plans import standard_alignment

Complete Common Instrument Guide
---------------------------------

Understanding Common Package Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common packages contain **reusable components** but are **not instruments themselves**:

.. code-block:: text

    multi-beamline-project/
    ├── src/
    │   ├── id12_common/              # Shared 12-ID components
    │   │   ├── __init__.py           # "Support for 12-ID instruments"
    │   │   ├── devices/              # Shared hardware definitions
    │   │   │   ├── area_detector.py  # Common detector configurations
    │   │   │   ├── shutters.py       # Beamline shutter systems
    │   │   │   └── optics.py         # Shared optical components
    │   │   └── plans/                # Standardized procedures
    │   │       ├── alignment.py      # Common alignment protocols
    │   │       └── calibration.py    # Beamline-wide calibrations
    │   ├── id12_b/                   # Endstation B instrument
    │   │   ├── startup.py            # REQUIRED - actual instrument
    │   │   └── configs/iconfig.yml   # Endstation-specific config
    │   └── id12_e/                   # Endstation E instrument
    │       ├── startup.py            # REQUIRED - actual instrument
    │       └── configs/iconfig.yml   # Endstation-specific config

**Key Rules:**
- Common packages have **NO startup.py** - they're libraries, not instruments
- Common packages provide **shared components** for actual instruments
- Actual instruments **import from** common packages in their startup.py

Real-World Examples
~~~~~~~~~~~~~~~~~~~

**12-ID Multi-Endstation Pattern:**

Based on the successful 12-ID deployment:

.. code-block:: python

    # src/id12_common/devices/area_detector.py
    """EPICS area_detector definitions for 12-ID."""

    import logging
    from apstools.devices import CamMixin_V34
    from ophyd.areadetector import CamBase
    from ophyd.areadetector.cam import PilatusDetectorCam

    logger = logging.getLogger(__name__)
    logger.info(__file__)

    class CamUpdates_V34(CamMixin_V34, CamBase):
        """Updates to CamBase since v22. PVs removed from AD now."""
        pool_max_buffers = None

    class ID12_PilatusCam_V34(CamUpdates_V34, PilatusDetectorCam):
        """Pilatus Area Detector cam module for AD 3.4+"""
        pass

.. code-block:: python

    # src/id12_b/startup.py - Endstation B
    from apsbits.core.instrument_init import make_devices
    from id12_common.devices.area_detector import ID12_PilatusCam_V34

    # Use shared detector in endstation B
    pilatus_b = ID12_PilatusCam_V34("12IDB:cam1:", name="pilatus_b")

.. code-block:: python

    # src/id12_e/startup.py - Endstation E
    from apsbits.core.instrument_init import make_devices
    from id12_common.devices.area_detector import ID12_PilatusCam_V34

    # Same detector class, different PV prefix
    pilatus_e = ID12_PilatusCam_V34("12IDE:cam1:", name="pilatus_e")

**9-ID Multi-Technique Pattern:**

Based on the 9-ID deployment with multiple experimental techniques:

.. code-block:: python

    # src/common_9id/devices/sample_environment.py
    """Shared sample environment for 9-ID techniques."""

    from ophyd import Device, EpicsMotor, Component as Cpt

    class SampleStage(Device):
        """Multi-technique sample positioning system."""
        x = Cpt(EpicsMotor, "X}")
        y = Cpt(EpicsMotor, "Y}")
        theta = Cpt(EpicsMotor, "Theta}")

**Preferred YAML Configuration Approach:**

.. code-block:: yaml

    # src/common_9id/configs/devices.yml - YAML-first approach (Recommended)
    apstools.devices.motor_factory.mb_creator:
    - name: sample_stage
      prefix: "9ID:SampleStage:"
      motors:
        x: "X}"
        y: "Y}"
        theta: "Theta}"
      labels: ["motors", "sample", "positioning"]

.. code-block:: python

    # src/common_9id/plans/alignment.py
    """Standardized alignment procedures for all 9-ID techniques."""

    from bluesky import plan_stubs as bps
    from bluesky.plans import rel_scan

    def align_sample_position(detector, stage, range_mm=1.0):
        """Standard sample alignment for any 9-ID technique."""
        yield from rel_scan([detector], stage.x, -range_mm, range_mm, 21)
        yield from rel_scan([detector], stage.y, -range_mm, range_mm, 21)

.. code-block:: python

    # src/gisaxs/startup.py - GISAXS technique instrument
    from common_9id.devices.sample_environment import SampleStage
    from common_9id.plans.alignment import align_sample_position

    # Technique-specific detector
    gisaxs_detector = PilatusDetector("9IDGISAXS:", name="gisaxs")

    # Shared sample environment
    sample_stage = SampleStage("9ID:SampleStage:", name="stage")

Creating Common Device Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Shared Hardware Devices:**

For hardware used by multiple endstations:

.. code-block:: python

    # src/beamline_common/devices/shutters.py
    """Beamline shutter systems shared across endstations."""

    from apstools.devices import ApsPssShutterWithStatus

    class BeamlineShutter(ApsPssShutterWithStatus):
        """Standard beamline shutter with APS-specific logic."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add beamline-specific configuration
            self.delay_s = 0.1  # Beamline-specific timing

.. code-block:: python

    # src/beamline_common/devices/optics.py
    """Shared optical components."""

    from apstools.devices import SlitDevice

    class BeamlineSlits(SlitDevice):
        """Primary beamline slits used by all endstations."""

        # Override with beamline-specific limits
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.h_size.limits = (0, 20)  # mm
            self.v_size.limits = (0, 15)  # mm

**Version Compatibility Mixins:**

Handle EPICS version differences:

.. code-block:: python

    # src/beamline_common/devices/compatibility.py
    """Version compatibility helpers for beamline devices."""

    from apstools.devices import CamMixin_V34
    from ophyd.areadetector import CamBase

    class BeamlineCamBase_V34(CamMixin_V34, CamBase):
        """Updated CamBase for Area Detector 3.4+ at this beamline."""

        # Remove deprecated PVs
        pool_max_buffers = None

        # Add beamline-specific PVs if needed
        # custom_pv = Cpt(EpicsSignal, "CustomPV")

Creating Common Plan Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Standardized Procedures:**

For procedures used across all instruments:

.. code-block:: python

    # src/beamline_common/plans/alignment.py
    """Standard alignment procedures for the beamline."""

    from bluesky import plan_stubs as bps
    from apstools.plans import lineup2

    def beamline_alignment(detector, optics):
        """Standard beamline alignment procedure."""

        # Align primary optics
        yield from lineup2([detector], optics.h_center, -2, 2, 21)
        yield from lineup2([detector], optics.v_center, -2, 2, 21)

        # Record alignment metadata
        yield from bps.mv(optics.h_size, 1.0)  # Standard alignment aperture
        yield from bps.mv(optics.v_size, 1.0)

**Data Management Integration:**

Shared data management procedures:

.. code-block:: python

    # src/beamline_common/plans/data_management.py
    """Shared data management workflows."""

    from apstools.devices import DM_WorkflowConnector
    from bluesky import plan_stubs as bps

    def start_beamline_workflow(experiment_name, technique="general"):
        """Standard workflow startup for beamline data processing."""

        dm_workflow = DM_WorkflowConnector(name="dm_workflow")

        workflow_args = {
            "experimentName": experiment_name,
            "beamline": "your_beamline",
            "technique": technique,
        }

        yield from bps.mv(dm_workflow.workflows_root, "/path/to/workflows")
        yield from bps.mv(dm_workflow.workflow, "standard_processing")
        yield from bps.mv(dm_workflow.workflow_args, workflow_args)

Integration Patterns
~~~~~~~~~~~~~~~~~~~~

**Importing Common Components:**

In individual instrument startup files:

.. code-block:: python

    # src/technique_a/startup.py
    from apsbits.core.instrument_init import make_devices

    # Import shared components
    from beamline_common.devices.shutters import BeamlineShutter
    from beamline_common.devices.optics import BeamlineSlits
    from beamline_common.plans.alignment import beamline_alignment

    # Instantiate shared hardware
    shutter = BeamlineShutter("SHUTTER_PV:", name="shutter")
    slits = BeamlineSlits("SLIT_PV:", name="slits")

    # Technique-specific devices
    technique_detector = SpecialDetector("TECHNIQUE_A:", name="detector")

**Configuration Integration:**

Use common configurations with technique-specific overrides:

.. code-block:: yaml

    # src/technique_a/configs/iconfig.yml
    ICONFIG_VERSION: 2.0.0

    # Import common configuration patterns
    RUN_ENGINE:
        DEFAULT_METADATA:
            beamline_id: your_beamline
            technique: technique_a
            # Technique-specific metadata
            detector_type: special_detector

Package Dependencies
~~~~~~~~~~~~~~~~~~~~

**pyproject.toml Configuration:**

Each instrument package should depend on the common package:

.. code-block:: toml

    [project]
    name = "beamline-technique-a"
    dependencies = [
        "apsbits",
        "beamline-common"  # Internal dependency
    ]

**Development Installation:**

Install all related packages together:

.. code-block:: bash

    # Install common package first
    pip install -e src/beamline_common/

    # Install individual instruments
    pip install -e src/technique_a/
    pip install -e src/technique_b/

    # Or install everything together
    pip install -e .

AI Integration Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~

**bAIt Analysis Rules:**

AI agents should recognize these common package patterns:

.. code-block:: python

    # AI analysis patterns for common packages
    def analyze_common_package(package_path):
        """bAIt rules for analyzing common packages."""

        rules = {
            "no_startup_py": "Common packages should not have startup.py",
            "no_iconfig_yml": "Common packages should not have instrument configs",
            "shared_devices": "Devices should be reusable across instruments",
            "standard_plans": "Plans should be generic, not technique-specific",
            "proper_imports": "Use relative imports within common package",
            "documentation": "Common packages need usage examples"
        }

        return validate_against_rules(package_path, rules)

**Recommended Structure Validation:**

.. code-block:: python

    # AI recommendations for common package organization
    recommended_structure = {
        "devices/": "Hardware abstractions shared across instruments",
        "plans/": "Standardized procedures and workflows",
        "utils/": "Helper functions and utilities",
        "configs/": "Common configuration templates (optional)",
        "__init__.py": "Package documentation and purpose"
    }

Best Practices Summary
~~~~~~~~~~~~~~~~~~~~~~

**DO:**
- Create common packages for truly shared components
- Use descriptive names like ``beamline_common`` or ``facility_common``
- Include comprehensive documentation and examples
- Follow consistent naming conventions across the beamline
- Test common components with multiple instruments

**DON'T:**
- Include ``startup.py`` in common packages (they're not instruments)
- Mix technique-specific logic in common packages
- Create common packages for single-use components
- Forget to handle version compatibility in shared devices

**Next Steps:**

1. :doc:`Create custom devices in common packages <creating_devices>`
2. :doc:`Develop standardized scan plans <creating_plans>`
3. :doc:`Configure data management workflows <dm>`
4. :doc:`Deploy multi-instrument systems <deployment_patterns>`
