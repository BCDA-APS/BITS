.. _api.api:

API
===

The API module provides command-line interfaces for instrument management:

.. autosummary::
   :toctree: generated
   :recursive:

   apsbits.api.create_new_instrument
   apsbits.api.delete_instrument
   apsbits.api.run_instrument

These command-line tools help with:

1. Creating new instruments from templates
2. Deleting instruments and their associated qserver configurations
3. Running instruments and retrieving their ophyd registry information

Example Usage
-------------

Create a new instrument:

.. code-block:: bash

   create-bits --name my_instrument --path /path/to/instrument

Delete an instrument:

.. code-block:: bash

   delete-bits --name my_instrument --path /path/to/instrument

Run an instrument:

.. code-block:: bash

   run-bits --name my_instrument --path /path/to/instrument

API Reference
-------------

.. automodule:: apsbits.api
   :members:
   :undoc-members:
   :show-inheritance:
