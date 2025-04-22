User Installation
====================

It is easiest to start installation with a fresh ``conda`` environment. For
any packages that require installation of pre-compiled content (such as Qt,
PyQt, and others), install those packages with ``conda``.  For pure Python code,
use ``pip``.


.. code-block:: bash
    :linenos:

    export INSTALL_ENVIRONMENT_NAME=apsbits_env
    conda create -y -n "${INSTALL_ENVIRONMENT_NAME}" python=3.11 pyepics
    conda activate "${INSTALL_ENVIRONMENT_NAME}"
    pip install apsbits

.. tip:: Replace the text ``INSTALL_ENVIRONMENT_NAME`` with the name you wish to use
    for this conda environment.
