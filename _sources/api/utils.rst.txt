.. _api.utils:

Utilities
=========

The utilities module provides helper functions and tools for working with Bluesky data acquisition systems.

.. currentmodule:: apsbits.utils

.. autosummary::
   :toctree: generated
   :recursive:

   aps_functions
   config_loaders
   controls_setup
   helper_functions
   logging_setup
   metadata
   stored_dict

These utilities help with:

1. Loading and managing configuration files
2. Setting up logging
3. Managing device metadata
4. Interfacing with APS-specific functionality
5. Creating and managing device configurations

Example Usage
-------------

Here's how to use some of the utility functions:

.. code-block:: python

    from apsbits.utils import config_loaders, logging_setup, metadata

    # Load configuration from YAML
    config = config_loaders.load_yaml_config('config.yml')

    # Set up logging
    logger = logging_setup.setup_logger('my_logger')

    # Store metadata
    md = metadata.get_metadata()

API Reference
-------------

.. automodule:: apsbits.utils
   :members:
   :undoc-members:
   :show-inheritance:
