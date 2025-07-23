# Tutorial Introduction & Prerequisites

## Welcome to BITS Demo Tutorial

This tutorial will guide you through creating a complete Bluesky data acquisition system using the BITS framework. By the end, you'll have a production-ready deployment that can control your EPICS IOCs.

## Learning Objectives

After completing this tutorial, you will:
- Understand how to discover and categorize devices in your IOCs
- Know how to configure Bluesky devices to match your hardware
- Be able to create custom scan plans for your experiments
- Have experience with interactive and remote data acquisition
- Know how to visualize and analyze your data
- Have created a maintainable deployment repository

## Prerequisites

### Required Knowledge
- **Basic Python**: Variables, functions, imports
- **EPICS Basics**: Understanding of Process Variables (PVs) and IOCs
- **Git/GitHub**: Basic version control operations
- **Command Line**: Basic terminal/shell operations

### Required Software
- **Python 3.11+**: Conda or system Python
- **Git**: Version control system
- **Podman**: For running example IOCs
- **Modern Web Browser**: For Jupyter notebooks and monitoring tools

### Hardware Requirements
- **4GB RAM minimum** (8GB recommended)
- **2GB free disk space**
- **Network access** for GitHub and package installation

## Tutorial IOCs

This tutorial uses two containerized IOCs that simulate real beamline hardware:

### Area Detector IOC (adsim:)
- **Purpose**: Simulates a 2D detector
- **Key PVs**: Image acquisition, file saving, statistics
- **Use Cases**: Area detector scans, image analysis

### General Purpose IOC (gp:)  
- **Purpose**: Simulates standard beamline devices
- **Devices**: 20 motors (m1-m20), 3 scalers, calculation records
- **Use Cases**: Motor scans, counting measurements

## Tutorial Flow

### Phase 1: Discovery & Setup (Steps 1-2)
Learn what devices are available and set up your development environment.

### Phase 2: Configuration (Steps 3-4)
Configure devices and create scan plans to control your hardware.

### Phase 3: Operation (Steps 5-7)
Use your system interactively, remotely, and for analysis.

### Phase 4: Deployment (Steps 8-10)
Create production deployment and verify complete system.

## BITS Development Workflow

This tutorial follows the complete BITS development workflow from environment setup to running instrument.

### 1. Create Necessary Environment and Folder Structure
```bash
# Create working directory
mkdir -p ~/beamline_workspace
cd ~/beamline_workspace

# Create project structure
mkdir -p tutorial_workspace
cd tutorial_workspace
echo "BITS tutorial workspace created at: $(pwd)"
```

### 2. Install BITS (Following Official BITS Guide)
```bash
# Check if conda is available
which conda

# If conda command not found, source the initialization script:
# source ~/miniconda3/etc/profile.d/conda.sh  # Adjust path as needed

# Create BITS environment (following official BITS naming)
conda create -y -n bits_env python=3.11 pyepics
conda activate bits_env

# Install BITS framework
pip install apsbits

# Verify installation
python -c "import apsbits; print('✓ BITS installed')"
```

### 3. Create Your First Instrument (Official BITS Method)
```bash
# Create a new project directory
mkdir my_beamline && cd my_beamline

# Create instrument using BITS API
python -m apsbits.api.create_new_instrument my_instrument

# Install the instrument
pip install -e .

# Test instrument import
python -c "from my_instrument.startup import *; print('Instrument ready!')"
```

**What BITS creates (following official structure):**
- `src/my_instrument/startup.py` - Entry point (REQUIRED)
- `src/my_instrument/configs/iconfig.yml` - Main instrument config
- `src/my_instrument/devices/` - Custom device implementations
- `src/my_instrument/plans/` - Custom scan plans
- `src/my_instrument/callbacks/` - Data writing and processing
- `src/my_instrument_qserver/` - Queue server configuration

### 4. Test Your Instrument with BITS Simulation
```bash
# Verify components loaded (BITS official way)
python -c "
from my_instrument.startup import *
print(f'RunEngine: {RE}')
print(f'Catalog: {cat}')

# Test with built-in simulation plans
RE(sim_print_plan())        # Print scan information
RE(sim_count_plan())        # Simulate data collection
RE(sim_rel_scan_plan())     # Simulate a scan
"
```

**Expected output:**
```
RunEngine: <bluesky.run_engine.RunEngine object>
Catalog: <intake_bluesky.jsonl.BlueskyJSONLCatalog object>

# Simulation plans will show scan progress and simulated data
```

### 5. Container: Check, Build (if necessary), and Run
```bash
# Check Podman installation
podman --version

# Pull pre-built EPICS container (recommended)
podman pull ghcr.io/bcda-aps/epics-podman:latest
podman tag ghcr.io/bcda-aps/epics-podman:latest epics-podman:latest

# Verify container is available
podman images | grep epics-podman

# Start the demo IOCs container
podman run -d --name demo_iocs \
  --network=host \
  epics-podman:latest

# Check container is running
podman ps | grep demo_iocs
```

**Alternative: Build from source (if needed):**
```bash
# Download and build container from source
curl -L https://github.com/BCDA-APS/epics-podman/raw/main/Containerfile -o Containerfile
podman build -t epics-podman:latest -f Containerfile .
```

### 6. Check IOCs are Running
```bash
# Test IOC connectivity using EPICS tools
# Wait a few seconds for IOCs to fully start
sleep 10

# Test General Purpose IOC (gp:)
caget gp:m1.VAL gp:m2.VAL gp:scaler1.CNT

# Test Area Detector IOC (adsim:)
caget adsim:cam1:Acquire adsim:cam1:ImageMode

# If caget command not found, install EPICS base tools or use container:
# podman exec demo_iocs caget gp:m1.VAL

echo "✅ IOCs are running and responding"
```

**Expected output:**
```
gp:m1.VAL                      0
gp:m2.VAL                      0  
gp:scaler1.CNT                 0
adsim:cam1:Acquire             0
adsim:cam1:ImageMode           2
```

## Next Phase: Connect Your Instrument to Real Hardware

With your BITS instrument created (using simulation) and IOCs running, you're ready to connect to real hardware and proceed through the tutorial sequence:

### 7. Connect to Real IOCs (Next Step)
```python
# After IOCs are confirmed running, connect your instrument to them
from my_instrument.startup import *

# The following tutorials will show you how to:
# - Replace simulation devices with real EPICS devices  
# - Configure device connections using IOC PVs
# - Create custom plans for your specific hardware
```

**→ Next Step**: [IOC Exploration & Device Discovery](01_ioc_exploration.md)

In the following tutorials, you'll learn the **official BITS way** to:
1. **Explore IOCs** - Discover available devices and process variables from real hardware
2. **Configure Devices** - Map IOC PVs to BITS device objects using proper configuration
3. **Create Plans** - Develop custom scan plans following BITS patterns
4. **Interactive Use** - Test your instrument with live data acquisition
5. **Remote Execution** - Set up queue server for multi-user operations

All tutorials follow the [BITS documentation](../../../docs/) for authentic development patterns and best practices.

## Container vs Real Hardware

This tutorial uses containerized IOCs for learning, but the principles apply directly to real hardware:

- **Container IOCs**: Perfect for learning and development
- **Real IOCs**: Same configuration approach, different PV prefixes
- **Hybrid Approach**: Start with containers, migrate to real hardware

## Time Commitment

| Phase | Steps | Time | Activity |
|-------|-------|------|----------|
| Setup | 0 | 15 min | Environment preparation |
| Discovery | 1 | 20 min | IOC exploration |
| Configuration | 2-4 | 60 min | Device and plan setup |
| Operation | 5-7 | 50 min | Interactive and remote use |
| Deployment | 8-10 | 40 min | Production deployment |
| **Total** | | **~3 hours** | Complete tutorial |

## Support Resources

### During Tutorial
- **Validation Scripts**: Check setup at each step
- **Example Configurations**: Working examples for reference
- **Troubleshooting Guides**: Common issues and solutions

### After Tutorial
- **Template Repository**: Starting point for new instruments
- **Documentation**: Comprehensive references
- **Community**: BITS user community and support

## Getting Help

If you encounter problems:
1. **Check Prerequisites**: Ensure all software is installed
2. **Run Validation**: Use provided validation scripts  
3. **Review Examples**: Compare with working examples
4. **Consult Documentation**: Detailed guides for each step

## Ready to Start?

Once you've completed the environment setup, you're ready to begin:

**Next Step**: [IOC Exploration & Device Discovery](01_ioc_exploration.md)

---

### Quick Environment Check
```bash
# Verify everything is ready (using official BITS environment name)
conda activate bits_env
python -c "import apsbits; print('✓ BITS installed')"
podman --version && echo "✓ Podman ready"
echo "✓ Environment ready for tutorial!"
```

### Troubleshooting Common Setup Issues (Following BITS Documentation)

**Import errors after creating devices (from BITS docs)**:
```bash
# Solution: Reinstall the package
pip install -e .
```

**EPICS connection timeouts (from BITS docs)**:
```python
# Solution: Use SIM: prefix for testing
# In devices.yml, use "SIM:DEVICE" instead of real PV names
```

**Plans not found after creation (from BITS docs)**:
```python
# Solution: Check imports in plans/__init__.py
from .my_plans import my_plan_name
```

**Conda Issues**:
```bash
# If conda command not found, try these in order:
source ~/miniconda3/etc/profile.d/conda.sh
# or
source ~/anaconda3/etc/profile.d/conda.sh
# or for Linux package manager installs
source /opt/miniconda3/etc/profile.d/conda.sh
# or
source /usr/local/miniconda3/etc/profile.d/conda.sh

# Alternative: Add conda to PATH permanently
echo 'export PATH="~/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Permission Issues with Podman**:
```bash
# Add user to podman group (Linux)
sudo groupadd podman
sudo usermod -aG podman $USER
# Log out and back in
```

**Import Errors**:
```bash
# Reinstall packages
pip uninstall apsbits -y
pip install apsbits
```