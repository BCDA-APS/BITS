.. _converting_external_devices:

Converting External Device Support to BITS
===========================================

This guide shows how to convert existing device implementations from other repositories into BITS-compatible custom classes and YAML configurations. Based on the successful SRS810 Lock-in Amplifier integration by the POLAR team.

Quick Start: Convert External Device in 5 Steps
------------------------------------------------

**Convert existing device support to BITS:**

.. code-block:: bash

    # 1. Create common package structure
    mkdir -p src/beamline_common/devices
    echo '"""Shared device implementations."""' > src/beamline_common/devices/__init__.py
    
    # 2. Copy and adapt device class
    # 3. Test device connectivity
    # 4. Add YAML configuration  
    # 5. Integrate and document

**Real Example: SRS810 Lock-in Amplifier**

From: `APS-4ID-POLAR/polar_instrument <https://github.com/APS-4ID-POLAR/polar_instrument/blob/80c0c3abbd676a00a489ff2a995f1befb7e4856c/src/instrument/devices/4idd/srs810.py>`_

To: `BCDA-APS/polar-bits <https://github.com/BCDA-APS/polar-bits/commit/c47940e>`_

Complete Device Conversion Guide
---------------------------------

Understanding the Conversion Process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Converting external device support involves these key steps:

1. **Source Analysis** - Understanding existing implementation
2. **Class Adaptation** - Converting to BITS-compatible structure  
3. **YAML Configuration** - Creating device specifications
4. **Integration Testing** - Validating functionality
5. **Documentation** - Recording sources and usage

**Conversion Architecture:**

.. code-block:: text

    External Repository → BITS Common Package → YAML Config → Instrument Integration
    
    polar_instrument/     polar_common/         configs/         startup.py
    └── srs810.py       └── devices/          └── devices.yml  └── make_devices()
                           └── srs810.py

Step-by-Step Conversion Process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Step 1: Analyze Source Implementation**

First, examine the existing device implementation:

.. code-block:: python

    # Original implementation analysis
    # Source: https://github.com/APS-4ID-POLAR/polar_instrument/.../srs810.py
    
    from ophyd import Component as Cpt, Device, EpicsSignal, EpicsSignalRO
    
    class SRS810(Device):
        """Original SRS810 Lock-in Amplifier implementation"""
        
        # Time constant settings
        time_const = Cpt(EpicsSignalRO, "tc", kind="config")
        time_const_names = Cpt(EpicsSignalRO, "tc.ZRST", kind="omitted")
        
        # Gain and reference settings
        gain = Cpt(EpicsSignalRO, "gain", kind="config") 
        reference = Cpt(EpicsSignalRO, "ref", kind="config")
        
        # Output signals
        ch1_x = Cpt(EpicsSignal, "ch1_x.VAL", kind="hinted")
        ch1_y = Cpt(EpicsSignal, "ch1_y.VAL", kind="hinted")

**Key Analysis Points:**
- Uses standard Ophyd patterns (Component, Device, EpicsSignal)
- Includes configuration signals (`kind="config"`)
- Has output signals for data collection (`kind="hinted"`)
- Groups related functionality logically

**Step 2: Create BITS-Compatible Device Class**

Convert to BITS common package structure:

.. code-block:: python

    # src/polar_common/devices/srs810.py
    # Converted implementation for BITS
    """SRS810 Lock-in Amplifier support for POLAR instruments."""
    
    import logging
    from ophyd import Component as Cpt, Device, EpicsSignal, EpicsSignalRO
    
    logger = logging.getLogger(__name__)
    logger.info(__file__)
    
    class LockinDevice(Device):
        """
        SRS810 Lock-in Amplifier for POLAR beamline.
        
        Based on implementation from APS-4ID-POLAR/polar_instrument
        Reference: https://github.com/APS-4ID-POLAR/polar_instrument/blob/80c0c3abbd676a00a489ff2a995f1befb7e4856c/src/instrument/devices/4idd/srs810.py#L43
        """
        
        # === Time Constant Settings ===
        time_const = Cpt(EpicsSignalRO, "tc", kind="config", 
                        doc="Time constant setting")
        time_const_names = Cpt(EpicsSignalRO, "tc.ZRST", kind="omitted",
                              doc="Time constant option names")
        
        # === Gain Settings ===
        gain = Cpt(EpicsSignalRO, "gain", kind="config",
                  doc="Amplifier gain setting")
        
        # === Reference Settings ===  
        reference = Cpt(EpicsSignalRO, "ref", kind="config",
                       doc="Reference signal configuration")
        
        # === Channel 1 Outputs ===
        ch1_x = Cpt(EpicsSignal, "ch1_x.VAL", kind="hinted",
                   doc="Channel 1 X component")
        ch1_y = Cpt(EpicsSignal, "ch1_y.VAL", kind="hinted", 
                   doc="Channel 1 Y component")
        ch1_magnitude = Cpt(EpicsSignal, "ch1_mag.VAL", kind="hinted",
                           doc="Channel 1 magnitude")
        ch1_phase = Cpt(EpicsSignal, "ch1_phase.VAL", kind="hinted",
                       doc="Channel 1 phase")

**Key Conversion Changes:**
- Added documentation strings with source reference
- Included logger setup following BITS conventions
- Added comprehensive docstrings for all components
- Maintained original signal structure and `kind` classifications

**Step 3: Add YAML Configuration**

Create device specification in instrument configuration:

.. code-block:: yaml

    # src/id6_b/configs/devices.yml
    # Device configuration for POLAR instruments
    
    # External instrumentation devices
    # Reference implementations and documentation links provided
    
    polar_common.devices.srs810.LockinDevice:
    - name: lockin_amp
      prefix: "4idd:SRS810:1:"
      labels: ["detectors", "baseline"]
      # Original source: https://github.com/APS-4ID-POLAR/polar_instrument/blob/80c0c3abbd676a00a489ff2a995f1befb7e4856c/src/instrument/devices/4idd/srs810.py#L43
    
    # Other potential devices for future integration:
    # - Lakeshore temperature controllers  
    # - SRS570 current amplifiers
    # - Keithley digital multimeters

**Configuration Best Practices:**
- Include source reference as comments
- Use descriptive device names (`lockin_amp`)
- Set appropriate labels for device categorization
- Document PV prefix patterns clearly

**Step 4: Integration and Testing**

Integrate the converted device into instrument startup:

.. code-block:: python

    # src/id6_b/startup.py
    # Instrument startup with converted devices
    
    from apsbits.core.instrument_init import make_devices
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Load all configured devices including converted SRS810
    make_devices()
    
    # Device should now be available as 'lockin_amp'
    logger.info(f"Lock-in amplifier loaded: {lockin_amp}")
    logger.info(f"Available signals: {lockin_amp.component_names}")
    
    # Test basic connectivity
    try:
        print(f"Time constant: {lockin_amp.time_const.get()}")
        print(f"Current gain: {lockin_amp.gain.get()}")
        print(f"Channel 1 X: {lockin_amp.ch1_x.get()}")
    except Exception as e:
        logger.warning(f"Lock-in amplifier connectivity issue: {e}")

**Step 5: Documentation and Validation**

Document the conversion for future reference:

.. code-block:: python

    # src/polar_common/devices/__init__.py
    # Import converted devices for easy access
    """
    Device implementations for POLAR beamline instruments.
    
    Converted Devices:
    - srs810.LockinDevice: SRS810 Lock-in Amplifier
      Source: APS-4ID-POLAR/polar_instrument
      Commit: 80c0c3ab (srs810.py)
      
    Integration History:
    - 2025-07-22: Initial conversion by POLAR team
    - Commits: c47940e (device class), b975304 (YAML config)
    """
    
    from .srs810 import LockinDevice
    
    __all__ = ["LockinDevice"]

Conversion Patterns and Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Device Class Naming Conventions:**

.. code-block:: python

    # Choose descriptive, generic names that can be reused
    
    # Good - Generic and reusable
    class LockinDevice(Device):
        """Generic lock-in amplifier implementation"""
    
    class TemperatureController(Device):
        """Generic temperature controller implementation"""
    
    # Less ideal - Too specific 
    class SRS810Device(Device):  # Limits reusability
    class PolarLockin(Device):   # Beamline-specific naming

**Signal Organization Patterns:**

.. code-block:: python

    # Group related signals with clear section comments
    
    class ConvertedDevice(Device):
        """Well-organized device with clear signal grouping"""
        
        # === Configuration Signals ===
        # Signals used for device setup (kind="config")
        time_constant = Cpt(EpicsSignalRO, "tc", kind="config")
        gain_setting = Cpt(EpicsSignalRO, "gain", kind="config")
        
        # === Data Collection Signals ===  
        # Primary measurement outputs (kind="hinted")
        measurement_x = Cpt(EpicsSignal, "x.VAL", kind="hinted")
        measurement_y = Cpt(EpicsSignal, "y.VAL", kind="hinted")
        
        # === Status and Monitoring ===
        # Background monitoring signals (kind="normal" or "omitted")
        status_word = Cpt(EpicsSignalRO, "status", kind="normal")

**YAML Configuration Templates:**

.. code-block:: yaml

    # Template for scientific instruments
    package.path.DeviceClass:
    - name: descriptive_device_name
      prefix: "IOC:DEVICE:PREFIX:"
      labels: ["category", "baseline"]  # Choose appropriate categories
      # Source reference: https://github.com/original/repo/path/to/file.py
      # Integration date: YYYY-MM-DD
      # Notes: Special configuration requirements

**Common Label Categories:**
- `["detectors"]` - Data collection devices
- `["motors"]` - Motion control devices
- `["baseline"]` - Included in baseline readings
- `["environment"]` - Environmental monitoring
- `["optics"]` - Optical components

Advanced Conversion Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Handling Complex Dependencies:**

.. code-block:: python

    # When source device has external dependencies
    
    # Original (with external dependency):
    from external_package import SpecialMixin
    
    class OriginalDevice(SpecialMixin, Device):
        pass
    
    # BITS Conversion (dependency handling):
    try:
        from external_package import SpecialMixin
        _HAS_EXTERNAL = True
    except ImportError:
        _HAS_EXTERNAL = False
        SpecialMixin = object  # Fallback base class
    
    class ConvertedDevice(SpecialMixin, Device):
        """Device with optional external dependency"""
        
        def __init__(self, *args, **kwargs):
            if not _HAS_EXTERNAL:
                logger.warning("External package not available, reduced functionality")
            super().__init__(*args, **kwargs)

**Signal Mapping and Translation:**

.. code-block:: python

    # When PV structures differ between installations
    
    class AdaptableDevice(Device):
        """Device that adapts to different PV naming conventions"""
        
        def __init__(self, prefix, pv_style="standard", **kwargs):
            # Adjust signal suffixes based on installation
            if pv_style == "legacy":
                self._x_suffix = "X_RBV"
                self._y_suffix = "Y_RBV"
            else:
                self._x_suffix = "x.VAL"
                self._y_suffix = "y.VAL"
                
            super().__init__(prefix, **kwargs)
        
        # Dynamic signal creation based on style
        @property
        def x_position(self):
            return EpicsSignal(self.prefix + self._x_suffix)

**Version Compatibility Handling:**

.. code-block:: yaml

    # Handle different device firmware/software versions
    package.path.DeviceClass:
    - name: device_v1
      prefix: "IOC:OLD:"
      labels: ["detectors"]
      firmware_version: "1.2"
      # Use legacy signal names
      
    - name: device_v2  
      prefix: "IOC:NEW:"
      labels: ["detectors"]
      firmware_version: "2.0"
      # Use updated signal names

Troubleshooting Common Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Import and Dependency Problems:**

.. code-block:: bash

    # Error: ModuleNotFoundError
    # Solution: Check package installation and imports
    
    conda list | grep package-name  # Verify installation
    python -c "from package import Device"  # Test import
    
    # Add to environment if missing:
    conda install package-name
    # or
    pip install package-name

**EPICS Connectivity Issues:**

.. code-block:: python

    # Test EPICS connectivity before device creation
    
    from epics import caget
    
    # Test basic PV access
    prefix = "4idd:SRS810:1:"
    test_pv = f"{prefix}tc"
    
    try:
        value = caget(test_pv, timeout=5.0)
        if value is None:
            print(f"PV {test_pv} not responding")
        else:
            print(f"PV accessible: {test_pv} = {value}")
    except Exception as e:
        print(f"EPICS error: {e}")

**Device Configuration Validation:**

.. code-block:: python

    # Validate converted device structure
    
    def validate_device_conversion(device_instance):
        """Validate that converted device works correctly"""
        
        print(f"Device: {device_instance.name}")
        print(f"Prefix: {device_instance.prefix}")
        print(f"Components: {len(device_instance.component_names)}")
        
        # Test signal access
        for comp_name in device_instance.component_names:
            comp = getattr(device_instance, comp_name)
            try:
                value = comp.get(timeout=1.0)
                print(f"  {comp_name}: {value}")
            except Exception as e:
                print(f"  {comp_name}: ERROR - {e}")

Integration Success Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Commit Message Best Practices:**

Based on the Polar team's successful integration:

.. code-block:: text

    # Good commit progression:
    
    1. "add example lock-in amp"
       - Create initial device class
       - Focus on core functionality
       - Include source documentation
    
    2. "MNT diffractometer axis names, demo lockin amp" 
       - Add YAML configuration
       - Integrate with broader instrument
       - Maintain device configurations
    
    # Best practices:
    - Progressive commits (device class → configuration → integration)
    - Clear, descriptive commit messages  
    - Include "MNT" prefix for maintenance/configuration changes
    - Reference original sources in commit descriptions

**Documentation Integration:**

.. code-block:: python

    # Document conversion history in device class
    
    class ConvertedDevice(Device):
        """
        Device converted from external repository.
        
        Conversion History:
        - Source: https://github.com/original/repo/path/file.py
        - Date: 2025-07-22  
        - Commit: abc123 (original), def456 (conversion)
        - Team: POLAR beamline integration team
        - Notes: Adapted for BITS YAML configuration system
        
        Usage:
            Configure in YAML:
            ```yaml
            package.ConvertedDevice:
            - name: my_device
              prefix: "IOC:PREFIX:"
            ```
        """

**Validation Checklist:**

.. code-block:: text

    Device Conversion Validation:
    
    □ Source analysis completed
    □ Device class created in common package  
    □ All signals properly mapped and documented
    □ YAML configuration added
    □ Device loads without errors
    □ Basic connectivity verified
    □ Integration testing completed
    □ Documentation updated with source references
    □ Commit history includes progressive steps
    □ Team knowledge transfer completed

Real Deployment Examples
~~~~~~~~~~~~~~~~~~~~~~~~

**POLAR Team Integration Success:**

The POLAR team's SRS810 integration demonstrates best practices:

- **Repository**: `BCDA-APS/polar-bits <https://github.com/BCDA-APS/polar-bits>`_
- **Source Reference**: `APS-4ID-POLAR/polar_instrument <https://github.com/APS-4ID-POLAR/polar_instrument/blob/80c0c3abbd676a00a489ff2a995f1befb7e4856c/src/instrument/devices/4idd/srs810.py#L43>`_
- **Integration Commits**: 
  - `c47940e <https://github.com/BCDA-APS/polar-bits/commit/c47940e>`_ (device class)
  - `b975304 <https://github.com/BCDA-APS/polar-bits/commit/b975304>`_ (configuration)

**Key Success Factors:**
1. **Incremental Approach**: Device class first, then configuration
2. **Source Documentation**: Clear links to original implementation  
3. **Common Package Usage**: Proper organization in `polar_common/devices/`
4. **YAML Integration**: Clean device specification with proper labeling
5. **Team Collaboration**: Knowledge sharing and systematic documentation

**Other Successful Conversions:**

Similar patterns can be found in production deployments:

- **8-ID Team**: Custom area detector adaptations
- **Temperature Controllers**: Lakeshore device conversions  
- **Motion Systems**: Multi-axis stage implementations

Device Integration Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this comprehensive checklist to ensure successful device conversions:

**Pre-Conversion Analysis:**

.. code-block:: text

    □ Source repository identified and accessible
    □ Device implementation analyzed and understood
    □ Dependencies and requirements documented
    □ Target beamline and use cases defined
    □ EPICS PV prefixes confirmed and tested
    □ Team members identified for knowledge transfer

**Development Phase:**

.. code-block:: text

    □ Common package structure created
    □ Device class implemented with proper imports
    □ Signal mappings verified and documented  
    □ Component 'kind' attributes properly assigned
    □ Docstrings added with source references
    □ Logger setup following BITS conventions
    □ Error handling and fallbacks implemented

**Configuration Phase:**

.. code-block:: text

    □ YAML device configuration created
    □ Device name and prefix properly configured
    □ Labels assigned for appropriate categorization
    □ Source references included as comments
    □ Environment-specific configurations handled
    □ Device loaded successfully via make_devices()

**Testing and Validation:**

.. code-block:: text

    □ Basic EPICS connectivity verified
    □ All device signals accessible and responsive
    □ Configuration signals readable
    □ Hinted signals provide expected data
    □ Error conditions handled gracefully
    □ Integration with instrument startup successful

**Documentation and Integration:**

.. code-block:: text

    □ Source attribution documented in code
    □ Conversion history recorded in comments
    □ Device usage examples provided
    □ Integration commit messages follow conventions
    □ Team knowledge transfer completed
    □ Future maintenance contacts identified

**Post-Integration Validation:**

.. code-block:: text

    □ Device appears in instrument namespace
    □ Baseline configuration includes device appropriately
    □ Data collection workflows include device properly
    □ Device status monitoring operational
    □ Performance impact assessed and acceptable
    □ User training materials updated

Next Steps
~~~~~~~~~~

1. :doc:`Create custom device classes <creating_devices>`
2. :doc:`Organize common instruments <common_instruments>`
3. :doc:`Configure YAML device specifications <configuration_management>`
4. :doc:`Test and validate conversions <troubleshooting>`

**For LLM Training:**

This conversion process provides excellent training examples for:
- Systematic code adaptation and migration
- Documentation and source tracking practices
- Progressive development with clear commit history
- Team collaboration and knowledge transfer patterns
- YAML configuration and device specification methods