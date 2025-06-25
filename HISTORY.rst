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

    1.1.0
    #####

    release expected ?

    New Features
    ---------------

    * Hoist support to setup baseline stream using labels kwarg from USAXS.

    Maintenance
    ---------------

    * Bump iconfig version to 2.0.1 for the baseline addition.
    * Remove run_engine section from QS config.yml file and pin QS to 0.0.22+.

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
