.. _area_detectors:

Area Detector Configuration Patterns
=====================================

This guide covers area detector setup in BITS, from simple configurations to advanced patterns using apstools factories and version compatibility.

Quick Start: Basic Area Detector
---------------------------------

**Set up an ADSimDetector in 3 steps:**

.. code-block:: python

    # 1. devices/detectors.py - Basic simulation detector
    from ophyd.areadetector import SimDetector

    class MySimDetector(SimDetector):
        """Basic simulation detector for development and testing."""
        pass

.. code-block:: yaml

    # 2. configs/devices.yml
    my_instrument.devices.MySimDetector:
    - name: adsim
      prefix: "IOC:ADSIM:"
      labels: ["detectors", "primary"]

.. code-block:: python

    # 3. Test detector
    from my_instrument.startup import *
    RE(count([adsim]))

.. note::
   ADSimDetector is available in containerized environments and provides
   realistic detector behavior for development. For production, substitute with
   actual detector classes like PilatusDetector, PerkinElmerDetector, etc.

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
        plugins=["image", "stats", "roi", "hdf5"]
    )

    # Advanced factory configuration
    advanced_detector = ad_creator(
        "IOC:DETECTOR:",
        name="advanced_det",
        detector_class="SimDetectorCam",  # Use SimDetectorCam for development
        plugins=["image", "stats", "roi", "hdf5"]
    )

.. note::
   For production detectors, replace ``SimDetectorCam`` with actual detector
   camera classes like ``PilatusDetectorCam``, ``PerkinElmerDetectorCam``, etc.

**Factory Benefits:**
- Automatic plugin configuration
- Proper port connections
- Standard naming conventions
- Built-in error handling

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

        # Use version-compatible plugins
        image = Cpt(ImagePlugin_V34, ":image1:")
        stats1 = Cpt(StatsPlugin_V34, ":Stats1:")
        stats2 = Cpt(StatsPlugin_V34, ":Stats2:")

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

        cam = Cpt(FastCCDDetectorCam, ":cam1:")
        hdf5 = Cpt(HDF5Plugin_V34, ":HDF1:",
                   write_path_template="/data/%Y/%m/%d/")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Fast CCD specific configuration
            self.cam.fccd_fw_enable.put(1)  # Enable firmware
            self.cam.fccd_sw_enable.put(1)  # Enable software

**Area Detector with Custom Processing:**

.. code-block:: python

    # devices/processing_detector.py - Custom image processing
    from ophyd.areadetector import DetectorBase
    from ophyd.areadetector.plugins import ProcessPlugin_V34, ROIPlugin_V34
    from ophyd import Component as Cpt

    class ProcessingDetector(DetectorBase):
        """Detector with real-time image processing."""

        # Multiple ROIs for different sample regions
        roi1 = Cpt(ROIPlugin_V34, ":ROI1:", kind="hinted")
        roi2 = Cpt(ROIPlugin_V34, ":ROI2:", kind="hinted")
        roi3 = Cpt(ROIPlugin_V34, ":ROI3:", kind="hinted")

        # Image processing
        proc1 = Cpt(ProcessPlugin_V34, ":Proc1:")

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
        """Detector that saves in multiple formats."""

        hdf5 = Cpt(HDF5Plugin_V34, ":HDF1:")
        tiff = Cpt(TIFFPlugin_V34, ":TIFF1:")

        def configure_file_writing(self, experiment_name, sample_name):
            """Configure file paths and names."""

            # Create date-based directory structure
            today = datetime.datetime.now()
            data_path = Path(f"/data/{today.year:04d}/{today.month:02d}/{today.day:02d}")

            # HDF5 for analysis
            hdf5_path = data_path / "hdf5"
            self.hdf5.file_path.put(str(hdf5_path))
            self.hdf5.file_name.put(f"{experiment_name}_{sample_name}")
            self.hdf5.file_template.put("%s%s_%06d.h5")

            # TIFF for quick review
            tiff_path = data_path / "tiff"
            self.tiff.file_path.put(str(tiff_path))
            self.tiff.file_name.put(f"{experiment_name}_{sample_name}")

**Statistics and ROI Plugins:**

.. code-block:: python

    # devices/analysis_plugins.py - Real-time analysis
    from ophyd.areadetector.plugins import StatsPlugin_V34, ROIPlugin_V34
    from ophyd import Component as Cpt, Signal

    class AnalysisDetector(DetectorBase):
        """Detector with real-time analysis capabilities."""

        # Primary statistics
        stats1 = Cpt(StatsPlugin_V34, ":Stats1:")

        # ROI-based statistics
        roi1 = Cpt(ROIPlugin_V34, ":ROI1:", kind="hinted")
        roi_stats1 = Cpt(StatsPlugin_V34, ":Stats2:")  # Stats on ROI1

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
      plugins: ["image", "stats", "hdf5"]
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

    def detector_count(detector, num=1, delay=0):
        """Count plan with detector-specific setup."""

        # Configure detector
        yield from bps.mv(detector.cam.acquire_time, 0.1)
        yield from bps.mv(detector.cam.num_images, 1)

        # Execute count
        yield from count([detector], num=num, delay=delay)

    def detector_series(detector, num_images, exposure_time):
        """Collect a series of images."""

        # Configure for series acquisition
        yield from bps.mv(detector.cam.acquire_time, exposure_time)
        yield from bps.mv(detector.cam.num_images, num_images)
        yield from bps.mv(detector.cam.image_mode, "Multiple")

        # Trigger acquisition
        yield from bps.trigger_and_read([detector])

**Detector Alignment Plans:**

.. code-block:: python

    # plans/detector_alignment.py - Detector positioning
    from apstools.plans import lineup2
    from bluesky import plan_stubs as bps

    def align_detector_distance(detector, distance_motor, nominal_distance):
        """Align detector to optimal distance."""

        # Scan around nominal position
        yield from lineup2(
            [detector.stats1.total],
            distance_motor,
            nominal_distance - 10,  # mm
            nominal_distance + 10,  # mm
            21
        )

Data Management Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Metadata Collection:**

.. code-block:: python

    # devices/detector_metadata.py - Metadata integration
    from ophyd import Device, Component as Cpt, Signal

    class DetectorMetadata(Device):
        """Collect detector metadata for data management."""

        # Detector configuration
        exposure_time = Cpt(Signal, kind="config")
        num_images = Cpt(Signal, kind="config")
        detector_distance = Cpt(Signal, kind="config")

        # Environmental conditions
        detector_temperature = Cpt(EpicsSignal, ":TEMP:RBV", kind="config")

        # Calibration information
        pixel_size = Cpt(Signal, value=0.172, kind="config")  # mm
        wavelength = Cpt(Signal, kind="config")  # Angstroms

**File Management:**

.. code-block:: python

    # callbacks/detector_files.py - File management
    from apstools.callbacks import NXWriter
    from pathlib import Path

    class DetectorFileManager:
        """Manage detector files and metadata."""

        def __init__(self, detector, base_path="/data"):
            self.detector = detector
            self.base_path = Path(base_path)

        def setup_scan_files(self, scan_id, sample_name):
            """Configure files for a scan."""

            scan_dir = self.base_path / f"scan_{scan_id:04d}"
            scan_dir.mkdir(exist_ok=True)

            # Configure HDF5 file
            self.detector.hdf5.file_path.put(str(scan_dir))
            self.detector.hdf5.file_name.put(f"{sample_name}")

            # Setup NeXus writer
            nx_writer = NXWriter(str(scan_dir / f"{sample_name}.nx.hdf5"))
            return nx_writer

Troubleshooting Area Detectors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common Issues:**

1. **Plugin Connection Errors:**

   .. code-block:: bash

       # Check plugin connections
       caget IOC:ADSIM:cam1:ArrayPort
       caget IOC:ADSIM:image1:NDArrayPort

       # Verify plugin enable status
       caget IOC:ADSIM:image1:EnableCallbacks

2. **File Writing Problems:**

   .. code-block:: python

       # Check file writing configuration
       detector.hdf5.file_path.get()
       detector.hdf5.file_write_mode.get()
       detector.hdf5.capture.get()

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

        # Check plugins
        for plugin_name in ['image', 'stats1', 'hdf5']:
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
- Use apstools factory for standard detectors
- Handle version compatibility with mixins
- Configure appropriate plugin chains
- Test detector operations without beam
- Include metadata collection for data management

**DON'T:**
- Create custom detectors when apstools factory works
- Hardcode file paths in detector classes
- Skip plugin connection validation
- Ignore memory and buffer configuration
- Forget to handle EPICS version differences

**Next Steps:**

1. :doc:`Create detector-specific scan plans <creating_plans>`
2. :doc:`Integrate with data management workflows <dm>`
3. :doc:`Set up queue server for detector operations <qserver>`
4. :doc:`Deploy production detector systems <deployment_patterns>`
