.. _creating_instrument:

Creating An Instrument
-------------------------

Once the repository is set up and the environment is ready, the next step is to create the instrument.
This guide explains how to create a new instrument from our template for instrument repositories.

Inside the root folder inside of the templated repository run create

.. code-block:: bash

    export YOUR_INSTRUMENT_NAME=new_instrument
    create-bits $YOUR_INSTRUMENT_NAME
    pip install -e .


.. tip::
    Every single time you create a new instrument, you will need to install the new instrument using the pip command
