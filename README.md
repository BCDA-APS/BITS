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

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install apsbits      # into an active environment
# ...or, from a clone for development (uses the committed uv.lock):
uv sync --extra dev
```

For development please reference our documentation

## Startup Architecture

When a user runs `from apsbits.demo_instrument.startup import *`, the following
import and initialization sequence executes. No module runs code on import.
All initialization flows through `startup.py` via explicit function calls.

### Module Dependency Graph

Arrows show import direction. No circular imports exist.

```mermaid
graph LR
    subgraph utils["apsbits.utils (base layer)"]
        config_loaders
        aps_functions
        controls_setup
        helper_functions --> config_loaders
        logging_setup -.->|"inside fn"| config_loaders
        baseline_setup --> config_loaders
        metadata -.->|"inside fn"| apsbits_init
        stored_dict -.->|"inside fn"| config_loaders
        sim_creator --> helper_functions
    end

    subgraph core["apsbits.core (middle layer)"]
        core_init["core/__init__"] --> helper_functions
        best_effort_init --> helper_functions
        catalog_init
        instrument_init --> config_loaders
        run_engine_init --> controls_setup
        run_engine_init --> metadata
        run_engine_init --> stored_dict
    end

    subgraph demo["demo_instrument (top layer)"]
        startup
        nexus_cb["callbacks/nexus"]
        spec_cb["callbacks/spec"]
        sim_plans --> instrument_init
    end

    subgraph api["apsbits.api"]
        create_new_instrument
        delete_instrument
    end

    apsbits_init["apsbits/__init__"]

    startup --> logging_setup
    startup --> core_init
    startup --> best_effort_init
    startup --> catalog_init
    startup --> instrument_init
    startup --> run_engine_init
    startup --> helper_functions
    startup --> config_loaders
    startup --> baseline_setup
    startup --> aps_functions
    startup -.->|"if enabled"| nexus_cb
    startup -.->|"if enabled"| spec_cb
    startup --> sim_plans
```

Solid arrows = module-level imports. Dashed arrows = conditional or function-level imports.

### Initialization Sequence

Everything is called explicitly by `startup.py` in this order:
```mermaid
graph TD
    S["startup.py"] -->|1| A["configure_logging()"]
    A -->|reads| A1[("logging.yml")]
    S -->|2| B["prepare_bits()"]
    S -->|3| C["load_config()"]
    C -->|reads| C1[("iconfig.yml")]
    S -->|4| D["configure_logging(extra)"]
    D -->|reads| D1[("extra_logging.yml")]
    S -->|5| E["init_instrument()"]
    E -->|creates| E1["instrument, oregistry"]
    S -->|6| F["init_bec_peaks(iconfig)"]
    F -->|creates| F1["bec, peaks"]
    S -->|7| G["init_catalog(iconfig)"]
    G -->|creates| G1["cat"]
    S -->|8| H["init_RE(iconfig, ...)"]
    H -->|creates| H1["RE, sd"]
    S -->|"9 (if enabled)"| I["nxwriter_init(RE, iconfig)"]
    I -->|creates| I1["nxwriter"]
    S -->|"10 (if enabled)"| J["init_specwriter_with_RE(RE, iconfig)"]
    J -->|creates| J1["specwriter"]
    S -->|11| K["make_devices(...)"]
    K -->|reads| K1[("devices.yml")]
    S -->|12| L["setup_baseline_stream()"]

    style S fill:#fff3e0
    style A1 fill:#f3e5f5
    style C1 fill:#f3e5f5
    style D1 fill:#f3e5f5
    style K1 fill:#f3e5f5
    style E1 fill:#c8e6c9
    style F1 fill:#c8e6c9
    style G1 fill:#c8e6c9
    style H1 fill:#c8e6c9
    style I1 fill:#c8e6c9
    style J1 fill:#c8e6c9
```

Purple = YAML config files read from disk. Green = objects available in your session.

## Testing the apsbits base installation

On an ipython console

```py
from apsbits.demo_instrument.startup import *
listobjects()
RE(sim_print_plan())
RE(sim_count_plan())
RE(sim_rel_scan_plan())
```
