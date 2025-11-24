.. _configuration_management:

Configuration Management with Guarneri
======================================

This guide covers advanced configuration management patterns using Guarneri for BITS instruments, enabling declarative device creation from configuration files.

Quick Start: Guarneri Configuration
------------------------------------

**Create devices from TOML configuration in 3 steps:**

.. code-block:: toml

    # 1. configs/devices.toml - TOML device configuration
    [[ motor ]]
    name = "sample_x"
    prefix = "IOC:SAMPLE:X"

    [[ motor ]]
    name = "sample_y"
    prefix = "IOC:SAMPLE:Y"

    [[ detector ]]
    name = "area_detector"
    prefix = "IOC:AD:"
    hdf_plugin = true

.. code-block:: python

    # 2. startup.py - Load devices from configuration
    from guarneri import Instrument
    from my_instrument.devices import SampleMotor, AreaDetector

    # Create instrument with device mappings
    instrument = Instrument({
        "motor": SampleMotor,
        "detector": AreaDetector
    })

    # Load devices from TOML file
    instrument.load("configs/devices.toml")

    # Connect all devices
    await instrument.connect()

.. code-block:: python

    # 3. Access devices through registry
    sample_x = instrument.devices['sample_x']
    area_detector = instrument.devices['area_detector']

Complete Guarneri Integration Guide
-----------------------------------

Understanding Guarneri Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Guarneri provides declarative device creation with several key advantages:

1. **Human-readable configuration** - TOML/YAML files instead of Python code
2. **Parallel device connection** - Faster startup times
3. **Graceful error handling** - Missing devices don't break the entire system
4. **Easy simulation** - Switch between real and simulated devices
5. **Tool integration** - External tools can modify configurations

**Guarneri vs Traditional BITS:**

.. code-block:: text

    Traditional BITS              Guarneri-Enhanced BITS
    ================              ======================
    devices/motors.py             devices/motors.py (class definitions)
    configs/devices.yml           configs/devices.toml (instances)
    startup.py (make_devices)     startup.py (Instrument.load)

Device Factory Patterns
~~~~~~~~~~~~~~~~~~~~~~~~

**Basic Device Factories:**

.. code-block:: python

    # devices/factories.py - Device factory functions
    from ophyd import EpicsMotor, Device
    from apstools.devices import mb_creator

    def create_motor(prefix: str, name: str = "", **kwargs):
        """Factory for creating standard motors."""
        return EpicsMotor(prefix, name=name, **kwargs)

    def create_motor_bundle(prefix: str, motors: dict, name: str = "", **kwargs):
        """Factory for creating motor bundles."""
        return mb_creator(
            prefix=prefix,
            motors=motors,
            name=name,
            **kwargs
        )

    def create_area_detector(prefix: str, name: str = "",
                           plugins: list = None, **kwargs):
        """Factory for creating area detectors with plugins."""
        from apstools.devices import ad_creator

        plugins = plugins or ["image", "hdf5", "stats"]
        return ad_creator(
            prefix=prefix,
            name=name,
            plugins=plugins,
            **kwargs
        )

**Configuration-Driven Factories:**

.. code-block:: toml

    # configs/devices.toml - Factory-based device creation
    [[ motor ]]
    name = "theta"
    prefix = "IOC:THETA"
    labels = ["sample", "rotation"]

    [[ motor_bundle ]]
    name = "sample_stage"
    prefix = "IOC:STAGE:"
    motors = {x = "X", y = "Y", z = "Z"}
    labels = ["sample", "positioning"]

    [[ area_detector ]]
    name = "pilatus"
    prefix = "IOC:PILATUS:"
    plugins = ["image", "hdf5", "stats", "roi"]
    file_path = "/data/pilatus/"

.. code-block:: python

    # startup.py - Using factories with Guarneri
    from guarneri import Instrument
    from my_instrument.devices.factories import (
        create_motor,
        create_motor_bundle,
        create_area_detector
    )

    instrument = Instrument({
        "motor": create_motor,
        "motor_bundle": create_motor_bundle,
        "area_detector": create_area_detector
    })

    instrument.load("configs/devices.toml")

Environment-Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Multi-Environment Setup:**

.. code-block:: toml

    # configs/devices_production.toml - Production configuration
    [[ motor ]]
    name = "sample_x"
    prefix = "12ID:SAMPLE:X"

    [[ detector ]]
    name = "pilatus"
    prefix = "12ID:PILATUS:"
    file_path = "/net/s12dserv/xorApps/data/pilatus/"

.. code-block:: toml

    # configs/devices_simulation.toml - Development configuration
    [[ motor ]]
    name = "sample_x"
    prefix = "SIM:SAMPLE:X"

    [[ detector ]]
    name = "pilatus"
    prefix = "SIM:PILATUS:"
    file_path = "/tmp/pilatus_sim/"

.. code-block:: python

    # startup.py - Environment-aware configuration loading
    from pathlib import Path
    from apsbits.utils.aps_functions import host_on_aps_subnet

    # Select configuration based on environment
    if host_on_aps_subnet():
        config_file = "configs/devices_production.toml"
    else:
        config_file = "configs/devices_simulation.toml"

    instrument.load(config_file)

Advanced Configuration Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Hierarchical Configuration:**

.. code-block:: toml

    # configs/base_devices.toml - Common devices
    [[ motor ]]
    name = "base_motor"
    prefix = "IOC:BASE"

.. code-block:: toml

    # configs/experiment_devices.toml - Experiment-specific
    [[ detector ]]
    name = "experiment_detector"
    prefix = "IOC:EXP:DET"

.. code-block:: python

    # Load multiple configuration files
    instrument.load("configs/base_devices.toml")
    instrument.load("configs/experiment_devices.toml")

**Dynamic Configuration Generation:**

.. code-block:: python

    # utils/config_generator.py - Generate configurations from templates
    import tomlkit
    from pathlib import Path

    def generate_motor_config(beamline_id, motor_list):
        """Generate motor configuration for beamline."""

        config = tomlkit.document()

        for motor_name, motor_pv in motor_list.items():
            motor_section = tomlkit.table()
            motor_section["name"] = motor_name
            motor_section["prefix"] = f"{beamline_id}:{motor_pv}"
            motor_section["labels"] = ["motors"]

            config.setdefault("motor", tomlkit.aot()).append(motor_section)

        return config

    # Generate configuration for 12-ID
    motor_config = generate_motor_config("12ID", {
        "sample_x": "SAMPLE:X",
        "sample_y": "SAMPLE:Y",
        "detector_z": "DETECTOR:Z"
    })

    # Save to file
    with open("configs/12id_motors.toml", "w") as f:
        tomlkit.dump(motor_config, f)

Validation and Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Configuration Validation:**

.. code-block:: python

    # utils/validation.py - Configuration validation
    from guarneri import Instrument
    from guarneri.exceptions import InvalidConfiguration

    def validate_device_config(config_file):
        """Validate device configuration before loading."""

        try:
            # Try to parse configuration
            instrument = Instrument({})
            device_defns = instrument.parse_config(
                open(config_file),
                config_format="toml"
            )

            # Check for required fields
            for defn in device_defns:
                if "name" not in defn.get("kwargs", {}):
                    raise InvalidConfiguration(f"Missing 'name' field in {defn}")

                if "prefix" not in defn.get("kwargs", {}):
                    raise InvalidConfiguration(f"Missing 'prefix' field in {defn}")

            return True, "Configuration valid"

        except Exception as e:
            return False, str(e)

**Graceful Error Handling:**

.. code-block:: python

    # startup.py - Robust device loading with error handling
    from guarneri import Instrument
    import logging

    logger = logging.getLogger(__name__)

    async def load_devices_safely(config_files):
        """Load devices with comprehensive error handling."""

        instrument = Instrument(device_classes, ignored_classes=["metadata"])

        # Load configurations
        for config_file in config_files:
            try:
                instrument.load(config_file)
                logger.info(f"Loaded configuration: {config_file}")
            except Exception as e:
                logger.error(f"Failed to load {config_file}: {e}")
                continue

        # Connect devices with timeout and exception handling
        try:
            connected_devices, exceptions = await instrument.connect(
                timeout=30,  # seconds
                return_exceptions=True
            )

            logger.info(f"Connected {len(connected_devices)} devices")

            if exceptions:
                logger.warning(f"Failed to connect {len(exceptions)} devices:")
                for device_name, exception in exceptions.items():
                    logger.warning(f"  {device_name}: {exception}")

            return instrument

        except Exception as e:
            logger.error(f"Critical error during device connection: {e}")
            raise

Integration with BITS Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Hybrid BITS-Guarneri Approach:**

.. code-block:: python

    # startup.py - Combining BITS and Guarneri patterns
    from apsbits.utils.device_registry import make_devices
    from guarneri import Instrument

    # Traditional BITS devices (complex, hand-crafted)
    make_devices(device_file="configs/custom_devices.yml")

    # Guarneri devices (standard, configuration-driven)
    instrument = Instrument(standard_device_classes)
    instrument.load("configs/standard_devices.toml")
    await instrument.connect()

    # Merge device registries
    for name, device in instrument.devices.items():
        globals()[name] = device

**Migration Strategy from BITS to Guarneri:**

.. code-block:: python

    # utils/migration.py - Convert BITS YAML to Guarneri TOML
    import yaml
    import tomlkit
    from pathlib import Path

    def convert_bits_to_guarneri(bits_yaml_file, guarneri_toml_file):
        """Convert BITS YAML device config to Guarneri TOML."""

        with open(bits_yaml_file) as f:
            bits_config = yaml.safe_load(f)

        guarneri_config = tomlkit.document()

        for device_class, instances in bits_config.items():
            device_type = device_class.split('.')[-1].lower()

            for instance in instances:
                device_section = tomlkit.table()
                device_section.update(instance)

                guarneri_config.setdefault(device_type, tomlkit.aot()).append(
                    device_section
                )

        with open(guarneri_toml_file, 'w') as f:
            tomlkit.dump(guarneri_config, f)

Testing and Development
~~~~~~~~~~~~~~~~~~~~~~~

**Simulation and Mocking:**

.. code-block:: toml

    # configs/devices_test.toml - Test configuration with simulation
    [[ motor ]]
    name = "sample_x"
    prefix = "SIM:SAMPLE:X"
    fake = true  # Use simulated device

    [[ detector ]]
    name = "area_detector"
    prefix = "SIM:AD:"
    fake = true

.. code-block:: python

    # tests/test_devices.py - Testing with Guarneri
    import pytest
    from guarneri import Instrument

    @pytest.fixture
    async def test_instrument():
        """Create test instrument with simulated devices."""

        instrument = Instrument(device_classes)
        instrument.load("configs/devices_test.toml", fake=True)
        await instrument.connect(mock=True)

        yield instrument

        # Cleanup if needed

    async def test_device_creation(test_instrument):
        """Test device creation from configuration."""

        assert "sample_x" in test_instrument.devices
        assert "area_detector" in test_instrument.devices

        # Test device functionality
        motor = test_instrument.devices["sample_x"]
        assert motor.connected

Best Practices and Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Configuration Organization:**

.. code-block:: text

    configs/
    ├── devices_base.toml          # Common devices across all modes
    ├── devices_production.toml    # Production-specific devices
    ├── devices_simulation.toml    # Development/simulation devices
    ├── devices_commissioning.toml # Commissioning-specific devices
    └── templates/                 # Configuration templates
        ├── motor_template.toml
        ├── detector_template.toml
        └── stage_template.toml

**DO:**

- Use factories for complex device creation
- Validate configurations before loading
- Handle connection failures gracefully
- Use environment-specific configurations
- Document device parameters in TOML comments
- Test with simulated devices first

**DON'T:**

- Put business logic in configuration files
- Hardcode prefixes across environments
- Skip error handling during device connection
- Mix device instantiation and configuration
- Ignore connection timeout and retry logic

**Next Steps:**

1. :doc:`Integrate with queue server environments <qserver>`
2. :doc:`Set up automated configuration validation <testing>`
3. :doc:`Create deployment-specific configurations <deployment_patterns>`
4. :doc:`Implement configuration management workflows <../operations>`
