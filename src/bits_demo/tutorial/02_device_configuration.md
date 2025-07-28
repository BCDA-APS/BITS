# Device Configuration

## Overview

In this step, you'll replace the simulated devices with real configurations that connect to your IOCs. You'll learn how to map EPICS PVs to Bluesky devices and test connectivity.

**Time**: ~25 minutes
**Goal**: Working device configurations connected to demo IOCs

## Prerequisites

✅ Completed Steps 0-1
✅ BITS-Starter repository set up
✅ Demo IOCs running (adsim_ioc and gp_ioc)
✅ Device inventory from IOC exploration

## Understanding Device Configuration

### Device Configuration File

The `configs/devices.yml` file maps EPICS PVs to Bluesky devices:

```yaml
# YAML structure
device_callable: # Device class or function
  - name: unique_name
    labels: [ "category1", "category2" ]  # optional
    # additional keyword arguments expected by the callable, typical for EPICS include:
    prefix: "epics:pv:prefix:"  # include any trailing delimiter, such as ":"
    # additional parameters...
```

### Device Callables

| Device Callable | Use Case | EPICS PV kwarg | kwarg meaning |
|-----------------|----------|----------------| ------------- |
| `ophyd.EpicsMotor` | Motors, positioners | `prefix` | Base PV (e.g., `gp:m1`) |
| `ophyd.scaler.ScalerCH` | Multi-channel scalers | `prefix` | Base PV (e.g., `gp:scaler1`) |
| `apstools.devices.ad_creator` | Area detectors | `prefix` | Base PV (e.g., `adsim:`) |
| `ophyd.EpicsSignalRO` | Read-only values | `read_pv` | Full PV name |
| `ophyd.EpicsSignal` | Read-write values | `write_pv` | Full PV name (add `read_pv` kwarg if different) |

Notes:

- When in doubt, check the source code for the `device_callable`.
- For some reason, the `prefix` kwarg works just fine with both `EpicsSignal` & `EpicsSignalRO`.

### Device Labels

Labels organize devices for different uses.  These are the labels with
specific meanings.  Feel free to use other labels at your choice:

- `"detectors"`: Used in scans for data collection
- `"baseline"`: Monitored during every scan
- `"motors"`: Available for motion commands

## Step-by-Step Configuration

### 1. Backup Original Configuration

```bash
# Save the original simulation config
cd src/my_beamline/configs/
cp devices.yml devices_simulation_backup.yml
```

### 2. Create IOC Device Configuration

Replace the contents of `configs/devices.yml`:

```yaml
# Device configuration for demo IOCs
# Uses actual BITS YAML syntax matching production deployments

# Motors from GP IOC (gp:m1 through gp:m20)
ophyd.EpicsMotor:
- name: m1
  prefix: "gp:m1"
  labels: ["motors"]
- name: m2
  prefix: "gp:m2"
  labels: ["motors"]
- name: m3
  prefix: "gp:m3"
  labels: ["motors"]
- name: sample_x
  prefix: "gp:m4"
  labels: ["motors", "sample"]
- name: sample_y
  prefix: "gp:m5"
  labels: ["motors", "sample"]
- name: sample_z
  prefix: "gp:m6"
  labels: ["motors", "sample"]
- name: m7
  prefix: "gp:m7"
  labels: ["motors"]
- name: m8
  prefix: "gp:m8"
  labels: ["motors"]

# Scalers from GP IOC
ophyd.scaler.ScalerCH:
- name: scaler1
  prefix: "gp:scaler1"
  labels: ["detectors"]
- name: scaler2
  prefix: "gp:scaler2"
  labels: ["detectors", "baseline"]

# Area detector from adsim IOC
apstools.devices.ad_creator:
- name: simdet
  prefix: "adsim:"
  labels: ["detectors", "area_detectors"]

# Support and monitoring devices
ophyd.EpicsSignalRO:
- name: ioc_cpu
  prefix: "gp:IOC_CPU_LOAD"
  labels: ["baseline", "monitoring"]
- name: ioc_memory
  prefix: "gp:IOC_MEM_USED"
  labels: ["baseline", "monitoring"]

# User calculations
ophyd.EpicsSignal:
- name: calc1
  prefix: "gp:userCalc1.VAL"
  labels: ["calculations"]
- name: calc2
  prefix: "gp:userCalc2.VAL"
  labels: ["calculations"]
```

### 3. Test Configuration Syntax

```bash
# Verify YAML syntax
python -c "
import yaml
with open('devices.yml') as f:
    config = yaml.safe_load(f)
    print('✅ Configuration file is valid YAML')
    print(f'Found {len(config)} device categories')
    for category, devices in config.items():
        print(f'  {category}: {len(devices)} devices')
"
```

### 4. Test Device Loading

```bash
# Start IPython to test device loading
ipython
```

```python
# Load your instrument with new configuration
from my_beamline.startup import *

# The startup process will now create devices from IOCs instead of simulators
# Watch for any connection warnings or errors
```

**Expected output:**
- Device creation messages
- Some connection warnings (normal during startup)
- No critical errors

### 5. Test Device Connectivity

```python
# Test motor connectivity
print("🔧 Testing Motors:")
print(f"m1 position: {m1.position}")
print(f"m1 limits: {m1.limits}")
print(f"sample_x position: {sample_x.position}")

# Test scaler connectivity
print("\n🔍 Testing Detectors:")
print(f"scaler1 connected: {scaler1.connected}")
print(f"scaler1 channels: {scaler1.channels}")

# Test area detector
print(f"simdet connected: {simdet.connected}")
print(f"simdet image size: {simdet.cam.array_size.get()}")

# Test baseline devices
print("\n📊 Testing Support Devices:")
print(f"IOC CPU: {ioc_cpu.get()}")
print(f"IOC Memory: {ioc_memory.get()}")
```

### 6. Verify Device Labels

```python
# Check which devices have which labels
import bluesky.preprocessors as bpp

print("🏷️  Device Labels:")
print(f"Motors: {list(bpp._devices_by_label['motors'])}")
print(f"Detectors: {list(bpp._devices_by_label['detectors'])}")
print(f"Baseline: {list(bpp._devices_by_label['baseline'])}")
```

### 7. Test Basic Device Operations

```python
# Test motor motion (small relative moves)
print("\n🚗 Testing Motor Motion:")
print(f"Moving m1 by +0.1...")
RE(bps.mvr(m1, 0.1))  # Move relative
print(f"New m1 position: {m1.position}")

print(f"Moving m1 back by -0.1...")
RE(bps.mvr(m1, -0.1))
print(f"Final m1 position: {m1.position}")

# Test scaler counting
print("\n⏱️  Testing Scaler Counting:")
RE(bp.count([scaler1], num=1, delay=1))

# Test area detector acquisition
print("\n📸 Testing Area Detector:")
RE(bp.count([simdet], num=1))
```

## Advanced Configuration Options

### 1. Custom Device Names and Metadata

```yaml
# More descriptive device names
ophyd.EpicsMotor:
- name: theta
  prefix: "gp:m1"
  labels: ["motors", "diffractometer"]
  # Custom metadata can be added via Python code after device creation
```

### 2. Device Grouping

```yaml
# Group related devices using consistent labeling
ophyd.EpicsMotor:
- name: sample_stage_x
  prefix: "gp:m4"
  labels: ["motors", "sample_stage"]
- name: sample_stage_y
  prefix: "gp:m5"
  labels: ["motors", "sample_stage"]
- name: sample_stage_z
  prefix: "gp:m6"
  labels: ["motors", "sample_stage"]
```

### 3. Area Detector Configuration

```yaml
# Area detectors use ad_creator
apstools.devices.ad_creator:
- name: camera
  prefix: "adsim:"
  labels: ["detectors", "area_detectors"]
  # Additional configuration done via Python after creation
```

### 4. Scaler Channel Configuration

```yaml
# Scalers with multiple instances
ophyd.scaler.ScalerCH:
- name: main_scaler
  prefix: "gp:scaler1"
  labels: ["detectors"]
  # Channel naming done via Python code after device creation
```

## Creating Example Device Configurations

Let me create some example configurations for common setups:

### 1. Simple Scanning Setup

Create `examples/device_configurations/simple_scanning.yml`:

```yaml
# Minimal configuration for basic scanning
ophyd.EpicsMotor:
- name: scan_motor
  prefix: "gp:m1"
  labels: ["motors"]

ophyd.scaler.ScalerCH:
- name: counter
  prefix: "gp:scaler1"
  labels: ["detectors"]
```

### 2. Diffractometer Setup

Create `examples/device_configurations/diffractometer.yml` to support the rotation
axes of a diffractometer such as this 4-circle example.  For complete control of a
diffractometer, including crystallographic and reciprocal-space operations, see
the ***hklpy2*** [package](https://blueskyproject.io/hklpy2).

```yaml
# 4-circle diffractometer configuration
ophyd.EpicsMotor:
- name: theta
  prefix: "gp:m1"
  labels: ["motors", "diffractometer"]
- name: chi
  prefix: "gp:m2"
  labels: ["motors", "diffractometer"]
- name: phi
  prefix: "gp:m3"
  labels: ["motors", "diffractometer"]
- name: tth
  prefix: "gp:m4"
  labels: ["motors", "diffractometer"]

ophyd.scaler.ScalerCH:
- name: point_detector
  prefix: "gp:scaler1"
  labels: ["detectors"]

apstools.devices.ad_creator:
- name: area_detector
  prefix: "adsim:"
  labels: ["detectors", "area_detectors"]
```

## Device Testing and Validation

### 1. Create Device Test Script

Create `scripts/test_devices.py`:

```python
#!/usr/bin/env python3
"""Test device connectivity and functionality"""

def test_all_devices():
    """Test all configured devices"""
    from my_beamline.startup import *
    import bluesky.preprocessors as bpp

    print("🔧 Device Connectivity Test")
    print("=" * 40)

    # Test motors
    motors = list(bpp._devices_by_label.get('motors', []))
    print(f"\n🚗 Motors ({len(motors)}):")
    for motor in motors:
        try:
            pos = motor.position
            limits = motor.limits
            print(f"  ✅ {motor.name}: pos={pos:.3f}, limits={limits}")
        except Exception as e:
            print(f"  ❌ {motor.name}: {e}")

    # Test detectors
    detectors = list(bpp._devices_by_label.get('detectors', []))
    print(f"\n🔍 Detectors ({len(detectors)}):")
    for det in detectors:
        try:
            connected = det.connected
            print(f"  {'✅' if connected else '❌'} {det.name}: connected={connected}")
        except Exception as e:
            print(f"  ❌ {det.name}: {e}")

    # Test baseline devices
    baseline = list(bpp._devices_by_label.get('baseline', []))
    print(f"\n📊 Baseline ({len(baseline)}):")
    for dev in baseline:
        try:
            value = dev.get()
            print(f"  ✅ {dev.name}: {value}")
        except Exception as e:
            print(f"  ❌ {dev.name}: {e}")

if __name__ == "__main__":
    test_all_devices()
```

### 2. Run Device Tests

```bash
# Make script executable
chmod +x scripts/test_devices.py

# Run device tests
python scripts/test_devices.py
```

### 3. Test with List Devices Magic

```python
# In IPython session with your instrument loaded
%wa  # List all devices with current values

# Show specific device categories
%wa motors      # Only motors
%wa detectors   # Only detectors
%wa baseline    # Only baseline devices
```

## Troubleshooting Common Issues

### 1. PV Connection Failures

```python
# Check specific PV connectivity
import epics
pv = epics.PV("gp:m1.RBV")
print(f"Connected: {pv.wait_for_connection(timeout=5)}")
print(f"Value: {pv.get()}")

# Check EPICS environment
import os
print(f"EPICS_CA_ADDR_LIST: {os.environ.get('EPICS_CA_ADDR_LIST', 'Not set')}")
print(f"EPICS_CA_AUTO_ADDR_LIST: {os.environ.get('EPICS_CA_AUTO_ADDR_LIST', 'Not set')}")
```

**Solutions:**
```bash
# Set EPICS environment if needed
export EPICS_CA_AUTO_ADDR_LIST=YES

# Check if IOCs are still running
podman ps | grep -E "(adsim_ioc|gp_ioc)"
```

### 2. Device Class Errors

```python
# Verify device classes are available
from ophyd import EpicsMotor, ScalerCH
from apstools.devices import ADBSoftDetector

print("✅ All device classes available")
```

### 3. YAML Syntax Errors

```bash
# Validate YAML syntax
python -c "
import yaml
try:
    with open('configs/devices.yml') as f:
        yaml.safe_load(f)
    print('✅ YAML syntax is correct')
except yaml.YAMLError as e:
    print(f'❌ YAML syntax error: {e}')
"
```

### 4. Timeout Issues

Edit `configs/iconfig.yml` to increase timeouts:

```yaml
OPHYD:
    TIMEOUTS:
        PV_READ: 10      # Increase from 5
        PV_WRITE: 10     # Increase from 5
        PV_CONNECTION: 10 # Increase from 5
```

## Best Practices

### 1. Device Naming
- Use descriptive names: `sample_x` instead of `m4`
- Group related devices: `sample_stage.x`, `sample_stage.y`
- Avoid special characters in names

### 2. Labeling Strategy
- `"detectors"`: Devices that measure data
- `"motors"`: Devices that can be scanned
- `"baseline"`: Devices monitored in every scan
- Custom labels: `"sample"`, `"optics"`, `"diagnostics"`

### 3. Configuration Organization
- Start with essential devices (2-3 motors, 1 detector)
- Add devices incrementally and test each addition
- Use comments to document PV meanings

### 4. Testing Approach
- Test configuration syntax before loading
- Test device connectivity individually
- Test basic operations before complex scans
- Keep backup of working configurations

## Validation Checklist

Before proceeding to the next step:

- ✅ Devices load without critical errors
- ✅ At least 2 motors are connected and responsive
- ✅ At least 1 scaler is connected
- ✅ Area detector connects (if using imaging)
- ✅ Device tests pass
- ✅ %wa command shows expected devices

## Commit Your Progress

```bash
# Add the new configuration
git add configs/devices.yml scripts/test_devices.py

# Commit changes
git commit -m "Configure real IOC devices

- Replace simulation devices with IOC devices
- Add motors: m1, m2, m3, sample_x, sample_y, sample_z
- Add detectors: scaler1, scaler2, simdet
- Add support devices: ioc_cpu, ioc_memory
- Include device testing script
- Verify connectivity to demo IOCs
"
```

## Next Steps

With working device configurations, you're ready to:
1. Create custom scan plans using your devices
2. Test different scanning patterns
3. Analyze the data generated

**Next Step**: [Plan Development](03_plan_development.md)

---

## Reference: Device Configuration Template

```yaml
# BITS device configuration template
device_callable_path:
- name: device_name
  prefix: "prefix:pv_name"
  labels: ["label1", "label2"]
  # Additional callable-specific parameters as needed
```

## Common Device Callables Reference

| Device Callable | Use Case | EPICS PV kwarg | kwarg meaning |
|-----------------|----------|----------------| ------------- |
| `ophyd.EpicsMotor` | Motors, positioners | `prefix` | Base PV (e.g., `gp:m1`) |
| `ophyd.scaler.ScalerCH` | Multi-channel scalers | `prefix` | Base PV (e.g., `gp:scaler1`) |
| `apstools.devices.ad_creator` | Area detectors | `prefix` | Base PV (e.g., `adsim:`) |
| `ophyd.EpicsSignalRO` | Read-only values | `read_pv` | Full PV name |
| `ophyd.EpicsSignal` | Read-write values | `write_pv` | Full PV name (add `read_pv` kwarg if different) |

Notes:

- When in doubt, check the source code for the `device_callable`.
- For some reason, the `prefix` kwarg works just fine with both `EpicsSignal` & `EpicsSignalRO`.
