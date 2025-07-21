Jupyter notebook
================

There are several alternatives to running a notebook.
An example notebook is provided:
.. [#] download notebook: :download:`../resources/demo.ipynb`


Jupyter
-------

Instructions for running a notebook with Jupyter are on the web [#]_.

.. [#] https://docs.jupyter.org/en/latest/running.html

Once in the web browser, open a new notebook.  Pick the kernel with your bluesky
installation, including the `instrument` package you installed.

Jupyter Lab
-----------

Instructions for starting a JupyterLab server are on the web [#]_.

.. [#] https://jupyterlab.readthedocs.io/en/stable/getting_started/starting.html

Once in the web browser, open a new notebook.  Pick the kernel with your bluesky
installation, including the `instrument` package you installed.

When ready to load the bluesky data acquisition for use, type this in a notebook
code cell:

.. code-block:: py

    from apsbits.demo_instrument.startup import *

VSCode editor
-------------

The VSCode editor [#]_ has extension packages to run notebooks in the editor.
See the web for advice on which extensions.  [#]_

.. [#] Microsoft Visual Studio Code Editor
.. [#] https://www.alphr.com/vs-code-open-jupyter-notebook/

Once the VSCode editor is running (with the jupyter notebook extensions), create
a new notebook file (name it something such as ``notebook.ipynb``). The
``.ipynb`` file extension is what informs VSCode to treat it as a notebook.
Pick the kernel with your bluesky installation, including the `instrument`
package you installed.

When ready to load the bluesky data acquisition for use, type this in a notebook
code cell:

.. code-block:: py

    from apsbits.demo_instrument.startup import *
