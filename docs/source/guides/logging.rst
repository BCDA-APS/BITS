Logging Configuration Guide
=========================

This guide explains how to configure and customize logging in the BITS package.

Overview
--------

The logging system provides:

* Console output for immediate feedback
* File logging for persistent records
* IPython session logging
* Module-specific log levels
* Log rotation to manage disk space

Default Configuration
-------------------

The default logging configuration is defined in ``src/apsbits/configs/logging.yml``:

.. code-block:: yaml

    console_logs:
      date_format: "%a-%H:%M:%S"
      log_format: "%(levelname)-.1s %(asctime)s.%(msecs)03d: %(message)s"
      level: info
      root_level: bsdev

    file_logs:
      date_format: "%Y-%m-%d %H:%M:%S"
      log_directory: .logs
      log_filename_base: logging.log
      log_format: "|\
        %(asctime)s.%(msecs)03d|\
        %(levelname)s|\
        %(process)d|\
        %(name)s|\
        %(module)s|\
        %(lineno)d|\
        %(threadName)s| - \
        %(message)s"
      maxBytes: 1_000_000
      backupCount: 9
      level: info
      rotate_on_startup: true

    ipython_logs:
      log_directory: .logs
      log_filename_base: ipython_log.py
      log_mode: rotate
      options: -o -t

    modules:
      apstools: warning
      bluesky-queueserver: warning
      bluesky: warning
      bluesky.RE: warning
      caproto: warning
      databroker: warning
      ophyd: warning

Log Levels
---------

The package defines seven log levels in order of increasing detail:

=========   =========   ==================================================
name        severity    comments
=========   =========   ==================================================
CRITICAL    50          Examine immediately. **Quietest** level.
ERROR       40          Something has failed.
WARNING     30          Something needs attention.
INFO        20          A report that may be of interest.
BSDEV       15          A report of interest to developers.
DEBUG       10          Diagnostic. **Noisiest** level.
NOTSET      0           Initial setting, defaults to WARNING.
=========   =========   ==================================================

Custom Configuration
------------------

To customize logging for your instrument, create an ``extra_logging.yml`` file in your instrument's config directory. The settings in this file will override the default configuration:

.. code-block:: yaml

    # Custom logging configuration
    # These settings will override the default configuration
    console_logs:
      level: debug  # Override console log level
      root_level: debug  # Override root log level

    file_logs:
      log_directory: /custom/path/to/logs  # Override log directory
      maxBytes: 2_000_000  # Override max file size
      backupCount: 5  # Override backup count

    modules:
      your_module: debug  # Add or override module logging level

The configuration system will:
1. Load the default configuration from ``src/apsbits/configs/logging.yml``
2. If an extra configuration is provided, merge it with the default configuration:
   * For dictionary settings (like ``console_logs``, ``file_logs``), only the specified keys are overridden
   * For non-dictionary settings, the entire setting is replaced
   * New settings not present in the default configuration are added

Then, in your ``startup.py``, configure logging with your custom configuration:

.. code-block:: python

    from pathlib import Path
    from apsbits.utils.logging_setup import configure_logging

    # Get the path to your instrument's config directory
    instrument_path = Path(__file__).parent
    extra_logging_configs_path = instrument_path / "configs" / "extra_logging.yml"

    # Configure logging with your custom settings
    # The extra configuration will override the default settings
    configure_logging(extra_logging_configs_path=extra_logging_configs_path)

Example of Configuration Override
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default configuration:
.. code-block:: yaml

    console_logs:
      level: info
      root_level: bsdev

    file_logs:
      maxBytes: 1_000_000
      backupCount: 9

Extra configuration:
.. code-block:: yaml

    console_logs:
      level: debug  # Only overrides the level, root_level remains bsdev

    file_logs:
      maxBytes: 2_000_000  # Only overrides maxBytes, backupCount remains 9

Resulting configuration:
.. code-block:: yaml

    console_logs:
      level: debug      # From extra config
      root_level: bsdev # From default config

    file_logs:
      maxBytes: 2_000_000  # From extra config
      backupCount: 9       # From default config

Error Handling
-------------

The logging configuration system includes error handling for common issues:

1. Invalid or Empty Configuration Files:
   * The main logging configuration file must be valid and non-empty
   * If the main configuration is invalid, a ``ValueError`` is raised
   * If the extra configuration is invalid, a warning is logged and the default configuration is used

2. Missing Configuration Files:
   * The main logging configuration file must exist
   * Extra configuration files are optional
   * If an extra configuration file is missing, the default configuration is used

Example error handling in your code:

.. code-block:: python

    try:
        configure_logging(extra_logging_configs_path=extra_logging_configs_path)
    except ValueError as e:
        logger.error("Failed to configure logging: %s", e)
        # Handle the error appropriately
    except Exception as e:
        logger.exception("Unexpected error configuring logging")
        # Handle unexpected errors

Log File Locations
----------------

By default, logs are stored in a ``.logs`` directory at the root of your package:

.. code-block:: text

    your_package/
    ├── .logs/
    │   ├── logging.log        # Main log file
    │   ├── logging.log.1      # Rotated logs
    │   ├── logging.log.2
    │   └── ipython_log.py     # IPython session logs
    ├── src/
    ├── tests/
    └── ...

You can override the log directory location by specifying ``log_directory`` in your configuration:

.. code-block:: yaml

    file_logs:
      log_directory: /custom/path/to/logs
      log_filename_base: my_instrument.log

Log Rotation
-----------

Log files are automatically rotated to manage disk space:

* Files are rotated when they reach the specified size (default: 1MB)
* A maximum number of backup files is kept (default: 9)
* Logs can be rotated on startup (default: true)

Configure these settings in your logging configuration:

.. code-block:: yaml

    file_logs:
      maxBytes: 2_000_000  # 2MB
      backupCount: 5       # Keep 5 backup files
      rotate_on_startup: true

Using Logging in Your Code
------------------------

To use logging in your code:

.. code-block:: python

    import logging

    # Get a logger for your module
    logger = logging.getLogger(__name__)

    # Log messages at different levels
    logger.debug("Detailed information for debugging")
    logger.info("General information about program execution")
    logger.warning("Warning messages for potentially problematic situations")
    logger.error("Error messages for serious problems")
    logger.critical("Critical messages for fatal errors")
    logger.bsdev("Developer-specific information")

Best Practices
-------------

1. Use appropriate log levels:
   * DEBUG: Detailed information for debugging
   * INFO: General information about program execution
   * WARNING: Potentially problematic situations
   * ERROR: Serious problems
   * CRITICAL: Fatal errors
   * BSDEV: Developer-specific information

2. Include relevant context in log messages:
   * Use string formatting for variables
   * Include error details when catching exceptions
   * Add module and function names for clarity

3. Configure module-specific logging levels to reduce noise:
   * Set verbose logging for your modules
   * Set higher levels for third-party modules

4. Use log rotation to manage disk space:
   * Set appropriate file sizes
   * Configure backup count based on available space
   * Consider rotating logs on startup for clean sessions

5. Handle logging configuration errors:
   * Always wrap logging configuration in try-except blocks
   * Provide fallback configurations when needed
   * Log configuration errors appropriately

References
----------

* `Python logging documentation <https://docs.python.org/3/library/logging.html>`_
* `Bluesky debugging guide <https://blueskyproject.io/bluesky/main/debugging.html>`_
* `Ophyd logging reference <https://blueskyproject.io/ophyd/user_v1/reference/logging.html>`_
