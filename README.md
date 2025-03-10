# BITS: Template Package for Bluesky Instruments

BITS: **B**luesky **I**nstrument **T**emplate**S**

Template of a Bluesky Data Acquisition Instrument in console, notebook, &
queueserver.

## Installation

Clone the repository.

```bash
git clone git@github.com:BCDA-APS/BITS.git
cd BITS
```

Set up the development environment.


export ENV_NAME=bits
conda create -y -n $ENV_NAME python=3.11 pyepics
conda activate $ENV_NAME
pip install -e ."[all]"
```

## IPython console

To start the bluesky instrument session in a ipython execute the next command in a terminal:

```bash
ipython
```

## Jupyter Notebook
Start JupyterLab, a Jupyter notebook server, or a notebook, VSCode.

## Starting the BITS Package

```py
from instrument.startup import *
RE(make_devices())  # create all the ophyd-style control devices
```

## Running Sim Plan Demo

To run some simulated plans that ensure the installation worked as expected
please run the next commands inside an ipython session or a jupyter notebook
after starting the data acquisition:

```py
RE(sim_print_plan())
RE(sim_count_plan())
RE(sim_rel_scan_plan())
```

See this [example](./docs/source/demo.ipynb).

## Configuration files

The files that can be configured to adhere to your preferences are:

- `configs/iconfig.yml` - configuration for data collection
- `configs/logging.yml` - configuration for session logging to console and/or files
- `qserver/qs-config.yml`    - contains all configuration of the QS host process. See the [documentation](https://blueskyproject.io/bluesky-queueserver/manager_config.html) for more details of the configuration.

## queueserver

The queueserver has a host process that manages a RunEngine. Client sessions
will interact with that host process.

### Run a queueserver host process

Use the queueserver host management script to start the QS host process.  The
`restart` option stops the server (if it is running) and then starts it.  This is
the usual way to (re)start the QS host process. Using `restart`, the process
runs in the background.

```bash
./qserver/qs_host.sh restart
```

### Run a queueserver client GUI

To run the gui client for the queueserver you can use the next command inside the terminal:

```bash
queue-monitor &
```

### Shell script explained

A [shell script](./qserver/qs_host.sh) is used to start the QS host process. Below
are all the command options, and what they do.

```bash
(bstest) $ ./qserver/qs_host.sh help
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
```

Alternatively, run the QS host's startup command directly within the `./qserver/`
subdirectory.

```bash
cd ./qserver
start-re-manager --config=./qs-config.yml
```

## Testing

Use this command to run the test suite locally:

```bash
pytest -vvv --lf ./src
```

## Documentation

<details>
<summary>prerequisite</summary>

To build the documentation locally, install [`pandoc`](https://pandoc.org/) in
your conda environment:

```bash
conda install conda-forge::pandoc
```

</details>

Use this command to build the documentation locally:

```bash
make -C docs clean html
```

Once the documentation builds, view the HTML pages using your web browser:

```bash
BROWSER ./docs/build/html/index.html &
```

### Adding to the documentation source

The documentation source is located in files and directories under
`./docs/source`.  Various examples are provided.

Documentation can be added in these formats:
[`.rst`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
(reStructured text), [`.md`](https://en.wikipedia.org/wiki/Markdown) (markdown),
and [`.ipynb`](https://jupyter.org/) (Jupyter notebook). For more information,
see the [Sphinx](https://www.sphinx-doc.org/) documentation.

## Warnings

### Bluesky Queueserver

The QS host process writes files into the `qserver/` directory. This directory can be
relocated. However, it should not be moved into the instrument package since
that might be installed into a read-only directory.

## How-To Guides
### How to use the template

Consider renaming this `instrument` package to be more clear that is specific to *this*
instrument.  This will be the name by which it is `pip` installed and also used with
`import`.  Let's use an example instrument package name `my_instrument` below to show which parts are edited.

1) Click on use as template button
2) Adjust the following parameters in the following files:
    - `pyproject.toml`
        - `[project]` `name =` *example: `my_instrument`*
        - `[project.urls]`  *change URLs for your repo*
        - `[tool.setuptools]` `package-dir = {"instrument" = "src/instrument"}` *example: `{"my_instrument" = "src/instrument"}`*
    - `src/instrument/init.py`
        - `__package__ = "instrument"` *example: `"my_instrument"`*
    - `src/instrument/configs/iconfig.yml`
        - `DATABROKER_CATALOG:` *change from `temp` to your catalog's name*
        - `beamline_id:` *one word beamline name (such as known by APS scheduling system)*
        - `instrument_name:` *descriptive name of your beamline*
        - `DM_SETUP_FILE:` *Path to DM bash setup file, comment out if you do not have*
        - `BEC:` *adjust for your preferences*
    - `qserver/qs-config.yml`
        - `startup_module: instrument.startup` *example: `my_instrument.startup`*
    - `docs/source/conf.py`
        - `import instrument` *example `import my_instrument`*
        - `project = "instrument"` *example: `"my_instrument"`*
        - `version = instrument.__version__` *example: `my_instrument.__version__`*

- [APS Data Management Plans](./docs/source/guides/dm.md)
