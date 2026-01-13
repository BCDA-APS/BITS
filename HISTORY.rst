..
  This file describes user-visible changes between the versions.
  At this time, there is no automation to update this file.
  Try to describe in human terms what is relevant for each release.

  Revise this file before tagging a new release.

  Subsections could include these headings (in this order), omit if no content.

    Notice
    Breaking Changes
    New Features
    Enhancements
    Fixes
    Maintenance
    Deprecations
    New Contributors

.. _release_notes:

========
Releases
========

Brief notes describing each release and what's new.

Project `milestones <https://github.com/prjemian/hklpy2/milestones>`_
describe future plans.

.. Coming release content can be gathered here.
    Some people object to publishing unreleased changes.

    2.0.1
    #####

    release expected ?

    New Features
    ---------------

    * Hoist support to setup baseline stream using labels kwarg from USAXS.

    Maintenance
    ---------------

    * Bump iconfig version to 2.0.1 for the baseline addition.
    * Remove run_engine section from QS config.yml file and pin QS to 0.0.22+.

2.0.0 (PyPI) and 1.0.6 (repository)
###################################

released 2025-10-21

Note that PyPI version (2.0.0) is different than repository (1.0.6).
They share the same source code hash (``484b02f1537301``).

1.0.4
#####

released 2025-05-14

1.0.3
#####

released 2025-05-01

Enhancements
---------------

* arguments for run engine

Fixes
-----

* 'make_devices()' from yaml file

Maintenance
---------------

* Clean backend

1.0.2
#####

released 2025-04-18

Maintenance
---------------

* Add a release history file
* Documentation overhaul1
* adding install docs given new workflow
* Feature/API_functionalities and Makedevices

    Breaking Changes
    ----------------

    * **Callback file renaming**: Demo callback files renamed to follow `_demo` naming convention:

      * ``nexus_data_file_writer.py`` → ``demo_nexus_callback.py``
      * ``spec_data_file_writer.py`` → ``demo_spec_callback.py``

      Import paths updated in startup.py. Direct imports of these modules will need updating.

    * **DM plans removed**: The ``dm_plans.py`` file has been removed to reduce apstools dependency.
      DM configuration infrastructure remains in iconfig.yml and startup.py.

    * **StoredDict implementation**: Now uses local implementation instead of ``apstools.utils.StoredDict``.
      This reduces external dependencies while maintaining full compatibility.

    Enhancements
    ------------

    * **Improved error handling**: Enhanced error messages with specific exception types and detailed context across core modules (device loading, configuration parsing, RunEngine initialization, databroker catalog setup).

    * **Complete type annotations**: Added comprehensive type annotations to all public APIs for better IDE support and code maintainability.

    * **Code quality improvements**: Added ``py.typed`` marker for mypy support and improved code formatting compliance.

1.0.1
#####

released 2025-03-24

Fixes
-----

* Calling RE(make_devices()) twice raises a lot of errors.
* startup sequence needs revision
* make_devices() needs a 'clear 'option
* make_devices() is noisy
* Why does make_devices() add all ophyd.sim simulator objects to ophyd registry?
* First argument to logger.LEVEL() should not be an f-string
* Adjust the order of steps when creating RE
* bp.scan (& others) missing in queueserver
* QS restart does not restart when QS was running

1.0.0
#####

released 2025-03-21

Initial public release.
