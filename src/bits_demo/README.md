# BITS Demo Tutorial

## Complete Tutorial: From IOCs to Production BITS Deployment

This comprehensive tutorial takes beamline scientists from understanding their EPICS IOCs to creating a fully functional BITS deployment with their own GitHub repository.

### Tutorial Overview

**Target Audience**: Beamline scientists with EPICS IOCs who want to implement Bluesky data acquisition

**Prerequisites**:
- Running EPICS IOCs (we provide containerized examples)
- Basic Python knowledge
- Git/GitHub familiarity
- Linux/macOS environment

**Time Commitment**: ~2-3 hours for complete tutorial

**End Result**: Production-ready BITS deployment in your own GitHub repository

### Tutorial Steps

| Step | Topic | Duration | Deliverable |
|------|-------|----------|-------------|
| [00](tutorial/00_introduction.md) | Introduction & Prerequisites | 10 min | Environment setup |
| [01](tutorial/01_ioc_exploration.md) | IOC Exploration & Device Discovery | 20 min | Device inventory |
| [02](tutorial/02_bits_starter_setup.md) | BITS-Starter Template Setup | 15 min | Instrument package |
| [03](tutorial/03_device_configuration.md) | Device Configuration | 30 min | Working devices |
| [04](tutorial/04_plan_development.md) | Scan Plan Development | 25 min | Custom plans |
| [05](tutorial/05_ipython_execution.md) | IPython Interactive Use | 15 min | Live operation |
| [06](tutorial/06_jupyter_notebooks.md) | Jupyter Notebook Analysis | 20 min | Analysis notebooks |
| [07](tutorial/07_queueserver_setup.md) | Queue Server Remote Execution | 20 min | Remote capability |
| [08](tutorial/08_tiled_visualization.md) | Data Visualization with Tiled | 15 min | Data browser |
| [09](tutorial/09_github_deployment.md) | GitHub Deployment Repository | 15 min | Production repo |
| [10](tutorial/10_verification_testing.md) | Final Verification & Testing | 10 min | Validated system |

### Quick Start

```bash
# 1. Start the demo IOCs
cd bits_demo/scripts
./start_demo_iocs.sh

# 2. Explore your IOCs
python explore_iocs.py

# 3. Follow the tutorial step by step
# Start with tutorial/00_introduction.md
```

### What You'll Learn

- **IOC Understanding**: How to discover and categorize devices in your IOCs
- **BITS Architecture**: Complete understanding of the BITS framework
- **Device Integration**: Map EPICS PVs to Bluesky devices
- **Plan Development**: Create custom scan plans for your science
- **Data Management**: Handle, visualize, and export your data
- **Remote Operation**: Set up queue server for remote execution  
- **Production Deployment**: Create a maintainable, shareable system

### What You'll Build

By the end of this tutorial, you'll have:

1. **Working Instrument Package**: Complete BITS deployment controlling your IOCs
2. **GitHub Repository**: Professional deployment repository with documentation
3. **Custom Scan Plans**: Tailored to your experimental needs
4. **Data Analysis Tools**: Jupyter notebooks and visualization setup
5. **Remote Capabilities**: Queue server for unattended operation
6. **Validation Framework**: Tools to verify system functionality

### Support & Troubleshooting

- **Scripts**: Automated validation and troubleshooting tools in `scripts/`
- **Examples**: Working examples for all concepts in `examples/`
- **Templates**: Ready-to-use templates in `templates/`
- **Documentation**: Comprehensive guides in `tutorial/`

### Getting Help

If you encounter issues:
1. Check the troubleshooting section in each tutorial step
2. Run validation scripts in `scripts/`
3. Compare with working examples in `examples/`
4. Review the FAQ in the final verification step

### Container IOCs Provided

This tutorial includes two containerized IOCs for learning:

- **adsim IOC** (`adsim:`): Area Detector simulation with 2D detector
- **gp IOC** (`gp:`): General purpose IOC with 20 motors, 3 scalers, and support records

These provide a realistic learning environment without requiring physical hardware.

### Next Steps

After completing this tutorial:
- Adapt the examples to your actual hardware
- Customize scan plans for your science requirements  
- Deploy to your beamline environment
- Share with your team through GitHub
- Extend with additional devices and capabilities

---

**Ready to start?** → Begin with [Tutorial Introduction](tutorial/00_introduction.md)