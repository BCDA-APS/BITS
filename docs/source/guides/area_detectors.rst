.. _area_detectors:

Area Detector Configuration Patterns
=====================================

This guide covers area detector setup in BITS, from simple configurations to advanced patterns using apstools factories and version compatibility.

Quick Start: Basic Area Detector
---------------------------------

**YAML-First Approach (Recommended):**

Start with YAML configuration - easier and more maintainable:

.. code-block:: yaml

    # 1. configs/devices.yml - Use apstools factory directly
    apstools.devices.ad_creator:
    - name: adsim
      prefix: "IOC:ADSIM:"
      detector_class: "SimDetectorCam"  # Works in containerized environments
      plugins: ["image", "stats1", "hdf1"]  # Numbered plugins follow convention
      labels: ["detectors", "primary"]

.. code-block:: python

    # 2. Test immediately - this creates a working detector
    from my_instrument.startup import *
    
    # Verify detector is functional
    print(f"Detector: {adsim.name}, Connected: {adsim.connected}")
    
    # Test acquisition
    RE(count([adsim]))

**Alternative Python Approach:**

If you need custom detector classes:

.. code-block:: python

    # devices/detectors.py - Custom detector class
    from apstools.devices import ad_creator
    
    # Create functional detector with proper plugin setup
    adsim = ad_creator(
        "IOC:ADSIM:",
        name="adsim", 
        detector_class="SimDetectorCam",
        plugins=["image", "stats1", "hdf1"]  # This creates a working detector
    )

.. important::
   **Why SimDetectorCam for Tutorials?** ADSimDetector is available in all
   containerized environments and provides realistic detector behavior without
   requiring specialized hardware. This makes tutorials immediately testable.
   
   **Production Transition:** To use real detectors, simply change:
   
   - ``detector_class: "SimDetectorCam"`` → ``"PilatusDetectorCam"``
   - ``prefix: "IOC:ADSIM:"`` → ``"12IDA:PILATUS:"`` (actual IOC prefix)
   - Test with your actual IOC running
   
   All plugin configurations and patterns remain identical.

Complete Area Detector Guide
-----------------------------

Understanding Area Detector Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Area detectors in BITS follow the EPICS Area Detector architecture:

.. code-block:: text

    Area Detector Components:
    ├── Camera (cam)          # Detector control
    ├── Plugins/              # Image processing
    │   ├── image             # Live image display
    │   ├── stats             # Statistics calculation
    │   ├── roi               # Region of interest
    │   ├── transform         # Image transforms
    │   └── hdf5              # File saving
    └── Configuration         # BITS integration

**BITS provides three approaches:**

1. **apstools Factory** (Recommended) - Automatic plugin setup
2. **Version-Compatible Classes** - Handle EPICS version differences
3. **Custom Detector Classes** - Full customization

Using apstools Area Detector Factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Automatic Detector Creation:**

.. code-block:: python

    # devices/detectors.py - Factory approach
    from apstools.devices import ad_creator

    # Create simulation detector with standard plugins
    adsim = ad_creator(
        "IOC:ADSIM:",
        name="adsim",
        detector_class="SimDetectorCam",
        plugins=["image", "stats1", "roi", "hdf1"]  # Note: Use numbered convention (hdf1, stats1)
    )

    # Advanced factory configuration
    advanced_detector = ad_creator(
        "IOC:DETECTOR:",
        name="advanced_det",
        detector_class="SimDetectorCam",  # Use SimDetectorCam for development
        plugins=["image", "stats1", "roi", "hdf1"]  # Note: Use numbered convention
    )

.. note::
   For production detectors, replace ``SimDetectorCam`` with actual detector
   camera classes like ``PilatusDetectorCam``, ``PerkinElmerDetectorCam``, etc.

**Factory Benefits:**
- **Automatic plugin configuration**: No need to manually set up plugin chains
- **Proper port connections**: Data flows correctly between camera and plugins  
- **Standard naming conventions**: Uses established patterns (stats1, hdf1, etc.)
- **Built-in error handling**: Factory validates configuration before creation
- **Immediate functionality**: Creates working detectors that can acquire data

.. note::
   The numbered plugin convention (hdf1, stats1, etc.) allows for multiple
   plugins of the same type. For example, you could have hdf1 for raw data
   and hdf2 for processed data, or stats1 from camera and stats2 from ROI.

Version Compatibility Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Handling EPICS Area Detector Version Changes:**

.. code-block:: python

    # devices/area_detector.py - Version compatibility pattern
    from apstools.devices import CamMixin_V34
    from ophyd.areadetector import CamBase
    from ophyd.areadetector.cam import SimDetectorCam

    class CamUpdates_V34(CamMixin_V34, CamBase):
        """Updates to CamBase for Area Detector 3.4+"""

        # PVs removed in AD 3.4
        pool_max_buffers = None

        # Add any beamline-specific PVs here
        # custom_readout_mode = Cpt(EpicsSignal, ":CustomMode")

    class BeamlineSimDetectorCam_V34(CamUpdates_V34, SimDetectorCam):
        """Simulation detector optimized for this beamline and AD 3.4+"""

        # Use stage_sigs for staging configuration instead of overriding stage()
        stage_sigs = {
            "cam.acquire_time": 0.1,
            "cam.num_images": 1,
            "cam.image_mode": "Single"
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Configure simulation parameters
            self.acquire_time.limits = (0.001, 60.0)  # seconds
            self.num_images.limits = (1, 10000)

.. note::
   For production detectors, substitute ``SimDetectorCam`` with actual detector
   camera classes like ``PilatusDetectorCam``, ``FastCCDDetectorCam``, etc.

**Multi-Version Support:**

.. code-block:: python

    # devices/detector_versions.py - Handle multiple EPICS versions
    import logging
    from pkg_resources import parse_version

    logger = logging.getLogger(__name__)

    def get_area_detector_version():
        """Detect installed Area Detector version."""
        try:
            import ophyd.areadetector
            # Check for version-specific features
            if hasattr(ophyd.areadetector.CamBase, 'pool_max_buffers'):
                return "3.3"
            else:
                return "3.4+"
        except Exception:
            return "unknown"

    # Create appropriate detector class
    AD_VERSION = get_area_detector_version()

    if AD_VERSION == "3.4+":
        from .area_detector import BeamlineSimDetectorCam_V34 as SimDetector
    else:
        from ophyd.areadetector import SimDetector

    logger.info(f"Using Area Detector version: {AD_VERSION}")

.. note::
   This pattern works for any detector type. Replace ``SimDetector`` with
   ``PilatusDetector``, ``FastCCDDetector``, etc. for production systems.

Common Detector Patterns
~~~~~~~~~~~~~~~~~~~~~~~~

**Simulation Detector Pattern:**

.. code-block:: python

    # devices/adsim.py - ADSimDetector setup for development/testing
    from apstools.devices import CamMixin_V34
    from ophyd.areadetector import SimDetector
    from ophyd.areadetector.plugins import ImagePlugin_V34, StatsPlugin_V34
    from ophyd import Component as Cpt

    class ProductionSimDetector(SimDetector):
        """Production-ready simulation detector with optimized plugins."""

        # Use version-compatible plugins (remove leading colons from PV suffixes)
        image = Cpt(ImagePlugin_V34, "image1:")
        stats1 = Cpt(StatsPlugin_V34, "Stats1:")  # Stats1 receives from camera
        stats2 = Cpt(StatsPlugin_V34, "Stats2:")  # Stats2 can receive from ROI

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Configure for realistic simulation
            self.cam.acquire_period.put(0.005)  # 5ms overhead
            self.stats1.kind = "hinted"  # Show in plots

        def collect_dark_images(self, num_images=10):
            """Simulate dark image collection for background subtraction."""
            # Simulate dark collection process
            original_num = self.cam.num_images.get()
            self.cam.num_images.put(num_images)
            self.cam.image_mode.put("Multiple")
            # Implementation continues...

.. note::
   This pattern applies to any detector type. For production systems, replace
   ``SimDetector`` with ``PilatusDetector``, ``PerkinElmerDetector``, etc.

**Fast CCD Pattern:**

.. code-block:: python

    # devices/fastccd.py - Fast CCD configuration
    from ophyd.areadetector import DetectorBase
    from ophyd.areadetector.cam import FastCCDDetectorCam
    from ophyd.areadetector.plugins import HDF5Plugin_V34
    from ophyd import Component as Cpt

    class FastCCDDetector(DetectorBase):
        """Fast CCD detector with HDF5 file writing."""

        cam = Cpt(FastCCDDetectorCam, "cam1:")
        # HDF5 plugin needs comprehensive setup (see 12ID repository for complete example)
        hdf1 = Cpt(HDF5Plugin_V34, "HDF1:",
                   write_path_template="/data/%Y/%m/%d/",
                   # Additional HDF5 configuration required for functionality
                   # - file_path, file_name, file_template must be set
                   # - capture mode and array callbacks need configuration
                   )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Fast CCD specific configuration
            self.cam.fccd_fw_enable.put(1)  # Enable firmware processing
            self.cam.fccd_sw_enable.put(1)  # Enable software processing
            
            # HDF5 requires additional setup beyond basic Component definition
            # See 12ID repository for complete HDF5 configuration example:
            # - file_path, file_name, file_template must be configured
            # - capture mode and callbacks need proper setup
            # - array port connections must be established

**Area Detector with Custom Processing:**

.. code-block:: python

    # devices/processing_detector.py - Working detector with image processing
    # This example creates a functional detector with ROI and processing capabilities
    from ophyd.areadetector import DetectorBase
    from ophyd.areadetector.plugins import ProcessPlugin_V34, ROIPlugin_V34, StatsPlugin_V34
    from ophyd.areadetector.cam import SimDetectorCam
    from ophyd import Component as Cpt

    class ProcessingDetector(DetectorBase):
        """Working detector with real-time image processing and statistics."""

        # Camera component required for functional detector
        cam = Cpt(SimDetectorCam, "cam1:")

        # Multiple ROIs for different sample regions (remove leading colons)
        roi1 = Cpt(ROIPlugin_V34, "ROI1:", kind="hinted")
        roi2 = Cpt(ROIPlugin_V34, "ROI2:", kind="hinted")
        roi3 = Cpt(ROIPlugin_V34, "ROI3:", kind="hinted")

        # Image processing
        proc1 = Cpt(ProcessPlugin_V34, "Proc1:")
        
        # Statistics plugins that receive from ROI plugins (proper data flow)
        roi1_stats = Cpt(StatsPlugin_V34, "Stats3:")  # Stats3 gets input from ROI1
        roi2_stats = Cpt(StatsPlugin_V34, "Stats4:")  # Stats4 gets input from ROI2

        def setup_rois(self, sample_positions):
            """Configure ROIs for different sample positions."""
            for i, (roi, pos) in enumerate(zip([self.roi1, self.roi2, self.roi3],
                                               sample_positions)):
                roi.min_x.put(pos['x'] - pos['width']//2)
                roi.min_y.put(pos['y'] - pos['height']//2)
                roi.size_x.put(pos['width'])
                roi.size_y.put(pos['height'])

Plugin Configuration Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File Writing Plugins:**

.. code-block:: python

    # devices/file_writers.py - Advanced file writing
    from ophyd.areadetector.plugins import HDF5Plugin_V34, TIFFPlugin_V34
    from ophyd import Component as Cpt
    from pathlib import Path
    import datetime

    class MultiFormatDetector(DetectorBase):
        """Working detector that saves in multiple formats.
        
        This example provides practical file writing configuration
        based on established beamline patterns.
        """

        # Camera required for functional detector
        cam = Cpt(SimDetectorCam, "cam1:")
        
        # File writing plugins (numbered convention allows multiple plugins)
        hdf1 = Cpt(HDF5Plugin_V34, "HDF1:")  # Primary HDF5 writer
        tiff1 = Cpt(TIFFPlugin_V34, "TIFF1:")  # Quick preview writer
        
        # Stats plugin for monitoring
        stats1 = Cpt(StatsPlugin_V34, "Stats1:")

        def configure_file_writing(self, experiment_name, sample_name):
            """Configure file paths and names."""

            # Create date-based directory structure
            today = datetime.datetime.now()
            data_path = Path(f"/data/{today.year:04d}/{today.month:02d}/{today.day:02d}")

            # HDF5 for analysis (using hdf1 naming convention)
            hdf5_path = data_path / "hdf5"
            self.hdf1.file_path.put(str(hdf5_path))
            self.hdf1.file_name.put(f"{experiment_name}_{sample_name}")
            self.hdf1.file_template.put("%s%s_%06d.h5")

            # TIFF for quick review (using tiff1 naming convention)
            tiff_path = data_path / "tiff"
            self.tiff1.file_path.put(str(tiff_path))
            self.tiff1.file_name.put(f"{experiment_name}_{sample_name}")

**Statistics and ROI Plugins:**

.. code-block:: python

    # devices/analysis_plugins.py - Real-time analysis
    from ophyd.areadetector.plugins import StatsPlugin_V34, ROIPlugin_V34
    from ophyd import Component as Cpt, Signal

    class AnalysisDetector(DetectorBase):
        """Detector with real-time analysis capabilities."""

        # Primary statistics (remove leading colon - PV naming convention)
        stats1 = Cpt(StatsPlugin_V34, "Stats1:")

        # ROI-based statistics (remove leading colons)
        roi1 = Cpt(ROIPlugin_V34, "ROI1:", kind="hinted")
        roi_stats1 = Cpt(StatsPlugin_V34, "Stats2:")  # Stats2 receives from ROI1 plugin

        # Peak finding
        peak_x = Cpt(Signal, value=0, kind="hinted")
        peak_y = Cpt(Signal, value=0, kind="hinted")
        peak_intensity = Cpt(Signal, value=0, kind="hinted")

        def find_beam_center(self):
            """Find beam center using centroid calculation."""
            centroid_x = self.stats1.centroid_x.get()
            centroid_y = self.stats1.centroid_y.get()
            max_value = self.stats1.max_value.get()

            # Update peak position signals
            self.peak_x.put(centroid_x)
            self.peak_y.put(centroid_y)
            self.peak_intensity.put(max_value)

            return centroid_x, centroid_y

Configuration Patterns
~~~~~~~~~~~~~~~~~~~~~~

**Basic Configuration:**

.. code-block:: yaml

    # configs/devices.yml - Standard detector configuration
    my_instrument.devices.ProductionSimDetector:
    - name: adsim
      prefix: "IOC:ADSIM:"
      labels: ["detectors", "primary"]

    # apstools factory configuration
    apstools.devices.ad_creator:
    - name: fast_detector
      # Factory arguments
      prefix: "IOC:ADSIM2:"
      detector_class: "SimDetectorCam"  # Use SimDetectorCam for development
      plugins: ["image", "stats1", "hdf1"]  # Use numbered plugin convention
      labels: ["detectors", "fast"]

.. note::
   For production, replace ``SimDetectorCam`` with actual detector classes
   like ``FastCCDDetectorCam``, ``PilatusDetectorCam``, etc.

**Environment-Specific Configuration:**

.. code-block:: yaml

    # configs/devices_aps_only.yml - Production detectors
    my_instrument.devices.ProductionPilatus:  # Replace with actual detector class
    - name: pilatus_real
      prefix: "12IDA:PILATUS:"
      labels: ["detectors", "primary"]
      # Custom initialization
      init_kwargs:
        acquire_time: 0.1
        file_path: "/data/pilatus/"

.. code-block:: yaml

    # configs/devices.yml - Development/simulation
    ophyd.areadetector.SimDetector:
    - name: adsim_dev
      prefix: "SIM:ADSIM:"
      labels: ["detectors", "primary"]
      # Simulation parameters
      init_kwargs:
        noise: true
        image_width: 1024  # Typical detector dimensions
        image_height: 1024

Integration with Plans
~~~~~~~~~~~~~~~~~~~~~

**Detector in Scan Plans:**

.. code-block:: python

    # plans/detector_scans.py - Detector-specific scan plans
    from bluesky.plans import count, scan
    from bluesky import plan_stubs as bps

    def detector_count(detector, *, num=1, delay=0, acquire_time=0.1):
        """Count plan with detector-specific setup.
        
        Parameters passed as keyword arguments for clarity and safety.
        This plan DOES publish Bluesky documents (start, event, stop).
        """

        # Configure detector parameters (passed as plan arguments)
        yield from bps.mv(detector.cam.acquire_time, acquire_time)
        yield from bps.mv(detector.cam.num_images, 1)

        # Execute count with proper document publishing
        yield from count([detector], num=num, delay=delay)

    def detector_series(detector, *, num_images, exposure_time):
        """Collect a series of images.
        
        IMPORTANT: This plan does NOT publish normal Bluesky documents.
        It only triggers and reads - no start/event/stop documents.
        Use detector_count() if you need full document publishing.
        """

        # Configure for series acquisition (parameters as keyword args)
        yield from bps.mv(detector.cam.acquire_time, exposure_time)
        yield from bps.mv(detector.cam.num_images, num_images)
        yield from bps.mv(detector.cam.image_mode, "Multiple")

        # Trigger acquisition - NO document publishing
        yield from bps.trigger_and_read([detector])

**Detector Alignment Plans:**

.. code-block:: python

    # plans/detector_alignment.py - Detector positioning
    from apstools.plans import lineup2
    from bluesky import plan_stubs as bps

    def align_detector_distance(detector, distance_motor, *, nominal_distance, 
                               scan_range=10, num_points=21):
        """Align detector to optimal distance.
        
        Parameters passed as keyword arguments for safety and clarity.
        """

        # Scan around nominal position (parameters as keyword args)
        yield from lineup2(
            [detector.stats1.total],
            distance_motor,
            nominal_distance - scan_range,  # mm
            nominal_distance + scan_range,  # mm
            num_points
        )

Data Management Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Metadata Collection:**

.. code-block:: python

    # devices/detector_metadata.py - Metadata integration
    from ophyd import Device, Component as Cpt, Signal

    class DetectorMetadata(Device):
        """Collect detector metadata for data management.
        
        This metadata gets automatically included in Bluesky documents
        when using kind="config" - essential for data analysis.
        """

        # Detector configuration (automatically saved with each scan)
        exposure_time = Cpt(Signal, kind="config")  # Current exposure setting
        num_images = Cpt(Signal, kind="config")     # Images per acquisition
        detector_distance = Cpt(Signal, kind="config") # Sample-to-detector distance

        # Environmental conditions (for data quality assessment)
        detector_temperature = Cpt(EpicsSignal, ":TEMP:RBV", kind="config")

        # Calibration information (essential for data analysis)
        pixel_size = Cpt(Signal, value=0.172, kind="config")  # mm per pixel
        wavelength = Cpt(Signal, kind="config")  # X-ray wavelength in Angstroms

**File Management:**

.. code-block:: python

    # callbacks/detector_files.py - File management
    from apstools.callbacks import NXWriter
    from pathlib import Path

    class DetectorFileManager:
        """Practical file management for area detectors.
        
        This example shows working file management patterns used
        in production beamlines. Handles directory creation,
        file naming, and metadata integration.
        """

        def __init__(self, detector, base_path="/data"):
            self.detector = detector
            self.base_path = Path(base_path)
            # Validate detector has required file writing capability
            if not hasattr(detector, 'hdf1'):
                raise ValueError(f"Detector {detector.name} lacks hdf1 plugin")

        def setup_scan_files(self, scan_id, sample_name):
            """Configure files for a scan."""

            scan_dir = self.base_path / f"scan_{scan_id:04d}"
            scan_dir.mkdir(exist_ok=True)

            # Configure HDF5 file (using hdf1 naming convention)
            self.detector.hdf1.file_path.put(str(scan_dir))
            self.detector.hdf1.file_name.put(f"{sample_name}")

            # Setup NeXus writer
            nx_writer = NXWriter(str(scan_dir / f"{sample_name}.nx.hdf5"))
            return nx_writer

Troubleshooting Area Detectors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common Issues and Practical Solutions:**

1. **Plugin Connection Errors** (Most common cause of non-functional detectors):

   .. code-block:: bash

       # Check plugin connections - data flow must be correct
       caget IOC:ADSIM:cam1:ArrayPort      # Should show "DET"
       caget IOC:ADSIM:image1:NDArrayPort  # Should show "DET"
       caget IOC:ADSIM:Stats1:NDArrayPort  # Should show "DET" or "ROI1"

       # Verify plugin enable status - plugins must be enabled
       caget IOC:ADSIM:image1:EnableCallbacks  # Should be 1
       caget IOC:ADSIM:Stats1:EnableCallbacks  # Should be 1

2. **HDF5 File Writing Problems** (HDF5 needs more than default setup):

   .. code-block:: python

       # Check complete HDF5 configuration (using hdf1 convention)
       print(f"File path: {detector.hdf1.file_path.get()}")
       print(f"File name: {detector.hdf1.file_name.get()}")
       print(f"File template: {detector.hdf1.file_template.get()}")
       print(f"Write mode: {detector.hdf1.file_write_mode.get()}")
       print(f"Capture status: {detector.hdf1.capture.get()}")
       print(f"Array port: {detector.hdf1.nd_array_port.get()}")  # Must match source
       
       # HDF5 plugin often needs explicit configuration:
       # detector.hdf1.file_path.put("/data/experiment/")
       # detector.hdf1.file_name.put("sample_001")
       # detector.hdf1.file_template.put("%s%s_%06d.h5")

3. **Memory and Buffer Issues:**

   .. code-block:: bash

       # Check memory pools
       caget IOC:ADSIM:cam1:PoolMaxBuffers
       caget IOC:ADSIM:cam1:PoolUsedBuffers

**Diagnostic Tools:**

.. code-block:: python

    # devices/detector_diagnostics.py - Diagnostic utilities
    def diagnose_detector(detector):
        """Run comprehensive detector diagnostics."""

        print(f"Detector: {detector.name}")
        print(f"Connection: {detector.connected}")
        print(f"Acquire state: {detector.cam.acquire.get()}")
        print(f"Array size: {detector.cam.array_size.get()}")

        # Check plugins (using numbered convention)
        for plugin_name in ['image', 'stats1', 'hdf1']:
            if hasattr(detector, plugin_name):
                plugin = getattr(detector, plugin_name)
                print(f"{plugin_name}: enabled={plugin.enable.get()}")

AI Integration Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~

**bAIt Analysis Patterns:**

.. code-block:: python

    # AI rules for area detector validation
    def analyze_detector_config(detector_config):
        """bAIt rules for detector analysis."""

        validation_rules = {
            "version_compatibility": "Check for apstools mixins",
            "plugin_connections": "Verify proper port connections",
            "file_paths": "Ensure writable file paths",
            "memory_configuration": "Check buffer pool settings",
            "performance_optimization": "Validate acquisition settings"
        }

        return validate_detector_rules(detector_config, validation_rules)

Best Practices Summary
~~~~~~~~~~~~~~~~~~~~~~

**DO:**
- **Use apstools factory** for standard detectors - creates working detectors immediately
- **Follow numbered plugin conventions** (hdf1, stats1) - allows multiple plugins
- **Remove leading colons** from PV suffixes - correct EPICS naming
- **Configure HDF5 completely** - file_path, file_name, file_template required
- **Connect stats to ROI plugins** - proper data flow for analysis
- **Test with simulation first** - verify patterns before production hardware
- **Pass plan parameters as kwargs** - safer and clearer than positional args
- **Document Bluesky publishing differences** - critical for data collection

**DON'T:**
- Use "hdf5" or "stats" without numbers - breaks convention
- Include leading colons in plugin PV suffixes - incorrect naming
- Create examples that don't produce working detectors - no practical value
- Skip HDF5 detailed configuration - plugin won't function properly
- Connect stats plugins directly to camera when ROI analysis needed
- Assume all plans publish documents - some only trigger/read
- Hardcode parameters in plans - use kwargs for flexibility

**Validation Checklist:**

Before moving to production, verify your detector setup:

.. code-block:: python

    # Test detector functionality
    print(f"Connected: {detector.connected}")
    print(f"Plugins enabled: {detector.hdf1.enable.get()}")
    print(f"File path set: {detector.hdf1.file_path.get()}")
    
    # Test acquisition
    detector.stage()  # Should not raise exceptions
    detector.unstage()
    
    # Test with Bluesky
    RE(count([detector]))  # Should complete successfully

**Next Steps:**

1. :doc:`Create detector-specific scan plans <creating_plans>`
2. :doc:`Integrate with data management workflows <dm>`  
3. :doc:`Set up queue server for detector operations <qserver>`
4. **Reference 12ID repository** for complete HDF5 configuration examples
