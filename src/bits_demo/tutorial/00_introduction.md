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
- **Podman or Docker**: For running example IOCs
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

## Environment Setup

### 1. Create Conda Environment
```bash
# Create isolated environment
conda create -y -n BITS_demo python=3.11
conda activate BITS_demo

# Install BITS framework
pip install apsbits

# Install additional tools
pip install jupyterlab ipython
```

### 2. Get Tutorial Materials
```bash
# Clone or navigate to the tutorial location
cd /path/to/bits_demo

# Verify structure
ls -la tutorial/
ls -la scripts/
ls -la examples/
```

### 3. Test Container System
```bash
# Test Podman installation
podman --version

# Pull the EPICS container (this may take a few minutes)
podman pull ghcr.io/bcda-aps/epics-podman:latest
```

### 4. Verify Python Environment
```python
# Test in Python
import bluesky
import ophyd
import apsbits

print("Environment ready!")
```

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
# Verify everything is ready
conda activate BITS_demo
python -c "import bluesky, ophyd, apsbits; print('✓ All imports successful')"
podman --version && echo "✓ Podman ready"
git --version && echo "✓ Git ready"
echo "✓ Environment ready for tutorial!"
```

### Troubleshooting Common Setup Issues

**Conda Issues**:
```bash
# If conda command not found
source ~/miniconda3/etc/profile.d/conda.sh
# or
source ~/anaconda3/etc/profile.d/conda.sh
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