# BITS-Starter Setup

## Overview

In this step, you'll create your own instrument package using the BITS-Starter template. This gives you a complete, working Bluesky instrument that you can customize for your IOCs.

**Time**: ~15 minutes  
**Goal**: Create a working instrument package ready for customization

## Prerequisites

✅ Completed Step 1: IOC Exploration  
✅ Demo IOCs running (adsim_ioc and gp_ioc)  
✅ BITS environment activated

## What is BITS-Starter?

BITS-Starter is a GitHub template repository that provides:
- Complete instrument package structure
- Working device configuration examples
- Integration with queue server
- Data management setup
- Testing framework

## Step-by-Step Setup

### 1. Create Your GitHub Repository

**Option A: Using GitHub Web Interface**
1. Go to [BITS-Starter repository](https://github.com/BCDA-APS/BITS-Starter)
2. Click "Use this template" → "Create a new repository"
3. Set repository name: `my_beamline_bits` (replace with your actual beamline)
4. Choose visibility (public recommended for learning)
5. Click "Create repository from template"

**Option B: Using GitHub CLI (if available)**
```bash
# Create repository from template
gh repo create my_beamline_bits --template BCDA-APS/BITS-Starter --public

# Clone your new repository
git clone https://github.com/YOUR_USERNAME/my_beamline_bits.git
cd my_beamline_bits
```

### 2. Clone and Setup Local Repository

```bash
# Navigate to your workspace
cd ~/workspace  # or your preferred location

# Clone your repository (replace with your actual repo URL)
git clone https://github.com/YOUR_USERNAME/my_beamline_bits.git
cd my_beamline_bits

# Verify structure
ls -la
# Should see: LICENSE, README.md, pyproject.toml, src/
```

### 3. Install BITS Framework

```bash
# Ensure BITS environment is active
conda activate BITS_demo

# Install BITS if not already installed
pip install apsbits

# Verify installation
python -c "import apsbits; print('✅ BITS installed:', apsbits.__version__)"
```

### 4. Create Your Instrument Package

```bash
# Set your instrument name (choose something meaningful for your beamline)
export YOUR_INSTRUMENT_NAME=my_beamline

# Create the instrument package
create-bits $YOUR_INSTRUMENT_NAME

# This creates src/my_beamline/ with complete structure
```

**What `create-bits` does:**
- Creates instrument package in `src/YOUR_INSTRUMENT_NAME/`
- Sets up configuration files (`configs/`)
- Creates device definitions (`devices/`)
- Adds scan plans (`plans/`)
- Configures data callbacks (`callbacks/`)
- Sets up queue server configuration
- Creates startup module

### 5. Install Your Instrument Package

```bash
# Install in development mode (allows live editing)
pip install -e .

# Verify installation
python -c "import $YOUR_INSTRUMENT_NAME; print('✅ Instrument package installed')"
```

### 6. Test Basic Functionality

```bash
# Test import
python -c "from $YOUR_INSTRUMENT_NAME.startup import *; print('✅ Startup import successful')"
```

**Expected output includes:**
- Logging configuration messages
- Device creation messages  
- RunEngine initialization
- Callback setup messages

## Understanding Your Package Structure

Let's explore what was created:

```bash
# Show complete structure
tree src/$YOUR_INSTRUMENT_NAME/

# Expected structure:
src/my_beamline/
├── __init__.py
├── startup.py              # Main entry point
├── callbacks/
│   ├── __init__.py
│   ├── nexus_data_file_writer.py
│   └── spec_data_file_writer.py
├── configs/
│   ├── __init__.py
│   ├── devices.yml         # Device definitions
│   ├── devices_aps_only.yml
│   ├── iconfig.yml         # Instrument configuration
│   └── logging.yml
├── devices/
│   └── __init__.py
├── plans/
│   ├── __init__.py
│   ├── dm_plans.py         # Data management plans
│   └── sim_plans.py        # Simulation plans
├── suspenders/
│   └── __init__.py
└── utils/
    └── __init__.py
```

### Key Files

**`startup.py`**: Main instrument initialization
- Loads configuration
- Creates RunEngine 
- Sets up devices
- Configures callbacks

**`configs/iconfig.yml`**: Instrument configuration
- Data management settings
- RunEngine metadata
- File writing options
- Timeout settings

**`configs/devices.yml`**: Device definitions
- Maps PV names to Bluesky devices
- Sets device labels and properties

## Test with Simulation Plans

Your new instrument comes with built-in test plans:

### 1. Start IPython Session
```bash
# Start IPython
ipython
```

### 2. Load Your Instrument
```python
# Import everything from your instrument
from my_beamline.startup import *

# This loads:
# - RunEngine (RE)
# - Devices from device configs
# - Data management setup
# - Standard Bluesky plans
```

### 3. Run Test Plans
```python
# Run simulation plans to verify everything works
RE(sim_print_plan())   # Simple print test
RE(sim_count_plan())   # Simulated counting
RE(sim_rel_scan_plan()) # Simulated scanning

# Check RunEngine status
print(RE.state)  # Should be 'idle'

# List available devices  
%wa  # Show all devices (currently simulated ones)
```

**Expected output:**
- Plan execution messages
- Simulated data generation
- File writing notifications
- No error messages

### 4. Verify Data Management
```python
# Check if data was saved
import databroker
cat = databroker.catalog['temp']  # Default catalog name

# List recent runs
list(cat)[-3:]  # Show last 3 runs

# Examine a run
run = cat[-1]  # Most recent run
run.metadata
run.primary.read()  # Read data
```

## Configuration Overview

### Instrument Configuration (`configs/iconfig.yml`)

Key settings to understand:

```yaml
# Catalog for data storage
DATABROKER_CATALOG: &databroker_catalog temp

# RunEngine metadata
RUN_ENGINE:
    DEFAULT_METADATA:
        beamline_id: my_beamline          # Your beamline identifier
        instrument_name: "My Beamline"    # Human readable name
        proposal_id: commissioning        # Current proposal
        databroker_catalog: *databroker_catalog

# File writing options
SPEC_DATA_FILES:
    ENABLE: true           # Write SPEC format files
    FILE_EXTENSION: dat

NEXUS_DATA_FILES:
    ENABLE: false          # NeXus files (set true if needed)
    FILE_EXTENSION: hdf
```

### Device Configuration (`configs/devices.yml`)

Currently contains simulated devices:

```yaml
# Example simulated devices (you'll replace these)
simulators:
  noisy:
    device_class: SynGauss
    name: 'noisy'
    motor: 'noisy_det'
    motor_field: 'motor'
    detector: 'noisy_det'
    detector_field: 'noisy_det'
    sigma: 1
    noise: 'uniform'
    noise_multiplier: 0.1
    labels: ["detectors"]
```

## Next Steps Preview

In the next step, you'll:
1. Replace simulated devices with real IOC devices
2. Configure motors from your gp IOC
3. Configure scalers and area detector
4. Test connectivity to real hardware

## Validation

Verify your setup is ready:

```bash
# Check installation
python -c "
from my_beamline.startup import *
print('✅ Instrument loads successfully')
print('✅ RunEngine available:', type(RE))
print('✅ Catalog available:', cat.name)
"

# Check queue server configuration exists
ls src/my_beamline_qserver/
# Should show: qs-config.yml, qs_host.sh, user_group_permissions.yaml
```

## Troubleshooting

### Import Errors
```bash
# If import fails, reinstall package
pip uninstall my_beamline -y
pip install -e .
```

### Missing Commands
```bash
# If create-bits not found
pip install apsbits --upgrade

# Verify command is available
which create-bits
```

### Configuration Errors
```bash
# Check configuration file syntax
python -c "
import yaml
with open('src/my_beamline/configs/iconfig.yml') as f:
    config = yaml.safe_load(f)
    print('✅ Configuration file is valid YAML')
"
```

### Permission Issues
```bash
# Fix file permissions if needed
chmod -R u+w src/
```

## Customization Tips

Before moving to the next step, you might want to:

### 1. Update Metadata
Edit `configs/iconfig.yml`:
```yaml
RUN_ENGINE:
    DEFAULT_METADATA:
        beamline_id: 8id_bits      # Your actual beamline
        instrument_name: "8-ID BITS"  # Your instrument name
        proposal_id: "2024-2"     # Current proposal
```

### 2. Update Repository Information
Edit `README.md` to describe your specific instrument.

### 3. Commit Your Changes
```bash
# Add all files
git add .

# Commit initial setup
git commit -m "Initial BITS instrument setup

- Created instrument package: my_beamline
- Configured basic settings
- Tested simulation functionality
"

# Push to GitHub
git push origin main
```

## Deliverables

After completing this step, you should have:
- ✅ GitHub repository with BITS-Starter template
- ✅ Working instrument package installed locally  
- ✅ Successful test with simulation plans
- ✅ Understanding of package structure and configuration
- ✅ Ready to configure real IOC devices

**Next Step**: [Device Configuration](03_device_configuration.md)

---

## Reference: Package Structure Explanation

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `configs/` | Configuration files | `iconfig.yml`, `devices.yml` |
| `devices/` | Custom device classes | Python device implementations |
| `plans/` | Scan plan definitions | Custom scanning procedures |
| `callbacks/` | Data writing callbacks | NeXus, SPEC file writers |
| `utils/` | Utility functions | Helper functions |
| `suspenders/` | Suspend/resume logic | Safety interlocks |

## Common Commands Reference

| Command | Purpose |
|---------|---------|
| `create-bits name` | Create new instrument package |
| `pip install -e .` | Install package in development mode |
| `from name.startup import *` | Load instrument in Python |
| `RE(plan())` | Execute a scan plan |
| `%wa` | List all devices (IPython magic) |