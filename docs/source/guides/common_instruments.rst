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
    echo '"""Shared device definitions."""' > src/beamline_common/devices/__init__.py
    echo '"""Shared plan definitions."""' > src/beamline_common/plans/__init__.py

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
    │   │   │   ├── __init__.py       # Device module initialization
    │   │   │   ├── area_detector.py  # Common detector configurations
    │   │   │   ├── shutters.py       # Beamline shutter systems
    │   │   │   └── optics.py         # Shared optical components
    │   │   └── plans/                # Standardized procedures
    │   │       ├── __init__.py       # Plan module initialization
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

**8-ID Multi-Endstation Pattern:**

Based on the successful 8-ID deployment with common/endstation architecture:

.. code-block:: python

    # src/id8_common/devices/area_detector.py
    # Real example from 8-ID deployment (bits_deployments/8id-bits/)
    """EPICS area_detector definitions for ID8."""

    import logging
    from apstools.devices import CamMixin_V34
    from ophyd.areadetector import CamBase
    from ophyd.areadetector import EigerDetectorCam

    logger = logging.getLogger(__name__)

    class ID8_EigerCam_V34(CamMixin_V34, EigerDetectorCam):
        """Eiger Area Detector cam module for AD 3.4+"""
        # CamMixin_V34 automatically handles deprecated PV compatibility

.. code-block:: yaml

    # src/id8_i/configs/devices.yml 
    # Real example from 8-ID deployment showing YAML configuration approach
    
    # Direct ophyd devices - simple motor configuration
    ophyd.EpicsMotor:
    - name: fl2
      prefix: "8ideSoft:CR8-E2:m7"
      labels: ["motor"]
    - name: fl3
      prefix: "8idiSoft:CR8-I2:m7"
      labels: ["motor"]

    # Custom device classes from common package
    id8_i.devices.xy_motors.XY_Motors:
    - name: damm
      prefix: "8iddSoft:CR8-D1:US"
      x_motor: m2
      y_motor: m3

**9-ID Multi-Technique Pattern:**

Based on the 9-ID deployment with multiple experimental techniques:

.. code-block:: yaml

    # src/common_9id/configs/devices.yml
    # YAML configuration with mb_creator (Recommended for bAIt/BITS)
    apstools.devices.motor_factory.mb_creator:
    - name: sample_stage
      prefix: "9ID:SampleStage:"
      class_name: "SampleStage"
      labels: [ "baseline", "sample" ]
      motors:
        x: "X"
        y: "Y"
        theta: "Theta"

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
    from apsbits.core.instrument_init import make_devices
    from common_9id.plans.alignment import align_sample_position

    # Load shared devices from YAML configuration
    make_devices(config_path="common_9id/configs/devices.yml")

    # Technique-specific detector
    gisaxs_detector = PilatusDetector("9IDGISAXS:", name="gisaxs")

    # sample_stage is now available from YAML configuration

Creating Common Device Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Shared Hardware Devices (YAML Configuration Approach):**

For hardware used by multiple endstations, prefer YAML configuration:

.. code-block:: yaml

    # src/beamline_common/configs/devices.yml
    # Shared beamline devices configured via YAML
    
    # Standard beamline shutter with APS-specific configuration
    apstools.devices.ApsPssShutterWithStatus:
    - name: beamline_shutter
      prefix: "BEAMLINE:SHUTTER"
      labels: ["shutters", "baseline"]
      delay_s: 0.1  # Beamline-specific timing

    # Primary beamline slits with custom limits
    apstools.synApps.Optics2Slit2D_HV:
    - name: primary_slits
      prefix: "BEAMLINE:SLIT1"
      labels: ["slits", "optics", "baseline"]
      # Limits configured via YAML attributes
      h_size_limits: [0, 20]  # mm
      v_size_limits: [0, 15]  # mm

**Area Detector Configuration:**

Handle EPICS Area Detector 3.4+ compatibility via direct apstools usage:

.. code-block:: yaml

    # Area detectors with built-in AD 3.4+ compatibility
    apstools.devices.CamMixin_V34:
    - name: pilatus_detector
      prefix: "BEAMLINE:PIL1:"
      labels: ["detectors", "area_detectors"]
      # CamMixin_V34 automatically handles deprecated PV compatibility

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

**Loading Common Components via YAML:**

In individual instrument startup files, use YAML configuration:

.. code-block:: python

    # src/technique_a/startup.py
    from apsbits.core.instrument_init import make_devices

    # Load shared devices from common configuration
    make_devices(config_path="beamline_common/configs/devices.yml")
    
    # Import shared plans
    from beamline_common.plans.alignment import beamline_alignment

    # Technique-specific devices
    technique_detector = SpecialDetector("TECHNIQUE_A:", name="detector")
    
    # Shared devices are now available: beamline_shutter, primary_slits, etc.

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

**Real Deployment Validation:**

All examples in this guide are validated against production deployments:

- **8-ID Common Architecture**: `bits_deployments/8id-bits/src/id8_common/` and `id8_i/`
- **CamMixin_V34 Usage**: Real implementation in `8id-bits/src/id8_common/devices/area_detector.py`
- **YAML Device Configuration**: Production patterns in `8id-bits/src/id8_i/configs/devices.yml`
- **Motor Bundle Patterns**: Custom XY_Motors implementation in `8id-bits/src/id8_i/devices/xy_motors.py`

**Next Steps:**

1. :doc:`Create custom devices in common packages <creating_devices>`
2. :doc:`Develop standardized scan plans <creating_plans>`
3. :doc:`Configure data management workflows <dm>`
4. :doc:`Deploy multi-instrument systems <deployment_patterns>`
