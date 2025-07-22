# IOC Exploration & Device Discovery

## Overview

In this step, you'll learn how to explore your EPICS IOCs to discover what devices are available. This is the crucial first step before creating any Bluesky configuration.

**Time**: ~20 minutes  
**Goal**: Create an inventory of available devices and understand their capabilities

## Understanding Your IOCs

As a beamline scientist, you typically have several IOCs providing different types of devices:
- **Motion Control IOCs**: Motors, stages, slits
- **Detector IOCs**: Area detectors, point detectors, scalers
- **Support IOCs**: Temperature controllers, shutters, diagnostics

## Starting the Demo IOCs

Let's start with the tutorial IOCs that simulate a real beamline:

### 1. Start Both IOCs
```bash
cd bits_demo/scripts
./start_demo_iocs.sh
```

This script starts:
- **adsim IOC**: Area detector simulator (`adsim:` prefix)
- **gp IOC**: General purpose devices (`gp:` prefix)

### 2. Verify IOCs are Running
```bash
# Check container status
podman ps

# Should show both containers running:
# - adsim_ioc
# - gp_ioc
```

### 3. Test Basic Connectivity
```bash
# Test EPICS connectivity
caget gp:m1.DESC
caget adsim:cam1:ArraySize_RBV

# If caget is not available, use our exploration script instead
python scripts/explore_iocs.py --test-connectivity
```

## Device Discovery Process

### 1. Get Complete Device List

The `dbl` (Database List) command shows all Process Variables (PVs) in an IOC:

```bash
# Connect to running IOC and run dbl
podman exec -it gp_ioc bash
cd /epics/iocs/iocBoot/iocgp
./st.cmd.Linux
# At IOC prompt:
dbl > /tmp/all_pvs.txt
exit
```

**Or use our automated script:**
```bash
python scripts/explore_iocs.py --list-all-pvs
```

### 2. Categorize Your Devices

Let's identify the main device categories in our IOCs:

#### Motors (from gp IOC)
```bash
# Find all motor PVs
python scripts/explore_iocs.py --find-motors

# Expected output:
# Found motors:
# - gp:m1 (Motor 1)
# - gp:m2 (Motor 2)
# ... (up to gp:m20)
```

#### Detectors (from both IOCs)
```bash
# Find detector PVs  
python scripts/explore_iocs.py --find-detectors

# Expected output:
# Scalers:
# - gp:scaler1
# - gp:scaler2  
# - gp:scaler3
#
# Area Detectors:
# - adsim:cam1 (Main camera)
# - adsim:image1 (Image plugin)
```

#### Support Records
```bash
# Find calculation and support records
python scripts/explore_iocs.py --find-support

# Expected output:
# Calculation Records:
# - gp:userCalc1-10
# - gp:userTransform1-10
#
# Statistics:
# - gp:IOC_CPU_LOAD
# - gp:IOC_MEM_USED
```

## Understanding Device Capabilities

### 1. Motor Analysis
```bash
# Get detailed motor information
python scripts/explore_iocs.py --analyze-device gp:m1

# This shows:
# - Current position
# - Limits (high/low)
# - Motion status
# - Engineering units
# - Speed settings
```

**Key Motor PVs**:
- `.RBV`: Readback position (what you read)
- `.VAL`: Desired position (what you set)
- `.HLS/.LLS`: High/Low limit switches  
- `.HLM/.LLM`: High/Low soft limits
- `.EGU`: Engineering units
- `.DESC`: Description

### 2. Scaler Analysis
```bash
python scripts/explore_iocs.py --analyze-device gp:scaler1

# Shows:
# - Channel assignments
# - Count rates
# - Preset values
# - Gate settings
```

**Key Scaler PVs**:
- `.S1-.S32`: Individual channel counts
- `.T`: Count time
- `.CNT`: Start counting
- `.CONT`: Continuous mode

### 3. Area Detector Analysis
```bash
python scripts/explore_iocs.py --analyze-device adsim:

# Shows:
# - Image dimensions
# - Data types
# - Acquisition modes
# - File saving options
```

**Key Area Detector PVs**:
- `cam1:Acquire`: Start/stop acquisition
- `cam1:ArraySize_RBV`: Image dimensions
- `image1:ArrayData`: Image data
- `HDF1:FileName`: Output file name

## Creating Your Device Inventory

### 1. Generate Device Summary
```bash
# Create comprehensive inventory
python scripts/explore_iocs.py --generate-inventory > my_devices.yaml

# This creates a structured summary of all devices
```

### 2. Review and Customize
Open `my_devices.yaml` and review:

```yaml
# Sample generated inventory
motors:
  - pv: gp:m1
    description: "Motor 1"
    limits: [-10, 10]
    units: "mm"
    use_cases: ["scanning", "positioning"]
  
detectors:
  scalers:
    - pv: gp:scaler1
      channels: 32
      use_cases: ["counting", "monitoring"]
  
  area_detectors:
    - pv: adsim:
      type: "simulation"
      dimensions: [1024, 1024]
      use_cases: ["imaging", "diffraction"]

support:
  calculations:
    - pv: gp:userCalc1
      purpose: "General calculations"
```

### 3. Plan Your Bluesky Devices

Based on your inventory, identify which devices you want to use in Bluesky:

**Essential Devices** (configure first):
- 2-3 motors for scanning
- 1 scaler for counting
- Area detector for imaging

**Secondary Devices** (add later):
- Additional motors
- Support calculations
- Monitoring devices

## Validation and Testing

### 1. Test Device Responsiveness
```bash
# Test motor motion
python scripts/explore_iocs.py --test-device gp:m1 --move-relative 0.1

# Test scaler counting
python scripts/explore_iocs.py --test-device gp:scaler1 --count 1.0

# Test area detector
python scripts/explore_iocs.py --test-device adsim: --acquire 1
```

### 2. Check Data Rates
```bash
# Monitor update rates
python scripts/explore_iocs.py --monitor-rates gp:m1.RBV gp:scaler1.S1

# Typical rates:
# - Motors: ~10 Hz position updates
# - Scalers: Variable (depends on counting)
# - Area detectors: Frame-rate dependent
```

### 3. Identify Connection Issues
```bash
# Check for disconnected PVs
python scripts/explore_iocs.py --check-connections

# Any PVs that don't connect may indicate:
# - IOC not running
# - Network issues  
# - Incorrect PV names
```

## Common IOC Patterns

### Naming Conventions
Most IOCs follow patterns:
- **Motors**: `prefix:m1`, `prefix:m2`, etc.
- **Scalers**: `prefix:scaler1`, `prefix:scaler2`
- **Area Detectors**: `prefix:cam1`, `prefix:image1`

### Device Groupings
Look for logical groupings:
- **Sample stages**: X, Y, Z motors
- **Slits**: Top, Bottom, Left, Right blades
- **Detector groups**: Multiple detector elements

### Support Systems
Don't forget support devices:
- **Shutters**: Safety interlocks
- **Temperature**: Sample environment
- **Diagnostics**: Beam monitoring

## Next Steps

After completing your device inventory:

1. **Review Results**: Ensure you understand available devices
2. **Prioritize Devices**: Choose which to configure first
3. **Plan Configuration**: Think about device names and groupings

## Troubleshooting

### IOCs Won't Start
```bash
# Check if ports are in use
netstat -ln | grep 5064  # EPICS CA port

# Stop existing containers
podman stop adsim_ioc gp_ioc
podman rm adsim_ioc gp_ioc

# Restart with fresh containers
./scripts/start_demo_iocs.sh
```

### Can't Connect to PVs
```bash
# Check EPICS environment
echo $EPICS_CA_ADDR_LIST
echo $EPICS_CA_AUTO_ADDR_LIST

# Set if needed
export EPICS_CA_AUTO_ADDR_LIST=YES
```

### Missing Commands
```bash
# If caget/caput not available
conda activate BITS_demo
pip install pyepics

# Or use the exploration script which doesn't require EPICS tools
```

## Deliverables

After this step, you should have:
- ✅ Running IOCs with known device inventory
- ✅ Understanding of device capabilities and limitations  
- ✅ Prioritized list of devices for Bluesky configuration
- ✅ Tested connectivity to key devices

**Next Step**: [BITS-Starter Setup](02_bits_starter_setup.md)

---

## Reference: Device Types for BITS

| Device Type | EPICS PV Pattern | Bluesky Device Class | Primary Use |
|-------------|------------------|---------------------|-------------|
| Motors | `prefix:m1`, `prefix:motor1` | `EpicsMotor` | Positioning, scanning |
| Scalers | `prefix:scaler1` | `ScalerCH` | Counting, rate monitoring |
| Area Detectors | `prefix:cam1` | `ADBSoftDetector` | Imaging, diffraction |
| Temperature | `prefix:temp1` | `EpicsSignalRO` | Monitoring |
| Calculations | `prefix:calc1` | `EpicsSignal` | Derived values |