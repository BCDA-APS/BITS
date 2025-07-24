# Plan Development

## Overview

In this step, you'll create custom scan plans tailored to your configured devices. You'll learn about Bluesky plan structure, create plans for common scientific use cases, and test them with your IOCs.

**Time**: ~25 minutes  
**Goal**: Working custom scan plans for your instrument

## Prerequisites

✅ Completed Steps 1-3  
✅ Working device configurations  
✅ Devices connected and responsive  
✅ Basic device operations tested

## Understanding Bluesky Plans

### What are Plans?

Plans are Python generators that describe what to do during a measurement:
- **Move devices** to positions
- **Trigger detectors** to collect data  
- **Read devices** and save data
- **Control timing** and sequencing

### Plan Types

| Plan Type | Purpose | Example |
|-----------|---------|---------|
| **Basic Plans** | Standard scans | `scan()`, `count()`, `rel_scan()` |
| **Custom Plans** | Your specific needs | Motor characterization, sample alignment |
| **Composite Plans** | Multiple measurements | Temperature series, batch processing |

### Plan Structure

```python
def my_plan(motor, detector, position, *, metadata=None):
    """A custom plan that properly collects data."""
    # Setup
    yield from bps.open_run(md=metadata)  # Start data collection
    
    # Measurement steps
    yield from bps.mv(motor, position)      # Move motor
    yield from bps.create("primary")        # Create event document
    yield from bps.read(motor)              # Read motor position
    yield from bps.trigger_and_read(detector) # Read detector
    yield from bps.save()                   # Save event document
    
    # Cleanup  
    yield from bps.close_run()  # End data collection
```

**Important Note**: The built-in bluesky plans handle `open_run`/`close_run` and `create`/`save` automatically. Only custom plans need explicit data collection statements.

## Built-in Plans Review

Before creating custom plans, let's review the built-in plans:

### 1. Test Built-in Plans

```python
# Start IPython session
from my_beamline.startup import *
import bluesky.plans as bp
import bluesky.plan_stubs as bps

# Count detectors (no motion)
RE(bp.count([scaler1], num=3, delay=1))

# Scan motor vs detector
RE(bp.scan([scaler1], m1, -1, 1, 11))

# Relative scan (around current position)  
RE(bp.rel_scan([scaler1], m1, -0.5, 0.5, 11))

# List scan (specific positions)
positions = [-1, -0.5, 0, 0.5, 1]
RE(bp.list_scan([scaler1], m1, positions))

# Multi-dimensional scan
RE(bp.grid_scan([scaler1], 
                m1, -1, 1, 5,    # m1: 5 points from -1 to 1
                m2, -0.5, 0.5, 3, # m2: 3 points from -0.5 to 0.5
                snake_axes=[m2]))  # Snake scanning in m2
```

## Creating Custom Plans

### 1. Create Plans Directory

```bash
# Create plans file for your custom plans
touch src/my_beamline/plans/custom_plans.py
```

### 2. Motor Characterization Plan

Edit `src/my_beamline/plans/custom_plans.py`:

```python
"""
Custom scan plans for my_beamline instrument
"""
import bluesky.plans as bp
import bluesky.plan_stubs as bps
from bluesky.utils import short_uid
import numpy as np


def motor_characterization(motor, detector, *, 
                          range_fraction=0.8, 
                          num_points=21,
                          metadata=None):
    """
    Characterize motor response over its full range.
    
    Parameters
    ----------
    motor : ophyd.Motor
        Motor to scan
    detector : ophyd.Device
        Detector to read
    range_fraction : float, optional
        Fraction of motor range to use (default: 0.8)
    num_points : int, optional
        Number of scan points (default: 21)
    metadata : dict, optional
        Additional metadata for the run
    """
    # Get motor limits
    low_limit, high_limit = motor.limits
    
    # Calculate scan range
    center = (high_limit + low_limit) / 2
    full_range = high_limit - low_limit
    scan_range = full_range * range_fraction
    
    start = center - scan_range / 2
    stop = center + scan_range / 2
    
    # Build metadata
    _metadata = {
        'plan_name': 'motor_characterization',
        'motor': motor.name,
        'detector': detector.name,
        'scan_range': [start, stop],
        'motor_limits': [low_limit, high_limit],
        'purpose': f'Characterize {motor.name} response'
    }
    if metadata:
        _metadata.update(metadata)
    
    # Perform the scan
    yield from bp.scan([detector], motor, start, stop, num_points, md=_metadata)


def sample_alignment(sample_motors, detector, *,
                    step_size=0.1, 
                    scan_range=2.0,
                    metadata=None):
    """
    Align sample by scanning each motor individually.
    
    Parameters
    ----------
    sample_motors : list
        List of motors to scan (e.g., [sample_x, sample_y])
    detector : ophyd.Device
        Detector for alignment signal
    step_size : float, optional
        Step size for scanning (default: 0.1)
    scan_range : float, optional
        Total range to scan (default: 2.0)
    metadata : dict, optional
        Additional metadata
    """
    num_points = int(scan_range / step_size) + 1
    half_range = scan_range / 2
    
    results = {}
    
    for motor in sample_motors:
        print(f"Aligning {motor.name}...")
        
        # Build metadata for this motor scan
        _metadata = {
            'plan_name': 'sample_alignment',
            'motor': motor.name,
            'detector': detector.name,
            'alignment_axis': motor.name,
            'purpose': f'Sample alignment scan for {motor.name}'
        }
        if metadata:
            _metadata.update(metadata)
        
        # Scan this motor
        yield from bp.rel_scan([detector], motor, 
                              -half_range, half_range, num_points,
                              md=_metadata)
        
        # Store scan info for reference
        results[motor.name] = {
            'range': [-half_range, half_range],
            'points': num_points,
            'step_size': step_size
        }
    
    print(f"Sample alignment complete for {len(sample_motors)} axes")
    return results


def temperature_series(temperature_controller, temperature_list, 
                      detectors, measurement_plan, *,
                      settle_time=60,
                      metadata=None):
    """
    Perform measurements at different temperatures.
    
    Parameters
    ----------
    temperature_controller : ophyd.Device
        Device to control temperature
    temperature_list : list
        List of temperatures to measure at
    detectors : list
        List of detectors to read
    measurement_plan : callable
        Plan to execute at each temperature
    settle_time : float, optional
        Time to wait after temperature change (default: 60 seconds)
    metadata : dict, optional
        Additional metadata
    """
    # Build metadata
    _metadata = {
        'plan_name': 'temperature_series',
        'temperature_controller': temperature_controller.name,
        'temperature_list': temperature_list,
        'settle_time': settle_time,
        'purpose': 'Temperature-dependent measurements'
    }
    if metadata:
        _metadata.update(metadata)
    
    yield from bps.open_run(md=_metadata)
    
    for i, temp in enumerate(temperature_list):
        print(f"Setting temperature to {temp} ({i+1}/{len(temperature_list)})")
        
        # Set temperature
        yield from bps.mv(temperature_controller, temp)
        
        # Wait for settlement
        if settle_time > 0:
            print(f"Waiting {settle_time}s for temperature to settle...")
            yield from bps.sleep(settle_time)
        
        # Take measurement
        print(f"Taking measurement at {temp}")
        yield from measurement_plan(detectors)
        
    yield from bps.close_run()


def detector_optimization(motor, detector, *,
                         initial_range=2.0,
                         refinement_cycles=2,
                         metadata=None):
    """
    Optimize detector signal by iterative refinement.
    
    This plan:
    1. Does a coarse scan to find approximate peak
    2. Refines the search around the peak
    3. Repeats refinement for better accuracy
    
    Parameters
    ----------
    motor : ophyd.Motor
        Motor to optimize
    detector : ophyd.Device  
        Detector to maximize
    initial_range : float, optional
        Initial scan range (default: 2.0)
    refinement_cycles : int, optional
        Number of refinement cycles (default: 2)  
    metadata : dict, optional
        Additional metadata
    """
    # Build metadata
    _metadata = {
        'plan_name': 'detector_optimization',
        'motor': motor.name,
        'detector': detector.name,
        'initial_range': initial_range,
        'refinement_cycles': refinement_cycles,
        'purpose': f'Optimize {detector.name} signal using {motor.name}'
    }
    if metadata:
        _metadata.update(metadata)
    
    yield from bps.open_run(md=_metadata)
    
    # Initial coarse scan
    current_range = initial_range
    center_pos = motor.position
    
    for cycle in range(refinement_cycles + 1):
        half_range = current_range / 2
        num_points = 11 if cycle == 0 else 21  # More points for refinement
        
        print(f"Optimization cycle {cycle + 1}: range ±{half_range:.3f}")
        
        # Perform scan around current center
        yield from bp.rel_scan([detector], motor,
                              -half_range, half_range, num_points,
                              md={'optimization_cycle': cycle + 1})
        
        # For refinement cycles, narrow the range
        if cycle < refinement_cycles:
            current_range *= 0.3  # Narrow range for next iteration
            # In practice, you'd analyze data to find new center
            # For demo, we'll just use current position
            center_pos = motor.position
    
    yield from bps.close_run()
    print(f"Detector optimization complete")


def batch_sample_measurement(sample_positions, measurement_plan, 
                           position_motors, detectors, *,
                           metadata=None):
    """
    Measure multiple samples at different positions.
    
    Parameters
    ----------
    sample_positions : list of tuples
        List of (x, y, z) positions or (x, y) positions
    measurement_plan : callable
        Plan to execute at each position
    position_motors : list
        Motors for positioning [x_motor, y_motor, z_motor] or [x_motor, y_motor]
    detectors : list
        Detectors to use in measurements
    metadata : dict, optional
        Additional metadata
    """
    # Build metadata
    _metadata = {
        'plan_name': 'batch_sample_measurement',
        'num_samples': len(sample_positions),
        'position_motors': [m.name for m in position_motors],
        'purpose': 'Automated batch sample measurements'
    }
    if metadata:
        _metadata.update(metadata)
    
    yield from bps.open_run(md=_metadata)
    
    for i, position in enumerate(sample_positions):
        print(f"Moving to sample {i+1}/{len(sample_positions)}: {position}")
        
        # Move to sample position
        for motor, pos in zip(position_motors, position):
            yield from bps.mv(motor, pos)
        
        # Add sample metadata
        sample_md = {
            'sample_number': i + 1,
            'sample_position': position,
        }
        
        # Take measurement
        yield from measurement_plan(detectors, md=sample_md)
        
    yield from bps.close_run()
    print(f"Batch measurements complete: {len(sample_positions)} samples")
```

### 3. Load Your Custom Plans

```python
# In IPython session, reload your plans
import importlib
import my_beamline.plans.custom_plans as cp
importlib.reload(cp)

# Make plans available
from my_beamline.plans.custom_plans import *
```

### 4. Test Custom Plans

```python
# Test motor characterization
RE(motor_characterization(m1, scaler1, num_points=11))

# Test sample alignment with multiple motors
sample_motors = [sample_x, sample_y]
RE(sample_alignment(sample_motors, scaler1, step_size=0.05, scan_range=1.0))

# Test detector optimization
RE(detector_optimization(m1, scaler1, initial_range=1.0, refinement_cycles=1))
```

## Creating Plan Wrappers

### 1. Convenience Functions

Create wrapped plans for easier use:

```python
# Add to custom_plans.py

def quick_scan(motor, detector, range_pm=1.0, points=21):
    """Quick relative scan around current position."""
    return bp.rel_scan([detector], motor, -range_pm, range_pm, points)

def count_detectors(time=1, num=1):
    """Count all detectors for specified time."""
    import bluesky.preprocessors as bpp
    detectors = list(bpp._devices_by_label['detectors'])
    return bp.count(detectors, num=num, delay=time)

def home_all_motors():
    """Home all motors to their center positions."""
    import bluesky.preprocessors as bpp
    motors = list(bpp._devices_by_label['motors'])
    
    def _home_plan():
        for motor in motors:
            low, high = motor.limits
            center = (low + high) / 2
            yield from bps.mv(motor, center)
    
    return _home_plan()
```

### 2. Specialized Scientific Plans

```python
# Add to custom_plans.py

def powder_diffraction_scan(theta_motor, detector, 
                          theta_start=10, theta_end=80, 
                          step_size=0.02, count_time=1):
    """
    Standard powder diffraction scan.
    """
    num_points = int((theta_end - theta_start) / step_size) + 1
    
    metadata = {
        'plan_name': 'powder_diffraction',
        'theta_range': [theta_start, theta_end],
        'step_size': step_size,
        'count_time': count_time,
        'measurement_type': 'powder_diffraction'
    }
    
    # Set detector count time if possible
    if hasattr(detector, 'preset_time'):
        yield from bps.mv(detector.preset_time, count_time)
    
    yield from bp.scan([detector], theta_motor, 
                      theta_start, theta_end, num_points, 
                      md=metadata)

def rocking_curve(motor, detector, center, width=2.0, points=41):
    """
    Rocking curve measurement around a center position.
    """
    metadata = {
        'plan_name': 'rocking_curve',
        'center_position': center,
        'scan_width': width,
        'measurement_type': 'rocking_curve'
    }
    
    half_width = width / 2
    start = center - half_width
    end = center + half_width
    
    yield from bp.scan([detector], motor, start, end, points, md=metadata)
```

## Plan Testing and Validation

### 1. Create Plan Test Script

Create `scripts/test_plans.py`:

```python
#!/usr/bin/env python3
"""Test custom plans with dry runs."""

def test_plans():
    """Test all custom plans with simulation mode."""
    from my_beamline.startup import *
    from my_beamline.plans.custom_plans import *
    
    # Enable simulation mode for testing
    RE.simulate_mode = True
    
    print("🧪 Testing Custom Plans (Simulation Mode)")
    print("=" * 50)
    
    try:
        # Test motor characterization
        print("1. Testing motor_characterization...")
        RE(motor_characterization(m1, scaler1, num_points=5))
        print("   ✅ motor_characterization completed")
        
        # Test sample alignment  
        print("2. Testing sample_alignment...")
        RE(sample_alignment([sample_x, sample_y], scaler1, 
                           scan_range=1.0, step_size=0.2))
        print("   ✅ sample_alignment completed")
        
        # Test detector optimization
        print("3. Testing detector_optimization...")
        RE(detector_optimization(m1, scaler1, 
                               initial_range=1.0, refinement_cycles=1))
        print("   ✅ detector_optimization completed")
        
        # Test convenience functions
        print("4. Testing convenience functions...")
        RE(quick_scan(m1, scaler1, range_pm=0.5, points=5))
        print("   ✅ quick_scan completed")
        
        print("\n🎉 All plan tests passed!")
        
    except Exception as e:
        print(f"❌ Plan test failed: {e}")
        return False
    finally:
        # Disable simulation mode
        RE.simulate_mode = False
    
    return True

if __name__ == "__main__":
    test_plans()
```

### 2. Test with Real Devices

```python
# Test with real devices (small motions)
# Make sure IOCs are running first!

# Test quick scan
RE(quick_scan(m1, scaler1, range_pm=0.2, points=5))

# Test motor characterization with small range
RE(motor_characterization(m1, scaler1, range_fraction=0.1, num_points=11))
```

## Data Analysis Integration

### 1. Plans with Analysis

```python
# Add to custom_plans.py

def scan_with_peak_finding(motor, detector, start, stop, num_points):
    """
    Scan and automatically find peak position.
    """
    import numpy as np
    from bluesky.callbacks import LiveFit
    from lmfit.models import GaussianModel
    
    # Setup live fitting
    model = GaussianModel()
    init_guess = {
        'amplitude': 1000,
        'center': (start + stop) / 2, 
        'sigma': (stop - start) / 10
    }
    
    lf = LiveFit(model, 'y', {'x': motor.name}, init_guess)
    
    # Perform scan with live fitting
    yield from bp.scan([detector], motor, start, stop, num_points, 
                      md={'analysis': 'peak_finding'})
    
    # Results would be available in lf.result after scan
```

### 2. Plans with Data Validation

```python
def validated_scan(motor, detector, start, stop, num_points, *,
                  min_counts=100, max_count_rate=1e6):
    """
    Scan with real-time data validation.
    """
    def validation_callback(name, doc):
        """Check data quality during scan."""
        if doc['name'] == 'primary':
            data = doc['data']
            if detector.name in data:
                counts = data[detector.name]
                if counts < min_counts:
                    print(f"⚠️  Low counts: {counts}")
                elif counts > max_count_rate:
                    print(f"⚠️  High count rate: {counts}")
    
    # Subscribe to validation callback
    token = RE.subscribe(validation_callback)
    
    try:
        yield from bp.scan([detector], motor, start, stop, num_points,
                          md={'data_validation': True})
    finally:
        RE.unsubscribe(token)
```

## Plan Organization

### 1. Plan Categories

Organize plans by scientific purpose:

```python
# In custom_plans.py, organize by category

# === ALIGNMENT PLANS ===
def sample_alignment(...): pass
def detector_optimization(...): pass

# === CHARACTERIZATION PLANS ===  
def motor_characterization(...): pass
def detector_response(...): pass

# === SCIENTIFIC MEASUREMENTS ===
def powder_diffraction_scan(...): pass
def rocking_curve(...): pass
def temperature_series(...): pass

# === UTILITY PLANS ===
def quick_scan(...): pass
def count_detectors(...): pass
def home_all_motors(...): pass
```

### 2. Plan Documentation

```python
def my_plan(motor, detector, **kwargs):
    """
    One-line description of the plan.
    
    Longer description explaining the scientific purpose,
    when to use this plan, and what it accomplishes.
    
    Parameters
    ----------
    motor : EpicsMotor
        Motor to scan
    detector : ScalerCH or similar
        Detector to measure
    **kwargs : dict
        Additional keyword arguments passed to underlying plans
    
    Returns
    -------
    generator
        Bluesky plan generator
    
    Examples
    --------
    >>> RE(my_plan(m1, scaler1, num_points=21))
    """
    # Plan implementation
    pass
```

## Integration with Instrument

### 1. Add Plans to Startup

Edit `src/my_beamline/startup.py` to automatically load custom plans:

```python
# Add at the end of startup.py

# Load custom plans
try:
    from .plans.custom_plans import *
    logger.info("✅ Custom plans loaded successfully")
    
    # Print available custom plans
    custom_plans = [
        'motor_characterization',
        'sample_alignment', 
        'detector_optimization',
        'quick_scan',
        'count_detectors'
    ]
    logger.info(f"Available custom plans: {', '.join(custom_plans)}")
    
except ImportError as e:
    logger.warning(f"⚠️  Could not load custom plans: {e}")
```

### 2. Plan Help System

```python
# Add to custom_plans.py

def list_custom_plans():
    """List all available custom plans with descriptions."""
    plans = {
        'motor_characterization': 'Scan motor over its full range',
        'sample_alignment': 'Align sample using multiple motors',
        'detector_optimization': 'Optimize detector signal iteratively',
        'quick_scan': 'Quick relative scan around current position',
        'count_detectors': 'Count all detectors for specified time',
        'powder_diffraction_scan': 'Standard powder diffraction measurement',
        'rocking_curve': 'Rocking curve around specified position'
    }
    
    print("📋 Available Custom Plans:")
    print("=" * 40)
    for plan_name, description in plans.items():
        print(f"  {plan_name:<25}: {description}")
    print("\nUse help(plan_name) for detailed information")

def plan_examples():
    """Show example usage of custom plans."""
    examples = """
    📚 Plan Usage Examples:
    =====================
    
    # Motor characterization
    RE(motor_characterization(m1, scaler1, num_points=21))
    
    # Sample alignment
    RE(sample_alignment([sample_x, sample_y], scaler1, step_size=0.1))
    
    # Quick scan
    RE(quick_scan(m1, scaler1, range_pm=1.0, points=11))
    
    # Count detectors
    RE(count_detectors(time=2, num=3))
    
    # Powder diffraction
    RE(powder_diffraction_scan(theta, detector, 10, 80, step_size=0.05))
    """
    print(examples)
```

## Deliverables

After completing this step, you should have:

- ✅ Custom plans tailored to your instrument
- ✅ Motor characterization and optimization plans  
- ✅ Sample alignment procedures
- ✅ Scientific measurement plans
- ✅ Convenience functions for common tasks
- ✅ Plan testing and validation framework
- ✅ Integration with your instrument startup

## Commit Your Progress

```bash
# Add the new plans
git add src/my_beamline/plans/custom_plans.py
git add scripts/test_plans.py

# Commit changes
git commit -m "Add custom scan plans

- Motor characterization and optimization plans
- Sample alignment procedures  
- Scientific measurement plans (powder diffraction, rocking curves)
- Convenience functions for common operations
- Plan testing framework
- Integration with instrument startup
- Examples and documentation
"
```

**Next Step**: [IPython Interactive Use](05_ipython_execution.md)

---

## Reference: Common Plan Patterns

### Basic Plan Structure
```python
def my_plan(devices, *, parameters, metadata=None):
    """Use keyword-only parameters for safety."""
    yield from bps.open_run(md=metadata)
    yield from bps.create("primary")
    # measurement steps
    yield from bps.save()
    yield from bps.close_run()
```

### Plan Building Blocks
| Function | Purpose |
|----------|---------|
| `bps.mv(device, value)` | Move device to value |
| `bps.mvr(device, value)` | Move device relatively |
| `bps.create(stream_name)` | Create event document |
| `bps.read(device)` | Read device (without triggering) |
| `bps.trigger_and_read(devices)` | Trigger and read devices |
| `bps.save()` | Save event document |
| `bps.sleep(time)` | Wait for specified time |
| `bp.scan(detectors, motor, start, stop, num)` | Standard scan (handles data collection) |