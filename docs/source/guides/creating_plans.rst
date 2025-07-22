.. _creating_plans:

Creating Scan Plans in BITS
============================

This comprehensive guide covers scan plan creation in BITS, from simple custom plans to advanced patterns using apstools and real-world deployment examples.

Quick Start: Create a Basic Plan
---------------------------------

**Create a custom scan plan in 3 steps:**

.. code-block:: python

    # 1. plans/my_plans.py - Create plan
    from bluesky.plans import count
    from bluesky import plan_stubs as bps

    def sample_count(detector, num=1, exposure=0.1):
        """Simple counting plan with detector setup."""
        yield from bps.mv(detector.cam.acquire_time, exposure)
        yield from count([detector], num=num)

.. code-block:: python

    # 2. plans/__init__.py - Import plan
    from .my_plans import sample_count
    __all__ = ["sample_count"]

.. code-block:: python

    # 3. Test the plan
    from my_instrument.startup import *
    RE(sample_count(detector, num=5, exposure=0.5))

Complete Plan Creation Guide
----------------------------

Understanding BITS Plan Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BITS plans follow the Bluesky plan structure with additional patterns:

.. code-block:: text

    src/my_instrument/
    ├── plans/                  # Plan modules
    │   ├── __init__.py         # Import plans
    │   ├── basic_scans.py      # Standard scan plans
    │   ├── alignment.py        # Alignment procedures
    │   ├── calibration.py      # Calibration routines
    │   ├── data_collection.py  # Production data collection
    │   ├── simulation.py       # Development/simulation plans
    │   └── dm_plans.py         # Data management integration
    └── startup.py              # Plans available after import

**Plan Categories in BITS:**

1. **Basic Scans** - Standard bluesky plans with instrument-specific setup
2. **Alignment Plans** - Using apstools alignment capabilities
3. **Data Management Plans** - APS Data Management workflow integration
4. **Calibration Plans** - Standardized calibration procedures
5. **Simulation Plans** - Development and testing plans

Using apstools Plan Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Alignment Plans with apstools:**

.. code-block:: python

    # plans/alignment.py - Using apstools alignment
    from apstools.plans import lineup2, TuneAxis
    from bluesky import plan_stubs as bps
    import logging

    logger = logging.getLogger(__name__)
    logger.bsdev(__file__)  # BITS logging convention

    def align_sample_position(detector, sample_stage):
        """Align sample using beam center finding."""
        
        # Align X position
        yield from lineup2(
            [detector.stats1.total],  # Signal to optimize
            sample_stage.x,           # Motor to scan
            -1.0, 1.0,               # Range (mm)
            21                       # Number of points
        )
        
        # Align Y position
        yield from lineup2(
            [detector.stats1.total],
            sample_stage.y,
            -1.0, 1.0,
            21
        )

    def tune_motor_axis(detector, motor, initial_range=2.0):
        """Auto-tune motor position using apstools TuneAxis."""
        
        tuner = TuneAxis([detector.stats1.total], motor)
        
        # Configure tuner
        tuner.range = initial_range  # mm
        tuner.num = 21
        tuner.peak_choice = "max"  # or "min" for absorption
        
        # Execute tuning
        yield from tuner.tune()
        
        # Log results
        logger.info(f"Tuned {motor.name} to {motor.position}")

**Excel-Based Command Execution:**

.. code-block:: python

    # plans/excel_plans.py - Excel integration from apstools
    from apstools.plans import run_command_file
    from bluesky import plan_stubs as bps
    from pathlib import Path

    def execute_excel_protocol(excel_file, sheet_name="default"):
        """Execute scan protocol from Excel spreadsheet."""
        
        # Validate file exists
        excel_path = Path(excel_file)
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_file}")
        
        # Log execution start
        yield from bps.mv(RE.md["excel_file"], str(excel_path))
        yield from bps.mv(RE.md["sheet_name"], sheet_name)
        
        # Execute commands from Excel
        yield from run_command_file(excel_file, sheet_name=sheet_name)

    def sample_series_from_excel(excel_file="sample_list.xlsx"):
        """Process multiple samples from Excel list."""
        
        # Read sample information
        import pandas as pd
        samples = pd.read_excel(excel_file, sheet_name="samples")
        
        for _, sample in samples.iterrows():
            # Update metadata
            yield from bps.mv(RE.md["sample_name"], sample["name"])
            yield from bps.mv(RE.md["composition"], sample["composition"])
            
            # Move to sample position
            yield from bps.mv(sample_stage.x, sample["x_pos"])
            yield from bps.mv(sample_stage.y, sample["y_pos"])
            
            # Execute scan protocol
            yield from execute_excel_protocol(
                sample["protocol_file"], 
                sheet_name=sample.get("sheet", "default")
            )

Creating Custom Scan Plans
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Basic Data Collection Plans:**

.. code-block:: python

    # plans/data_collection.py - Production data collection
    from bluesky.plans import count, scan, rel_scan
    from bluesky import plan_stubs as bps
    from bluesky.preprocessors import run_decorator

    @run_decorator(md={"plan_name": "production_count"})
    def production_count(detectors, num=1, delay=0, **metadata):
        """Production counting plan with full metadata."""
        
        # Add standard metadata
        yield from bps.mv(RE.md["num_points"], num)
        yield from bps.mv(RE.md["delay"], delay)
        
        # Update with user metadata
        for key, value in metadata.items():
            yield from bps.mv(RE.md[key], value)
        
        # Configure detectors
        for detector in detectors:
            if hasattr(detector, 'cam'):
                yield from bps.mv(detector.cam.num_images, 1)
        
        # Execute count
        yield from count(detectors, num=num, delay=delay)

    @run_decorator(md={"plan_name": "temperature_series"})
    def temperature_series(detectors, temperature_controller, 
                          temp_start, temp_stop, temp_step):
        """Temperature series measurement."""
        
        import numpy as np
        temperatures = np.arange(temp_start, temp_stop + temp_step, temp_step)
        
        for temp in temperatures:
            # Set temperature
            yield from bps.mv(temperature_controller.setpoint, temp)
            
            # Wait for stability (temperature-dependent)
            stability_time = max(60, abs(temp - temp_start) * 2)  # seconds
            yield from bps.sleep(stability_time)
            
            # Check temperature stability
            temp_actual = yield from bps.rd(temperature_controller.readback)
            if abs(temp_actual - temp) > 1.0:  # 1K tolerance
                logger.warning(f"Temperature unstable: {temp_actual} vs {temp}")
            
            # Collect data
            yield from production_count(
                detectors, 
                num=1,
                temperature_setpoint=temp,
                temperature_actual=temp_actual
            )

**Advanced Scan Patterns:**

.. code-block:: python

    # plans/advanced_scans.py - Complex scanning patterns
    from bluesky.plans import spiral, grid_scan, adaptive_scan
    from bluesky.plan_stubs import abs_set, trigger_and_read
    from bluesky.preprocessors import baseline_decorator

    @baseline_decorator([aps_current, beamline_energy])
    def sample_mapping(detector, sample_stage, map_size, step_size):
        """2D sample mapping with baseline monitoring."""
        
        # Calculate scan parameters
        num_x = int(map_size['x'] / step_size) + 1
        num_y = int(map_size['y'] / step_size) + 1
        
        # Execute grid scan
        yield from grid_scan(
            [detector],
            sample_stage.x, -map_size['x']/2, map_size['x']/2, num_x,
            sample_stage.y, -map_size['y']/2, map_size['y']/2, num_y,
            snake_axes=True  # Efficient scanning pattern
        )

    def adaptive_peak_finding(detector, motor, initial_range=5.0):
        """Adaptive scan that focuses on interesting regions."""
        
        def peak_decision(name, doc):
            """Decide whether to continue scanning based on signal."""
            if doc['data'][detector.name] > threshold:
                return "continue"  # Keep scanning in this region
            else:
                return "abort"    # Move to next region
        
        yield from adaptive_scan(
            [detector], 
            motor, 
            start=motor.position - initial_range/2,
            stop=motor.position + initial_range/2,
            min_step=0.1,
            max_step=1.0,
            target_delta=0.05,
            decision_func=peak_decision
        )

Environment-Specific Plans
~~~~~~~~~~~~~~~~~~~~~~~~~

**Simulation vs Production Plans:**

.. code-block:: python

    # plans/simulation.py - Development and testing plans
    from bluesky.plans import count
    from bluesky.plan_stubs import mv, sleep
    from apsbits.utils.aps_functions import host_on_aps_subnet

    def sim_alignment_plan(detector, motor):
        """Simulated alignment for development."""
        
        # Simulate motor scan
        positions = [-2, -1, 0, 1, 2]  # mm
        for pos in positions:
            yield from mv(motor, pos)
            yield from sleep(0.1)  # Simulate settling time
            
            # Simulate detector response (peak at center)
            simulated_intensity = 1000 * np.exp(-(pos**2)/2)
            detector.sim_intensity.put(simulated_intensity)
            
            yield from count([detector])

    def production_alignment_plan(detector, motor):
        """Real alignment for production."""
        from apstools.plans import lineup2
        
        yield from lineup2([detector], motor, -2, 2, 21)

    # Use environment detection to select plan
    if host_on_aps_subnet():
        alignment_plan = production_alignment_plan
    else:
        alignment_plan = sim_alignment_plan

**Configuration-Driven Plans:**

.. code-block:: python

    # plans/configurable.py - Configuration-driven plans
    from apsbits.utils.config_loaders import get_config

    def configurable_scan_plan(detector, motor, scan_config=None):
        """Scan plan driven by configuration."""
        
        if scan_config is None:
            iconfig = get_config()
            scan_config = iconfig.get("DEFAULT_SCAN_CONFIG", {})
        
        # Extract parameters from configuration
        start = scan_config.get("start", -5.0)
        stop = scan_config.get("stop", 5.0)
        num = scan_config.get("num_points", 21)
        exposure = scan_config.get("exposure_time", 0.1)
        
        # Configure detector
        if hasattr(detector, 'cam'):
            yield from bps.mv(detector.cam.acquire_time, exposure)
        
        # Execute scan
        yield from rel_scan([detector], motor, start, stop, num)

Data Management Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Data Management Workflow Plans:**

.. code-block:: python

    # plans/dm_plans.py - Data management integration (from 12-ID deployment)
    from apstools.devices import DM_WorkflowConnector
    from apstools.utils import dm_api_proc
    from bluesky import plan_stubs as bps
    import logging

    logger = logging.getLogger(__name__)
    logger.bsdev(__file__)

    def dm_kickoff_workflow(run, args_dict, timeout=None, wait=False):
        """Start a DM workflow for this bluesky run."""
        
        dm_workflow = DM_WorkflowConnector(name="dm_workflow")
        
        if timeout is None:
            timeout = 999_999_999_999  # Effectively forever
            
        yield from bps.mv(dm_workflow.concise_reporting, True)
        yield from bps.mv(dm_workflow.reporting_period, timeout)
        
        # Configure workflow
        yield from bps.mv(dm_workflow.workflow, args_dict.get("workflowName"))
        yield from bps.mv(dm_workflow.workflow_args, args_dict)
        
        # Start workflow
        yield from bps.trigger(dm_workflow, wait=wait)
        
        logger.info(f"Started DM workflow: {args_dict.get('workflowName')}")

    def dm_integrated_scan(detectors, scan_plan, workflow_name, **workflow_args):
        """Scan with automatic data management workflow."""
        
        # Execute the scan
        scan_result = yield from scan_plan(detectors)
        
        # Get the run information
        run_uid = scan_result[0]  # First return is typically the run UUID
        
        # Prepare workflow arguments
        dm_args = {
            "workflowName": workflow_name,
            "runUid": run_uid,
            "experimentName": RE.md.get("experiment_name", "unknown"),
            **workflow_args
        }
        
        # Start data management workflow
        yield from dm_kickoff_workflow(run_uid, dm_args, wait=False)

**Metadata and Documentation Plans:**

.. code-block:: python

    # plans/documentation.py - Automatic documentation
    from apstools.plans import doc_run
    from bluesky import plan_stubs as bps

    def documented_scan(detectors, scan_plan, documentation=None):
        """Scan with automatic documentation."""
        
        # Add documentation to run metadata
        if documentation:
            yield from bps.mv(RE.md["scan_documentation"], documentation)
            yield from bps.mv(RE.md["scan_purpose"], documentation.get("purpose", ""))
            yield from bps.mv(RE.md["expected_results"], documentation.get("expected", ""))
        
        # Use apstools doc_run for documentation
        yield from doc_run(
            documentation.get("title", "Undocumented scan"),
            scan_plan(detectors)
        )

Safety and Interlock Plans
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Plans with Safety Checks:**

.. code-block:: python

    # plans/safety.py - Plans with safety interlocks
    from bluesky.plans import scan
    from bluesky.plan_stubs import mv, rd
    from bluesky.preprocessors import finalize_decorator

    def safe_motor_scan(detector, motor, start, stop, num):
        """Motor scan with safety checks and automatic recovery."""
        
        # Record initial position for recovery
        initial_position = yield from rd(motor.position)
        
        def restore_position():
            """Recovery function."""
            yield from mv(motor, initial_position)
            logger.info(f"Restored {motor.name} to {initial_position}")
        
        # Safety checks before scan
        if abs(start) > motor.limits[1] or abs(stop) > motor.limits[1]:
            raise ValueError(f"Scan range exceeds motor limits: {motor.limits}")
        
        # Check beam conditions
        beam_current = yield from rd(aps_current.value)
        if beam_current < 50:  # mA
            logger.warning(f"Low beam current: {beam_current} mA")
        
        # Execute scan with automatic recovery
        @finalize_decorator(restore_position)
        def protected_scan():
            yield from scan([detector], motor, start, stop, num)
        
        yield from protected_scan()

**Suspender Integration:**

.. code-block:: python

    # plans/suspenders.py - Integration with suspender systems
    from bluesky.suspenders import SuspendFloor, SuspendCeil

    def setup_beam_suspenders():
        """Configure beam-related suspenders."""
        
        # Suspend if beam current too low
        beam_suspender = SuspendFloor(
            aps_current.value,
            50,  # mA threshold
            sleep=60  # seconds to wait before resuming
        )
        
        # Suspend if shutter closes
        shutter_suspender = SuspendFloor(
            beamline_shutter.status,
            0.5,  # Open threshold
            sleep=1
        )
        
        RE.install_suspender(beam_suspender)
        RE.install_suspender(shutter_suspender)
        
        return [beam_suspender, shutter_suspender]

Plan Testing and Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Plan Testing Framework:**

.. code-block:: python

    # tests/test_plans.py - Plan testing
    import pytest
    from bluesky.tests.utils import DocCollector
    from my_instrument.plans import production_count

    def test_production_count(RE, detector):
        """Test production count plan."""
        
        # Use document collector to capture plan output
        collector = DocCollector()
        RE(production_count([detector], num=3), collector)
        
        # Validate documents
        assert len(collector.start_docs) == 1
        assert len(collector.stop_docs) == 1
        assert len(collector.event_docs) == 3  # 3 counts
        
        # Check metadata
        start_doc = collector.start_docs[0]
        assert start_doc["plan_name"] == "production_count"
        assert start_doc["num_points"] == 3

    def test_plan_with_simulated_hardware(RE):
        """Test plan with simulated devices."""
        from ophyd.sim import det, motor
        
        # Run plan with simulated devices
        RE(alignment_plan(det, motor))
        
        # Verify plan executed successfully
        assert motor.position != motor._initial_position

**Dry Run and Simulation:**

.. code-block:: python

    # plans/validation.py - Plan validation utilities
    from bluesky.simulators import summarize_plan

    def validate_plan_structure(plan, *args, **kwargs):
        """Validate plan structure without execution."""
        
        # Generate plan messages
        plan_generator = plan(*args, **kwargs)
        
        # Summarize plan structure
        summary = summarize_plan(plan_generator)
        
        print("Plan Summary:")
        print(f"Motors: {summary.get('motors', [])}")
        print(f"Detectors: {summary.get('detectors', [])}")
        print(f"Estimated time: {summary.get('time', 'unknown')} seconds")
        
        return summary

    def dry_run_plan(plan, *args, **kwargs):
        """Execute plan in simulation mode."""
        
        # Store original RE state
        original_state = RE.state
        
        try:
            # Switch to simulation mode
            RE.simulate_mode = True
            
            # Execute plan
            result = RE(plan(*args, **kwargs))
            
            print("Dry run completed successfully")
            return result
            
        finally:
            # Restore original state
            RE.simulate_mode = False

Plan Organization and Import Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Plan Module Organization:**

.. code-block:: python

    # plans/__init__.py - Comprehensive plan imports
    """Scan plans for instrument."""
    
    # Basic scans
    from .basic_scans import (
        production_count,
        temperature_series,
        sample_mapping
    )
    
    # Alignment plans
    from .alignment import (
        align_sample_position,
        tune_motor_axis
    )
    
    # Data management plans
    from .dm_plans import (
        dm_kickoff_workflow,
        dm_integrated_scan
    )
    
    # Excel integration
    from .excel_plans import (
        execute_excel_protocol,
        sample_series_from_excel
    )
    
    # Environment-specific imports
    from apsbits.utils.aps_functions import host_on_aps_subnet
    
    if host_on_aps_subnet():
        from .production import production_plans
        __all__ = production_plans + [
            "production_count", "align_sample_position", 
            "dm_integrated_scan", "execute_excel_protocol"
        ]
    else:
        from .simulation import simulation_plans  
        __all__ = simulation_plans + [
            "production_count", "align_sample_position"
        ]

**Conditional Plan Loading:**

.. code-block:: python

    # plans/conditional.py - Environment-aware plan loading
    import logging
    from apsbits.utils.config_loaders import get_config

    logger = logging.getLogger(__name__)

    def load_beamline_plans():
        """Load plans appropriate for current environment."""
        
        iconfig = get_config()
        beamline_mode = iconfig.get("BEAMLINE_MODE", "development")
        
        if beamline_mode == "production":
            from .production_plans import *
            logger.info("Loaded production plans")
            
        elif beamline_mode == "commissioning":
            from .commissioning_plans import *
            from .diagnostic_plans import *
            logger.info("Loaded commissioning and diagnostic plans")
            
        else:
            from .simulation_plans import *
            logger.info("Loaded simulation plans")

AI Integration Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~

**bAIt Plan Analysis:**

.. code-block:: python

    # AI rules for plan validation
    def analyze_plan_structure(plan_file):
        """bAIt rules for plan analysis."""
        
        validation_rules = {
            "bluesky_compliance": "Check for proper yield from usage",
            "error_handling": "Validate exception handling patterns", 
            "metadata_integration": "Ensure proper metadata usage",
            "safety_checks": "Verify safety and interlock integration",
            "documentation": "Check for docstrings and comments",
            "apstools_usage": "Identify opportunities to use apstools plans"
        }
        
        return validate_plan_rules(plan_file, validation_rules)

Best Practices Summary
~~~~~~~~~~~~~~~~~~~~~~

**DO:**
- Use apstools plans when available (lineup2, TuneAxis, etc.)
- Follow bluesky plan conventions (yield from, plan decorators)
- Include comprehensive metadata in all plans
- Test plans with simulated devices before production use
- Implement safety checks and recovery mechanisms

**DON'T:**
- Create custom alignment plans when apstools provides equivalent functionality
- Skip error handling and safety validation
- Hardcode device names or parameters in plans
- Forget to document plan purpose and expected behavior
- Mix simulation and production code without environment detection

**Next Steps:**

1. :doc:`Integrate plans with data management workflows <dm>`
2. :doc:`Deploy plans in queue server environment <qserver>`
3. :doc:`Create comprehensive testing strategies <testing>`
4. :doc:`Set up production monitoring and logging <monitoring>`