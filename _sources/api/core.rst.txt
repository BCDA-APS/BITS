.. _api.core:

Core Components
===============

The core module provides fundamental components for building a Bluesky data acquisition system.

.. currentmodule:: apsbits.core

.. autosummary::
   :toctree: generated
   :recursive:

   best_effort_init
   catalog_init
   run_engine_init

These components are used to:

1. Initialize the Run Engine
2. Set up data catalogs
3. Configure best-effort callbacks
4. Establish baseline configurations

Example Usage
-------------

Here's how to initialize the Run Engine, set up data catalogs, and configure best-effort callbacks:

.. code-block:: python

    from apsbits.core import run_engine_init, catalog_init, best_effort_init

    # Initialize the Run Engine
    RE = run_engine_init()

    # Set up data catalogs
    cat = catalog_init()

    # Configure best-effort callbacks
    bec = best_effort_init(RE)

API Reference
-------------

.. automodule:: apsbits.core
   :members:
   :undoc-members:
   :show-inheritance:
