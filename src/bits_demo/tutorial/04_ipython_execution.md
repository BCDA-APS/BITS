# IPython Interactive Execution

## Overview

In this step, you'll learn to use your BITS instrument interactively with IPython. This is the primary way scientists interact with Bluesky for real-time data acquisition, analysis, and troubleshooting.

**Time**: ~30 minutes  
**Goal**: Master interactive operation of your instrument

## Prerequisites

✅ Completed Steps 0-3  
✅ BITS-Starter repository set up  
✅ Working device configurations  
✅ Custom plans created and tested  
✅ IOCs running and responsive

## Understanding IPython for Bluesky

### Why IPython?

IPython provides enhanced interactive Python with:
- **Magic commands**: `%wa`, `%ct`, `%mov` for device control
- **Tab completion**: Discover available methods and attributes
- **Command history**: Recall and modify previous commands
- **Rich display**: Better formatting of results
- **Integration**: Seamless with Bluesky and BITS

### IPython vs Standard Python

| Feature | Standard Python | IPython |
|---------|----------------|---------|
| Device listing | `print(devices)` | `%wa` |
| Help system | `help(function)` | `function?` |
| Command recall | Limited | Full history with search |
| Tab completion | Basic | Enhanced with context |
| Magic commands | None | Many Bluesky-specific commands |

## Starting Your Interactive Session

### 1. Launch IPython

```bash
# Ensure your environment is active
conda activate BITS_demo

# Start IPython
ipython
```

### 2. Load Your Instrument

```python
# Load everything from your instrument
from my_beamline.startup import *

# This imports:
# - RunEngine (RE)
# - All configured devices
# - Standard Bluesky plans (bp.*)
# - Plan stubs (bps.*)
# - Your custom plans
# - Data catalog (cat)
```

**Expected output:**
```
INFO:...:Loading configuration from .../iconfig.yml
INFO:...:Creating devices from devices.yml
INFO:...:RunEngine initialized
INFO:...:Data catalog 'temp' ready
INFO:...:Custom plans loaded
```

### 3. Verify Everything Loaded

```python
# Check RunEngine status
print(f"RunEngine state: {RE.state}")
print(f"Data catalog: {cat.name}")

# List available devices
%wa

# Check recent runs
list(cat)[-3:]  # Last 3 runs (if any exist)
```

## Essential IPython Magic Commands

### Device Management Commands

```python
# List all devices with current values
%wa

# List specific device types
%wa motors     # Only motors
%wa detectors  # Only detectors
%wa baseline   # Only baseline devices

# Move motors (relative)
%mov m1 1.5          # Move m1 to (absolute) position 1.5
%movr m1 0.1         # Move m1 (relative) by +0.1
%movr m1 -0.1 m2 0.2 # Move (relative) multiple motors, m1 by -0.1, m2 by +0.2

# Count (labeled devices)
%ct                  # Count devices with "detectors" label (uses their configured count times)
%ct baseline         # Count devices with "baseline" label  
%ct monitors         # Count devices with "monitors" label
```

### Information Commands

```python
# Get help on any object
motor1?              # Basic info
motor1??             # Source code
bp.scan?             # Help on scan plan

# Show object attributes
motor1.<TAB>         # Tab completion shows available attributes
detector1.<TAB>      # Tab completion for detector attributes

# Command history
%hist                # Show recent commands
%hist -n 10          # Show last 10 commands
%hist -g "scan"      # Search history for "scan"
```

### RunEngine Commands

```python
# RunEngine control
RE.state             # Current state
RE.pause()           # Pause current scan
RE.resume()          # Resume paused scan
RE.stop()            # Stop current scan (abrupt)
RE.abort()           # Return RunEngine to idle gracefully

# Scan history
RE.md                # Current metadata
RE.md['scan_id']     # Current scan ID
```

## Interactive Device Testing

### 1. Motor Testing

```python
# Check motor status
print(f"Motor m1 position: {m1.position}")
print(f"Motor limits: {m1.limits}")
print(f"Motor moving: {m1.moving}")

# Test small moves
initial_pos = m1.position
print(f"Starting at: {initial_pos=}")

# Move relative
RE(bps.mvr(m1, 0.1))
print(f"After +0.1: {m1.position=}")

# Move back
RE(bps.mvr(m1, -0.1))
print(f"Back to: {m1.position=}")

# Absolute move
RE(bps.mv(m1, 0.0))
print(f"At zero: {m1.position=}")
```

### 2. Detector Testing

```python
# Test detector reading
print(f"Scaler connected: {scaler1.connected}")
print(f"Current counts: {scaler1.channels.read()}")

# Simple count
RE(bp.count([scaler1], num=1, delay=1))

# Count with multiple detectors
RE(bp.count([scaler1, scaler2], num=3, delay=2))

# Area detector test (if available)
if 'simdet' in globals():
    print(f"Area detector connected: {simdet.connected}")
    RE(bp.count([simdet], num=1))

# Setting count times for different detector types
# Scaler count time
RE(bps.mv(scaler1.preset_time, 0.1))  # 0.1 s counting time

# Area detector count time
if 'simdet' in globals():
    RE(bps.mv(simdet.cam.acquire_time, 0.1))  # 0.1 s counting time
```

### 3. Combined Device Testing

```python
# Test motor and detector together
print("Testing coordinated motion and detection...")

# Move motor and count at each position
positions = [-0.5, 0, 0.5]
for pos in positions:
    print(f"\nMoving to {pos}")
    RE(bps.mv(m1, pos))
    
    print(f"Counting at {m1.position=}")
    RE(bp.count([scaler1], num=1))
```

## Interactive Scanning

### 1. Basic Scans

```python
# Simple scan
RE(bp.scan([scaler1], m1, -1, 1, 11))

# Relative scan (around current position)
RE(bp.rel_scan([scaler1], m1, -0.5, 0.5, 11))

# List scan (specific positions)
positions = [-1, -0.25, 0, 0.35, 1]  # note irregular spacing
RE(bp.list_scan([scaler1], m1, positions))

# Count without motion
RE(bp.count([scaler1], num=5, delay=1))
```

### 2. Multi-dimensional Scans

```python
# Grid scan with 2 motors
RE(bp.grid_scan([scaler1], 
                m1, -1, 1, 5,    # m1: 5 points from -1 to 1
                m2, -0.5, 0.5, 3, # m2: 3 points from -0.5 to 0.5
                snake_axes=[m2]))  # Snake pattern in m2

# Grid scan with 2 motors and relative positions.
RE(bp.rel_grid_scan([scaler1],
                        m1, -1, 1, 5,
                        m2, -0.5, 0.5, 3))
```

### 3. Using Your Custom Plans

```python
# Load custom plans if not already loaded
from my_beamline.plans.custom_plans import *

# Motor characterization
RE(motor_characterization(m1, scaler1, num_points=21))

# Quick scan around current position
RE(quick_scan(m1, scaler1, range_pm=1.0, points=11))

# Sample alignment
RE(sample_alignment([sample_x, sample_y], scaler1, step_size=0.1))

# Detector optimization
RE(detector_optimization(m1, scaler1, initial_range=2.0))
```

## Real-time Data Analysis

### 1. Live Data Inspection

```python
import datetime

# During or after scans, examine data
run = cat[-1]  # Get most recent run

# Basic run information
print(f"Scan ID: {run.metadata['start']['scan_id']}")
print(f"Plan name: {run.metadata['start']['plan_name']}")
# This is a floating-point time (always in UTC):
print(f"Start time: {run.metadata['start']['time']}")
# This is human-readable time (local time zone when defined):
print(f"Start time: {datetime.datetime.fromtimestamp(run.metadata['start']['time'])}")

# Read data
data = run.primary.read()
print(f"Data variables: {list(data)}")

# Quick plot (if matplotlib available)
try:
    import matplotlib.pyplot as plt, datetime
    
    # Get motor and detector data
    motor_data = data[m1.name]
    detector_data = data[f'{scaler1.channels.chan02.s.name}']  # Adjust as needed
    plan_name = run.metadata["start"].get("plan_name")
    scan_id = run.metadata["start"]["scan_id"]  # If scan_id not available, use 'uid'
    start_time = datetime.datetime.fromtimestamp(run.metadata['start']['time'])
    
    plt.figure()
    plt.plot(motor_data, detector_data, 'o-')
    plt.xlabel(f'{m1.name} position')
    plt.ylabel(f'{scaler1.name} counts')
    supertitle = f'Scan {scan_id}'
    if plan_name is not None:
        supertitle += f" ({plan_name!r})"
    plt.suptitle(supertitle)
    plt.title(f'started {start_time}')
    plt.show()
    
except ImportError:
    print("Matplotlib not available for plotting")
```

### 2. Data Export

```python
# Export to CSV
import pandas as pd

# Convert to DataFrame
df = data.to_dataframe()
print(df.head())

# Save to file
filename = f"scan_{run.metadata['start']['scan_id']}.csv"
df.to_csv(filename)
print(f"Data saved to {filename}")
```

## Advanced Interactive Techniques

### 1. Custom Metadata

```python
# Add custom metadata to scans
custom_md = {
    'sample': 'test_sample_001',
    'temperature': 295.0,
    'operator': 'your_name',
    'notes': 'Testing new setup'
}

# RE returns list of run uids.  Keep the first one for ...
uid, = RE(bp.scan([scaler1], m1, -1, 1, 11, md=custom_md))

# Verify metadata was saved using uid reported by RE above.
latest_run = cat[uid]
print("Custom metadata:")
for key, value in custom_md.items():
    print(f"  {key}: {latest_run.metadata['start'].get(key, 'Not found')}")
```

### 2. Multi-step Procedures

```python
# Complex measurement procedure
def measurement_procedure():
    """Multi-step measurement with error handling."""
    
    print("Starting measurement procedure...")
    
    # Step 1: Align sample
    print("Step 1: Sample alignment")
    yield from sample_alignment([sample_x, sample_y], scaler1)
    
    # Step 2: Optimize detector
    print("Step 2: Detector optimization")
    yield from detector_optimization(m1, scaler1)
    
    # Step 3: Take measurement
    print("Step 3: Main measurement")
    yield from bp.scan([scaler1], m1, -2, 2, 41)
    
    print("Measurement procedure complete!")

# Execute procedure
RE(measurement_procedure())
```

## Troubleshooting Interactive Sessions

### 1. Common Issues

```python
# Device connection issues
if not m1.connected:
    print("Motor m1 not connected!")
    # Check IOC status, EPICS environment

# RunEngine stuck
if RE.state != 'idle':
    print(f"RunEngine state: {RE.state}")
    # May need RE.abort().  Alternative is RE.stop()

# Memory issues with large datasets
import gc
gc.collect()  # Force garbage collection
```

### 2. Debugging Tools

```python
# Enable verbose logging
import logging
logging.getLogger('bluesky').setLevel(logging.DEBUG)

# Check device details
m1.summary()     # Summarize the 'm1' object
scaler1.describe() # Detailed detector info

# Monitor device values
m1.subscribe(lambda **kwargs: print(f"Motor moved to {kwargs['value']}"))
```

## Best Practices

### 1. Session Workflow

1. **Start Clean**: Always start with `from my_instrument.startup import *`
2. **Check Status**: Use `%wa` to verify device status
3. **Test First**: Test devices with small moves before big scans
4. **Save Work**: Export important data regularly
5. **Document**: Add meaningful metadata to all scans

### 2. Safety Practices

```python
# Always check motor limits before large moves
print(f"Motor limits: {m1.limits}")
print(f"Current position: {m1.position}")

# Use relative moves for safety
RE(bps.mvr(m1, 0.1))  # Safer than absolute moves

# Check detector count rates
RE(bp.count([scaler1], num=1))
# Verify reasonable count rates before long scans
```

### 3. Efficiency Tips

```python
# Use IPython features
# - Tab completion: motor1.<TAB>
# - Command history: Up arrow, Ctrl+R to search
# - Magic commands: %wa, %ct, %mov

# Combine operations efficiently
RE(bps.mv(m1, 1.0, m2, 2.0))  # Move multiple motors simultaneously

# Use meaningful variable names
current_run = cat[-1]
motor_pos = m1.position
```

## Session Documentation

<!--
TODO:
After the NX School, let's replace all content in this section with tools that
harvest all this content from databroker or tiled.  The example here encourages
duplication of effort and code.
-->

### 1. Keep a Session Log

```python
# Create session documentation
session_log = {
    'date': '2024-01-15',
    'operator': 'scientist_name',
    'sample': 'test_sample_001',
    'objectives': 'Test new alignment procedure',
    'scans_completed': [],
    'issues_encountered': [],
    'next_steps': []
}

# Update after each major operation
session_log['scans_completed'].append({
    'scan_id': cat[-1].metadata['start']['scan_id'],
    'plan': 'motor_characterization',
    'purpose': 'Characterize m1 response'
})
```

### 2. Export Session Summary

```python
# Generate session summary
def session_summary():
    recent_runs = list(cat)[-10:]  # Last 10 runs
    
    print(f"Session Summary ({len(recent_runs)} recent runs):")
    print("-" * 40)
    
    for run in recent_runs:
        start_time = run.metadata['start']['time']
        scan_id = run.metadata['start']['scan_id']
        plan_name = run.metadata['start']['plan_name']
        
        print(f"  {scan_id:>3}: {plan_name:<20} at {start_time}")

# Run at end of session
session_summary()
```

## Deliverables

After completing this step, you should be able to:

- ✅ Start IPython and load your instrument efficiently
- ✅ Use magic commands for device control and inspection
- ✅ Perform interactive scans and device testing
- ✅ Access and analyze data in real-time
- ✅ Handle common troubleshooting scenarios
- ✅ Document and save your work appropriately

## Next Steps

With interactive operation mastered, you're ready for:
- **Jupyter notebooks** for analysis and documentation
- **Queue server** for remote and automated operation  
- **Advanced data visualization** with specialized tools

**Next Step**: Advanced topics (Queue Server, Data Analysis, Production Deployment)

---

## Reference: Essential IPython Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `%wa` | List all devices | `%wa motors` |
| `%mov` | Move motors | `%mov m1 2.5` |
| `%movr` | Relative move | `%movr m1 0.1` |
| `%ct` | Count detectors | `%ct baseline` |
| `object?` | Get help | `bp.scan?` |
| `object.<TAB>` | Tab completion | `motor1.<TAB>` |
| `%hist` | Command history | `%hist -n 10` |

## Common Scan Patterns

| Pattern | Command | Use Case |
|---------|---------|----------|
| Point measurement | `bp.count([det], num=5)` | Detector characterization |
| Linear scan | `bp.scan([det], motor, -1, 1, 21)` | Response curves |
| Relative scan | `bp.rel_scan([det], motor, -0.5, 0.5, 11)` | Local optimization |
| List scan | `bp.list_scan([det], motor, positions)` | Specific points |
| Grid scan | `bp.grid_scan([det], m1, -1, 1, 5, m2, -1, 1, 5)` | 2D mapping |