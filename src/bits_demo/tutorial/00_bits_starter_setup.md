# BITS-Starter Setup

## Overview

**This is the first step in creating your BITS instrument.** You'll fork and clone the BITS-Starter template repository to create your own customizable instrument package.

**Time**: ~10 minutes  
**Goal**: Create your own BITS instrument repository ready for customization

## Prerequisites

### Required Software
- **Git**: Version control system
- **GitHub Account**: For creating your repository
- **Python 3.11+**: Conda or system Python

### Optional but Recommended
- **GitHub CLI**: For command-line repository creation

## What is BITS-Starter?

BITS-Starter is a GitHub template repository that provides:
- Complete instrument package structure
- Working device configuration examples
- Integration with queue server
- Data management setup
- Testing framework
- Production-ready deployment patterns

## Step-by-Step Setup

### 1. Create Your GitHub Repository

**Option A: Using GitHub Web Interface (Recommended)**

1. Go to [BITS-Starter repository](https://github.com/BCDA-APS/BITS-Starter)
2. Click the green **"Use this template"** button
3. Select **"Create a new repository"**
4. Set repository settings:
   - **Repository name**: `my_beamline_bits` (replace with your actual beamline name)
   - **Description**: "BITS instrument for [your beamline] beamline"
   - **Visibility**: Public (recommended for learning)
   - **Include all branches**: Leave unchecked
5. Click **"Create repository from template"**

**Option B: Using GitHub CLI (Alternative)**

```bash
# Create repository from template
gh repo create my_beamline_bits --template BCDA-APS/BITS-Starter --public

# The repository is created but not cloned yet
```

### 2. Clone Your New Repository

```bash
# Navigate to your workspace
mkdir -p ~/workspace
cd ~/workspace

# Clone your repository (replace YOUR_USERNAME with your GitHub username)
git clone https://github.com/YOUR_USERNAME/my_beamline_bits.git
cd my_beamline_bits

# Verify the structure
ls -la
```

**Expected structure:**
```
my_beamline_bits/
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   └── (template instrument files)
├── scripts/
└── tests/
```

### 3. Set Up Python Environment

```bash
# Create BITS environment
conda create -y -n bits_env python=3.11 pyepics
conda activate bits_env

# Install BITS framework
pip install apsbits

# Verify BITS installation
python -c "import apsbits; print('✅ BITS installed:', apsbits.__version__)"
```

### 4. Install Your Instrument Package

```bash
# Install your instrument in development mode
pip install -e .

# This allows you to edit the code and see changes immediately
```

### 5. Verify Installation

```bash
# Test that your instrument package can be imported
python -c "
import sys
print('Python path:', sys.executable)
print('✅ Installation successful')
"
```

## Understanding Your Repository Structure

Your new repository contains:

### Core Files
- **`pyproject.toml`**: Package configuration and dependencies
- **`README.md`**: Project documentation (customize for your beamline)
- **`LICENSE`**: Software license

### Source Code (`src/`)
- **Template instrument files**: Ready to customize for your beamline
- **Configuration examples**: Device and plan templates
- **Queue server setup**: For remote operation

### Development Tools
- **`scripts/`**: Utility scripts for development and deployment
- **`tests/`**: Test framework for validation

## Customization for Your Beamline

### 1. Update Repository Information

Edit `README.md` to describe your beamline:

```markdown
# [Your Beamline] BITS Instrument

BITS instrument package for the [Your Beamline] beamline at [Your Facility].

## Description
[Describe your beamline's purpose, capabilities, and typical experiments]
```

### 2. Update Package Configuration

Edit `pyproject.toml` to match your beamline:

```toml
[project]
name = "my_beamline_bits"  # Replace with your beamline name
description = "BITS instrument for [Your Beamline] beamline"
authors = [
    {name = "Your Name", email = "your.email@facility.org"},
]
```

### 3. Commit Your Customizations

```bash
# Add your changes
git add README.md pyproject.toml

# Commit the customizations
git commit -m "Customize repository for [Your Beamline] beamline

- Update README with beamline description
- Configure package metadata
- Ready for device configuration"

# Push to your repository
git push origin main
```

## Validation

Before proceeding, verify your setup:

```bash
# Check Python environment
conda activate bits_env
python -c "import apsbits; print('✅ BITS available')"

# Check repository
git status
git log --oneline -3

# Check package installation
pip list | grep -E "(apsbits|my-beamline)"
```

**Expected output:**
- ✅ BITS framework installed and importable
- ✅ Repository cloned and customized
- ✅ Package installed in development mode
- ✅ Git repository ready for development

## Next Steps

With your BITS instrument repository created, you're ready to:

1. **Explore your IOCs** to understand available devices
2. **Configure devices** to match your hardware  
3. **Create custom plans** for your experiments
4. **Set up interactive operation** for data acquisition

**→ Next Step**: [IOC Exploration & Device Discovery](01_ioc_exploration.md)

## Troubleshooting

### Repository Creation Issues

**"Use this template" button not visible:**
- Make sure you're logged into GitHub
- Ensure you have permission to create repositories
- Try using Option B (GitHub CLI) instead

**Git clone fails:**
```bash
# Check if Git is installed
git --version

# Verify repository URL
# Make sure to replace YOUR_USERNAME with your actual GitHub username
```

### Python Environment Issues

**Conda command not found:**
```bash
# Source conda initialization
source ~/miniconda3/etc/profile.d/conda.sh
# or
source ~/anaconda3/etc/profile.d/conda.sh
```

**Import errors after installation:**
```bash
# Reinstall in development mode
pip install -e .

# Check if package is installed
pip list | grep my-beamline
```

### Permission Issues

**Can't push to repository:**
```bash
# Check remote URL
git remote -v

# If using HTTPS, you may need to configure Git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Support

If you encounter issues:
1. Check the [BITS-Starter repository](https://github.com/BCDA-APS/BITS-Starter) for updates
2. Review the [BITS documentation](https://github.com/BCDA-APS/BITS)
3. Ensure all prerequisites are properly installed

---

**You now have your own BITS instrument repository!** 🎉

**Next Step**: [IOC Exploration & Device Discovery](01_ioc_exploration.md)