BITS Installation Guide
========================

This guide provides both quick installation steps and comprehensive setup instructions for BITS (Bluesky Instrument Template Structure).

Quick Start Installation
------------------------

**Get BITS running in 3 commands:**

.. code-block:: bash

    conda create -y -n bits_env python=3.11 pyepics
    conda activate bits_env
    pip install apsbits

**Verify installation:**

.. code-block:: python

    from apsbits.demo_instrument.startup import *
    print(f"BITS installed successfully! Demo instrument loaded.")
    RE(sim_count_plan())

Complete Installation Guide
---------------------------

Environment Setup
~~~~~~~~~~~~~~~~~

BITS requires a dedicated conda environment for proper dependency management:

.. code-block:: bash
    :linenos:

    # Create environment with essential dependencies
    export INSTALL_ENVIRONMENT_NAME=bits_production
    conda create -y -n "${INSTALL_ENVIRONMENT_NAME}" python=3.11 pyepics
    conda activate "${INSTALL_ENVIRONMENT_NAME}"

    # Install BITS framework
    pip install apsbits

    # Optional: Install development tools
    pip install "apsbits[dev]"

.. tip:: Replace ``INSTALL_ENVIRONMENT_NAME`` with your preferred environment name.

Dependencies and Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Core Requirements:**
- Python 3.11+
- PyEpics (EPICS Channel Access)
- Bluesky ecosystem packages
- apstools library

**Optional Components:**
- Jupyter Lab (for notebook operation)
- PyQt5 (for GUI components)
- Additional area detector plugins

**Network Requirements:**
- EPICS Channel Access network connectivity
- APS subnet access (for production deployments)
- Data management system access (optional)

Verification and Testing
~~~~~~~~~~~~~~~~~~~~~~~~

**Test basic functionality:**

.. code-block:: python

    # Test BITS import and basic functionality
    from apsbits.demo_instrument.startup import *

    # List available objects
    listobjects()

    # Run test plans
    RE(sim_print_plan())
    RE(sim_count_plan())
    RE(sim_rel_scan_plan())

**Test EPICS connectivity (if available):**

.. code-block:: bash

    # Test PyEpics installation
    python -c "import epics; print('PyEpics version:', epics.__version__)"

    # Test channel access
    caget EPICS:PV:NAME  # Replace with actual PV

Installation Options
~~~~~~~~~~~~~~~~~~~~

**Development Installation:**

For BITS framework development or custom modifications:

.. code-block:: bash

    git clone https://github.com/BCDA-APS/BITS.git
    cd BITS
    pip install -e ".[dev]"

**Production Deployment:**

For beamline production systems:

.. code-block:: bash

    # Install from PyPI
    pip install apsbits

    # Or install specific version
    pip install apsbits==1.2.3

Troubleshooting
~~~~~~~~~~~~~~~

**Common Issues:**

1. **PyEpics import errors:**

   .. code-block:: bash

       conda install -c conda-forge pyepics

2. **Qt/PyQt5 issues:**

   .. code-block:: bash

       conda install -c conda-forge pyqt

3. **Permission errors on APS subnet:**

   Ensure proper network configuration and EPICS gateway access.

4. **Module not found errors:**

   Verify conda environment activation:

   .. code-block:: bash

       conda activate bits_env
       which python

**Getting Help:**

- Check the `troubleshooting guide <guides/troubleshooting.html>`_
- Report issues on `GitHub <https://github.com/BCDA-APS/BITS/issues>`_
- Contact beamline staff for deployment-specific support

Next Steps
~~~~~~~~~~

After successful installation:

1. :doc:`Create your first instrument <guides/creating_instrument>`
2. :doc:`Configure devices and plans <guides/quick_start/index>`
3. :doc:`Set up queue server <guides/qserver>`
4. :doc:`Integrate with data management <guides/dm>`
