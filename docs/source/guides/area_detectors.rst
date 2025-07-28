.. _area_detectors:

Area Detector Configuration Patterns
=====================================

This guide covers area detector setup in BITS, from simple
configurations to advanced patterns using apstools factories and version
compatibility.

Quick Start: Basic Area Detector
---------------------------------

**YAML-First Approach (Recommended):**

Start with YAML configuration - easier and more maintainable.  Here we
show the specification of a Python object that will be created when the
session is started.

This area detector object provide controls for the camera (the ``cam``
plugin) and support to view the acquired image(s) (the ``image`` plugin).

.. code-block:: yaml
    :linenos:

    # 1. configs/devices.yml - Use apstools factory directly
    apstools.devices.ad_creator:
    - name: adsim
      prefix: "IOC:ADSIM:"  # EPICS PV prefix for this area detector instance.
      plugins:
      - cam  # The cam gets the image from the hardware.
          # In this case (ADSimDetector), the hardware is an EPICS simulation.
          class: "apstools.devices.SimDetectorCam_V34"
      - image  # no additional dictionary means to use default configuration from apstools
      labels: ["detectors"]

For an explanation of these terms used by ``ad_creator``, see the
:ref:`explanation <area_detector.ad_creator.explanation>` below.

Next, we show some Python code that demonstrates this object:

.. code-block:: python
    :linenos:

    # 2. Test immediately - this creates the 'adsim' detector object.
    from my_instrument.startup import *

    # Verify detector is functional.
    print(f"Detector: {adsim.name}, Connected: {adsim.connected}")

    # Test acquisition.
    RE(count([adsim]))

**Alternative Python Approach:**

These are the Python steps that duplicate the YAML specification above.  First,
create a Python file in the `devices/` directory:

.. code-block:: python
    :linenos:

    from apstools.devices import ad_creator

    # Create functional detector with Python code.
    adsim = ad_creator(
        prefix="IOC:ADSIM:",
        name="adsim",
        plugins=[
            {"name": "cam", "class": "apstools.devices.SimDetectorCam_V34"},
            "image",
        ]
        labels=["detectors"]
    )

The Python code to test this object is different, with one additional command line:

.. code-block:: python
    :linenos:

    # 2. Test immediately - this creates the 'adsim' detector object.
    from my_instrument.startup import *

    # Get the 'adsim' detector object from the ophyd object registry.
    adsim = oregistry["adsim"]

    # Verify detector is functional
    print(f"Detector: {adsim.name}, Connected: {adsim.connected}")

    # Test acquisition
    RE(count([adsim]))


.. important::
   **Why SimDetectorCam for Tutorials?** ADSimDetector simulates the hardware
   of an area detector.  It can be available in many environments such as
   containers.  It does not require any detector hardware. ADSimDetector
   provides realistic detector behavior without requiring specialized
   hardware. This makes it easy for anyone to duplicate this tutorial.

   **Production Transition:** To use real detectors, simply change:

   - Replace ``prefix: "IOC:ADSIM:"`` with actual IOC prefix
       (such as ``"S12-PILATUS1:"``).
   - In ``cam``, replace ``class: "apstools.devices.SimDetectorCam_V34"``
       with appropriate class (such as ``"ophyd.areadetector.PilatusDetectorCam"``).
   - Add additional plugins as necessary.
   - Test with your actual IOC running.

   All plugin configurations and patterns remain identical.

Complete Area Detector Guide
-----------------------------

Understanding Area Detector Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Area detectors in BITS follow the EPICS Area Detector architecture:

.. code-block:: text

    Area Detector Components:
    │   name                  # Name of the ophyd object (to create).
    │   prefix                # EPICS PV prefix for the area detector support.  Use quotes.  Always include trailing ":".
    ├── Plugins/              # Image processing
    │   ├── cam               # Operate camera features and receive image(s) from hardware.
    │   ├── hdf1              # Save image(s) to HDF5 files.  In ophyd, the plugin is named 'hdf1'.
    │   ├── image             # Live image display (EPICS CA interface)
    │   ├── pva               # Live image display (EPICS PVA interface)
    │   ├── roi1              # Select region of interest from image.
    │   ├── stat1             # Statistics calculation (could receive image array from roi1)
    │   ├── transform1        # Transform image array.
    │   └── other plugins     # as configured in EPICS
    └── labels                # (optional) List of ophyd object labels.

* All plugins are optional.  Usually, at least the cam and image plugins are
  needed for meaningful control and imaging.

**BITS provides three approaches:**

1. **apstools Factory** (Recommended) - Automatic plugin setup
2. **Version-Compatible Classes** - Handle EPICS version differences
3. **Custom Detector Classes** - Full customization

Using apstools Area Detector Factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Automatic Detector Creation:**

Create ``adsim`` with support for viewing images with EPICS
CA & PVA protocols.  No file saving or image processing.

.. code-block:: yaml
    :linenos:

    apstools.devices.ad_creator:
    - name: adsim
      prefix: "IOC:ADSIM:"
      plugins:
      - cam
          class: "apstools.devices.SimDetectorCam_V34"
      - image
      - pva
      labels: ["detectors"]

Create ``adsim2`` with additional support for computing statistics on a
selected region of interest and saving image(s) to HDF5 files where the
file name is specified in EPICS.

.. code-block:: yaml
    :linenos:

    apstools.devices.ad_creator:
    - name: adsim2
      prefix: "IOC:ADSIM:"
      plugins:
      - cam
          class: "apstools.devices.SimDetectorCam_V34"
      - image
      - pva
      - roi1
      - stats1
      - hdf1:
          class: "apstools.devices.area_detector_support.AD_EpicsFileNameHDF5Plugin"
          # Path templates MUST end with a trailing `/`.
          read_path_template: "/gdata/dm/TEST/2025-2/"
          write_path_template: "/gdata/dm/TEST/2025-2/"
          kind: normal
      labels: ["detectors"]

**Factory Benefits:**
- **Automatic plugin configuration**: No need to manually set up plugin chains
- **Proper port connections**: Data flows correctly between camera and plugins
- **Standard naming conventions**: Uses established patterns (stats1, hdf1, etc.)
- **Built-in error handling**: Factory validates configuration before creation
- **Immediate functionality**: Creates working detectors that can acquire data

.. note::
   The numbered plugin convention (hdf1, stats1, etc.) allows for multiple
   plugins of the same type. For example, you could have roi1 & roi2 for
   two different regions of interest.

See :ref:`area_detector.ad_creator.explanation` for more details.

Version Compatibility Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Handling EPICS Area Detector Version Changes:**

When building an area detector, it may be necessary to query the EPICS
support to learn what features are supported by a specific area
detector.  This can be learned by requesting the area detector core
release version from a PV.

.. code-block:: python

    # devices/detector_versions.py - Handle multiple EPICS versions
    from pkg_resources import parse_version
    from ophyd import EpicsSignalRO

    def get_area_detector_version(prefix):
        """Detect Area Detector release version from EPICS."""
        pv = f"{prefix}cam1:ADCoreVersion_RBV"
        signal = EpicsSignalRO(pv, name="signal")
        signal.wait_for_connection(timeout=1)
        return signal.get()

    # Create appropriate detector cam class
    AD_VERSION = get_area_detector_version("IOC:ADSIM:")

    # Choose cam class based on AD core release
    if parse_version("3.4.0") < parse_version(AD_VERSION):
        from ophyd.areadetector import SimDetectorCam
    else:
        from apstools.devices import SimDetectorCam_V34 as SimDetectorCam

    print(SimDetectorCam)
    # Either <class 'ophyd.areadetector.cam.SimDetectorCam'>
    # or <class 'apstools.devices.area_detector_support.SimDetectorCam_V34'>

.. note::
   This pattern works for any detector type. Replace ``SimDetector`` with
   ``PilatusDetector``, ``FastCCDDetector``, etc. for production systems.

Integration with Plans
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Detector in Scan Plans:**

Here are two examples of bluesky plans that operate an area detector.

===============  ===========  ===================================================
bluesky plan     creates run  Operates detector with ...
===============  ===========  ===================================================
detector_count   yes          user-specified acquire time (and other parameters).
detector_series  no           user-specified acquire time (and other parameters).
===============  ===========  ===================================================

.. code-block:: python

    # plans/detector_scans.py - Detector-specific scan plans
    from bluesky.plans import count, scan
    from bluesky.utils import plan
    from bluesky import plan_stubs as bps

    @plan
    def detector_count(detector, *, num=1, num_frames=1, delay=0, acquire_time=0.1):
        """Count plan with detector-specific setup.

        This bluesky plan creates a new bluesky run.

        PARAMETERS

        delay float:
            Time (s) to wait between image acquisitions (default: 0.0)
        acquire_time float:
            Exposure time (s) per frame (default: 0.1)
        num int:
            number of image acquisitions (default: 1)
        num_frames int:
            number of frames per image acquisition (default: 1)
        """

        # Configure detector parameters (passed as plan arguments)
        yield from bps.mv(detector.cam.acquire_time, acquire_time)
        yield from bps.mv(detector.cam.num_images, num_frames)

        # Execute count with proper document publishing
        yield from count([detector], num=num, delay=delay)

    @plan
    def detector_series(detector, *, num_frames=1, acquire_time=0.1):
        """Collect a series of images.

        This bluesky plan DOES NOT create a new bluesky run.
        It only operates the detector. Use 'detector_count()' if you
        need full document publishing.

        PARAMETERS

        acquire_time float:
            Exposure time (s) per frame (default: 0.1)
        num_frames int:
            number of frames per image acquisition (default: 1)
        """

        # Configure for series acquisition (parameters as keyword args)
        prior_mode = detector.cam.image_mode.get()
        yield from bps.mv(detector.cam.acquire_time, acquire_time)
        yield from bps.mv(detector.cam.num_images, num_frames)
        yield from bps.mv(detector.cam.image_mode, "Multiple")

        # Trigger acquisition - NO bluesky run (NO document publishing)
        yield from bps.trigger_and_read([detector])
        yield from bps.mv(detector.cam.image_mode, prior_mode)

.. tip:: A bluesky plan that does not create a bluesky run is referred to as a *plan stub*.

**Detector Alignment Plan:**

.. code-block:: python

    # plans/detector_alignment.py - Detector positioning
    from apstools.plans import lineup2
    from bluesky import plan_stubs as bps

    def align_detector_distance(detector, positioner, *, reference_position,
                               scan_range=10, num_points=21):
        """Align positioner to area detector centroid."""

        # Ensure that the signal will be reported by the bluesky EunEngine.
        detector.stats1.kind = "hinted"
        detector.stats1.total.kind = "hinted"

        # Scan around nominal position (parameters as keyword args)
        yield from lineup2(
            [detector.stats1.total],
            positioner,
            reference_position - scan_range/2,
            reference_position + scan_range/2,
            num_points
        )

.. _area_detector.ad_creator.explanation:

ad_creator YAML Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

YAML specifications for area detector objects using ``ad_creator`` rely
on these terms.

* ``apstools.devices.ad_creator``: The Python callable (a class or function)
    that will be used to create the object.  All keyword arguments (kwargs) of this
    callable are specified as shown below.  It is not necessary to specify
    any kwargs that have the default value.

* ``- name: adsim``: The name of the Python object to be created.Must

    .. important:: The ``name`` *must* be unique amongst *all* Python
        object names to be created.

* ``prefix: "IOC:ADSIM:"``: The EPICS PV prefix.  Most callables call this
    ``prefix``. Verify with the callable source or documentation as necessary.

* ``plugins:``: Plugins configure how this area detector object interfaces
    with EPICS.  The ``ad_creator`` has standard names and defaults for many
    plugins.  If all the defaults are acceptable, it is not necessary to
    provide a kwargs dictionary.

    * ``cam``: This "plugin" is the interface with the hardware.  In area
        detector, it is the source of the image array.  This plugin provides
        the image array to other plugins.

        There is no default value for ``class``.  *It is always necessary to
        provide this kwarg.*  The value is text name of the camera class.
        This class will be imported by ``ad_creator``.  Alternatively,
        the Python reference to a camera class could be provided.

        For production detectors, use the class appropriate to your hardware,
        such as ``"ophyd.areadetector.PilatusDetectorCam"`` for a Pilatus
        area detector.

    * ``image``: This "plugin" receives the image array and makes it available
        (by EPICS Channel Access protocol, CA) from EPICS PVs.

    * ``pva``: This "plugin" receives the image array and makes it available
        (by EPICS PV Access protocol, PVA) from EPICS PVs.

        .. Further description of CA and PVA is out of scope here.
           Consult the EPICS area detector documentation for full details.

* ``labels: "IOC:ADSIM:"``: The EPICS PV prefix.  Most callables call this
    ``prefix``. Verify with the callable source or documentation as necessary.

For full description of the available plugins and their
configuration using ``ad_creator``, including how to modify or
describe additional plugins, consult the documentation in apstools.

.. comment-out for now
    Troubleshooting Area Detectors
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Common Issues and Practical Solutions:**

    1. **Connection Errors**:

    Various root causes are possible:

    * IOC not running
    * Wrong PV prefix
    * Wrong PV name(s)
    * IOC does not provide expected plugin
    * Wrong asyn PORT name

    .. TODO: show example of each error and how to fix

    2. **HDF5/JPEG/TIFF File Writing Problems** (always needs more than default setup):

    We'll show with the HDF5 File Plugin but similar instructions
    apply to the other file writers.

    * file writer mode Wrong
    * file path does not exist
    * auto save and related parameters
    * plugin not enabled

    .. TODO: show example of each error and how to fix

    3. Problems with the `hdf1` plugin and the `Capture_RBV` PV.
    .. TODO: Show the error message, show how to fix.

       hint: Plugin needs to be *primed*.  Show how with apstools.

       # Check for unprimed plugin, prime it if needed.
       from apstools.devices import AD_plugin_primed, AD_prime_plugin2
       if not AD_plugin_primed(adsim.hdf1):
           AD_prime_plugin2(adsim.hdf1)

    4. Plugin known to be in use by EPICS but not configured here:
    .. TODO: Show the error message, show how to fix.

       hint: ``adsim.validate_asyn_ports()`` will raise RuntimeError for uncofigured plugins.
       hint: ``adsimdet.visualize_asyn_digraph()`` draws a digraph.  Unconfigured ports will appear by themselves.

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
