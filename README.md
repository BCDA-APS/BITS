# APSBITS: Template Package for Bluesky Instruments

| PyPI | Coverage |
| --- | --- |
[![PyPi](https://img.shields.io/pypi/v/apsbits.svg)](https://pypi.python.org/pypi/apsbits) | [![Coverage Status](https://coveralls.io/repos/github/BCDA-APS/BITS/badge.svg?branch=main)](https://coveralls.io/github/BCDA-APS/BITS?branch=main) |

BITS: **B**luesky **I**nstrument **T**emplate **S**tructure

Template of a Bluesky Data Acquisition Instrument in console, notebook, &
queueserver.

## Production use of BITS

Please create a bits instrument using our template repository: https://github.com/BCDA-APS/DEMO-BITS


## Installing the BITS Package

```bash
export INSTALL_ENVIRONMENT_NAME=apsbits_env
conda create -y -n "${INSTALL_ENVIRONMENT_NAME}" python=3.11 pyepics
conda activate "${INSTALL_ENVIRONMENT_NAME}"
pip install apsbits
```

For development please reference our documentation

## Testing the apsbits base installation

On an ipython console

```py
from apsbits.demo_instrument.startup import *
listobjects()
RE(sim_print_plan())
RE(sim_count_plan())
RE(sim_rel_scan_plan())
```
