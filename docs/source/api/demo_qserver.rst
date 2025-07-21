.. _api.demo_qserver:

Demo Queue Server
=================

.. currentmodule:: apsbits.demo_qserver



Starting the Server
===================

.. code-block:: bash

    ./qs_host.sh

Configuration
-------------

.. code-block:: yaml

    # qs-config.yml
    host: localhost
    port: 8080
    name: demo_qserver
    log_level: INFO

The demo queue server provides an example implementation of a Bluesky Queue Server using APSBITS.

For more details on using the Queue Server, see :doc:`../guides/qserver_service`.
