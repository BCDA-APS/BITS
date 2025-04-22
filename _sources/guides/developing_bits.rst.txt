Developing BITS
-----------------------

Install for development
========================
For development and other activities, replace the ``pip`` command above with:

.. code-block:: bash
    :linenos:

    export INSTALL_ENVIRONMENT_NAME=apsbits_env
    git clone github.com:BCDA-APS/BITS.git
    cd BITS
    conda create -y -n "${INSTALL_ENVIRONMENT_NAME}" python=3.11 pyepics
    conda activate "${INSTALL_ENVIRONMENT_NAME}"
    pip install -e ."[all]"


Testing
=======================

Use this command to run the test suite locally:

.. code-block:: bash
    :linenos:

    pytest -vvv --lf ./src


Documentation
========================

Use this command to build the documentation locally:

.. code-block:: bash
    :linenos:

    make -C docs clean html


The documentation source is located in files and directories under
`./docs/source`.  Various examples are provided.

Documentation can be added in these formats:
[`.rst`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
(reStructured text), [`.md`](https://en.wikipedia.org/wiki/Markdown) (markdown),
and [`.ipynb`](https://jupyter.org/) (Jupyter notebook). For more information,
see the [Sphinx](https://www.sphinx-doc.org/) documentation.
