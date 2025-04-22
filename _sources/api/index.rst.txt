.. _api:

API: The Source Code
====================

The APSBITS package provides tools and utilities to build Bluesky instruments. The package structure is:

.. code-block:: text
    :linenos:

    docs/source         sphinx documentation source
    pyproject.toml      project configuration
    src/               Python source code tree
        apsbits/       root of the 'apsbits' package
            api/       command-line interfaces for instrument management
            core/      core components for Bluesky data acquisition
            utils/     utilities for setup and configuration
            demo_instrument/  example instrument implementation
                startup.py   setup a demo session for Bluesky data acquisition
                callbacks/  receive and handle info from other code
                configs/   configuration files
                devices/   demo instrument's controls
                plans/    demo instrument's measurement procedures
                suspenders/  suspender implementations
                utils/      utility functions and classes
            demo_qserver/   example queueserver implementation

A Bluesky data acquisition session using the demo instrument begins with:

.. code-block:: py

    from apsbits.demo_instrument.startup import *

The ``apsbits/`` package is described in the following sections.

API Documentation
=================

This section contains detailed API documentation for the APSBITS package.

.. toctree::
   :maxdepth: 2

   core
   utils
   demo_instrument
   demo_qserver
   api




Core Components
---------------

The core components provide the fundamental building blocks for Bluesky data acquisition:

.. autosummary::
   :toctree: generated
   :recursive:

   apsbits.core.best_effort_init
   apsbits.core.catalog_init
   apsbits.core.run_engine_init

Utilities
---------

The utilities module provides helper functions and tools:

.. autosummary::
   :toctree: generated
   :recursive:

   apsbits.utils.aps_functions
   apsbits.utils.config_loaders
   apsbits.utils.controls_setup
   apsbits.utils.helper_functions
   apsbits.utils.logging_setup
   apsbits.utils.metadata
   apsbits.utils.stored_dict

Demo Components
---------------

Example implementations and templates:

.. autosummary::
   :toctree: generated
   :recursive:

   apsbits.demo_instrument
   apsbits.demo_qserver

Command-Line Interfaces
----------------------

The API module provides command-line interfaces for instrument management:

.. autosummary::
   :toctree: generated
   :recursive:

   apsbits.api.create_new_instrument
   apsbits.api.delete_instrument
   apsbits.api.run_instrument
