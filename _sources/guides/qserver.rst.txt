.. _qserver:

Queue Server
============

The Queue Server provides a way to run Bluesky plans remotely. We assume you have created used the create-bits command to create an instrument named ``new_instrument``.

Configuration
--------------------

The Queue Server configuration file will be stored inside ``src/new_instrument_qserver/qs-config.yml``:

.. literalinclude:: ../../../src/apsbits/demo_qserver/qs-config.yml
   :language: yaml

Starting the Server
-----------------------


The Queue Server can be started using the script at ``src/new_instrument_qserver/qs_host.sh``:

.. literalinclude:: ../../../src/apsbits/demo_qserver/qs_host.sh
   :language: bash


QS host -- queueserver host process
-----------------------------------

Use the queueserver host management script.  This option stops the server (if it
is running) and then starts it.  This is the usual way to (re)start the QS host
process.

.. code-block:: bash

    ./new_instrument_qserver/qs_host.sh restart

.. _qs.client:

Example Usage queueserver commandline
----------------------------------------

Here's an example of how to use the Queue Server:

.. code-block:: python

    from bluesky.plans import count
    from ophyd.sim import det

    # Connect to the Queue Server
    from bluesky_queueserver_api import BPlan
    from bluesky_queueserver_api.zmq import REManagerAPI

    # Create a plan
    plan = BPlan("count", [det], num=5)

    # Add the plan to the queue
    api = REManagerAPI()
    api.item_add(plan)

    # Start the queue
    api.queue_start()

.. _qs.host:


queueserver client GUI
------------------------

At this time, there is one GUI recommended for use with the bluesky queueserver.
Other GUI clients are in development and show promise of improvements.  For now,
use this one.

.. code-block:: bash

    queue-monitor &

.. _qs.host.configure:

Configure the QS Host
-----------------------

File ``qs-config.yml`` contains all configuration of the QS host process.
The source code contains lots of comments about the various settings. See the
bluesky-queueserver documentation [#]_ for more details of the configuration.

The QS host process writes files into this directory. This directory can be
relocated. However, it should not be moved into the instrument package since
that might be installed into a read-only directory.

.. [#] https://blueskyproject.io/bluesky-queueserver/manager_config.html

shell script ``qs_host.sh``
-----------------------------

A shell script ``qs_host.sh`` is used to start the QS host process. Typically,
it is run in the background: ``./new_instrument_qserver/qs_host.sh restart``. This command looks for
a running QS host process.  If found, that process is stopped.  Then, a new QS
host process is started in a *screen* [#]_ session.

.. [#] https://www.gnu.org/software/screen/manual/screen.html

.. code-block:: bash
    :linenos:

    (bstest) $ ./new_instrument_qserver/qs_host.sh help
    Usage: qs_host.sh {start|stop|restart|status|checkup|console|run} [NAME]

        COMMANDS
            console   attach to process console if process is running in screen
            checkup   check that process is running, restart if not
            restart   restart process
            run       run process in console (not screen)
            start     start process
            status    report if process is running
            stop      stop process

        OPTIONAL TERMS
            NAME      name of process (default: bluesky_queueserver-)

Alternatively, run the QS host's startup command directly within the ``./new_instrument_qserver/``
subdirectory.

.. code-block:: bash
    :linenos:

    cd ./qserver
    start-re-manager --config=./qs-config.yml
