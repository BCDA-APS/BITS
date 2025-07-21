=============================
Queue Server Systemd Service
=============================

This document describes how to set up and manage the Bluesky Queue Server as a systemd service, allowing for automatic startup and management of the Queue Server on Linux systems.

Service Configuration
=========================

Create a systemd service unit file at ``/etc/systemd/system/queueserver.service``. The configuration should be based on the settings in ``src/apsbits/demo_qserver/qs-config.yml`` and ``src/apsbits/demo_qserver/qs_host.sh``:

.. code-block:: ini

    [Unit]
    Description=Bluesky Queue Server Host Service
    After=network.target

    [Service]
    Type=simple
    User=YOUR_USERNAME
    Group=YOUR_GROUP

    # Environment setup
    Environment="HOME=/home/YOUR_USERNAME"
    Environment="CONDA_ROOT=/opt/conda"

    # Start-up script that activates conda and starts qs_host
    ExecStart=/bin/bash -c 'source ${CONDA_ROOT}/etc/profile.d/conda.sh && \
        conda activate YOUR_ENV_NAME && \
        start-re-manager --startup-dir /path/to/your/startup/dir'

    # Restart on failure
    Restart=always
    RestartSec=10

    # Set working directory if needed
    WorkingDirectory=/path/to/your/working/dir

    [Install]
    WantedBy=multi-user.target

Configuration Parameters
========================

Before implementing the service, you need to modify the following parameters:

* ``YOUR_USERNAME``: System user that will run the service
* ``YOUR_GROUP``: System group for the user
* ``CONDA_ROOT``: Path to your conda installation
* ``YOUR_ENV_NAME``: Name of your conda environment containing the Bluesky Queue Server
* ``/path/to/your/startup/dir``: Directory containing your startup configuration
* ``/path/to/your/working/dir``: Working directory for the service

Service Management
==================

Installation
~~~~~~~~~~~~

1. Save the service configuration file:

   .. code-block:: bash

       sudo nano /etc/systemd/system/queueserver.service

2. Reload the systemd daemon to recognize the new service:

   .. code-block:: bash

       sudo systemctl daemon-reload

Basic Service Commands
~~~~~~~~~~~~~~~~~~~~~~

Start the service:

.. code-block:: bash

    sudo systemctl start queueserver

Stop the service:

.. code-block:: bash

    sudo systemctl stop queueserver

Restart the service:

.. code-block:: bash

    sudo systemctl restart queueserver

Check service status:

.. code-block:: bash

    sudo systemctl status queueserver

Enable service to start on boot:

.. code-block:: bash

    sudo systemctl enable queueserver

Disable service from starting on boot:

.. code-block:: bash

    sudo systemctl disable queueserver

Monitoring and Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

View service logs:

.. code-block:: bash

    journalctl -u queueserver

Follow logs in real-time:

.. code-block:: bash

    journalctl -u queueserver -f

Security Considerations
=======================

1. Ensure the service user has appropriate permissions:

   * Access to conda environment
   * Access to startup directory
   * Access to working directory
   * Required network permissions

2. Consider setting up specific environment variables:

   * PYTHONPATH
   * Custom application configurations
   * Security tokens or credentials (use secure methods)

Additional Configuration Options
================================

The service can be further customized with additional systemd directives:

.. code-block:: ini

    [Service]
    # Logging configuration
    StandardOutput=append:/var/log/queueserver/output.log
    StandardError=append:/var/log/queueserver/error.log

    # Resource limits
    LimitNOFILE=65535
    TimeoutStartSec=30
    TimeoutStopSec=30

    # Security enhancements
    ProtectSystem=full
    PrivateTmp=true
    NoNewPrivileges=true

Troubleshooting
===============

Common issues and solutions:

1. Service fails to start:

   * Check logs using ``journalctl -u queueserver``
   * Verify conda path and environment name
   * Ensure all directories exist and have proper permissions

2. Environment issues:

   * Verify conda environment activation
   * Check if all required packages are installed
   * Validate environment variables

3. Permission problems:

   * Check user and group permissions
   * Verify file ownership in startup and working directories
   * Ensure systemd service user has necessary access rights

References
==========

* `Systemd Documentation <https://www.freedesktop.org/software/systemd/man/systemd.service.html>`_
* `Bluesky Queue Server Documentation <https://blueskyproject.io/bluesky-queueserver/>`_
