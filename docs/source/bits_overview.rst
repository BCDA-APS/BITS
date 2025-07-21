APS Bluesky Software Ecosystem Overview
=======================================

This document provides an overview of key GitHub repositories maintained and used by the APS for integrating the `Bluesky` data acquisition framework into beamline operations.

BITS Ecosystem Diagram
----------------------

The following figure describes the relationships among the various repositories and modules that compose or support the BITS framework at APS.

.. graphviz::

   digraph BITS_Ecosystem {
       rankdir=LR;
       node [shape=box style=filled fillcolor=lightgrey fontname="Arial"];

       {rank=min;
       BITS [label="BITS\n(Main Package)", shape=ellipse, fillcolor=lightblue];
       training [label="Bluesky_training\n(Training Resources)", shape=ellipse, fillcolor=lightblue];
       }

       apsbits [label="apsbits\n(Core Functionality)", shape=ellipse, fillcolor=lightyellow];
       demo_instr [label="demo_instrument\n(Standard Instrument)"];
       demo_qserver [label="demo_qserver\n(Standard QServer)"];

       {rank=same;
        apstools [label="apstools\n(Devices, Plans, Callbacks)", shape=ellipse, fillcolor=lightblue];
       guarneri [label="guarneri\n(Ophyd Loader)", shape=ellipse, fillcolor=lightblue];
       hklpy2 [label="hklpy2\n(Diffractometer Support)", shape=ellipse, fillcolor=lightblue];
       }

       {rank=same;
       BITS_Starter [label="BITS-Starter\n(Starter Repo)", shape=ellipse, fillcolor=lightblue];
       guarneri_maker [label="guarneri_maker\n(Ophyd Loader Maker)", shape=ellipse, fillcolor=lightyellow];
       apst_devices [label="apstools_devices\n(Devices)", shape=ellipse, fillcolor=lightyellow];
       apst_plans [label="apstools_plans\n(Plans)", shape=ellipse, fillcolor=lightyellow];
       apst_callbacks [label="apstools_callbacks\n(Callbacks)", shape=ellipse, fillcolor=lightyellow];
       apst_utils [label="apstools_utils\n(Utils)", shape=ellipse, fillcolor=lightyellow];
       }

       new_instrument [label="new_instrument\n(New Instrument)", shape=ellipse, fillcolor=lightblue];

       BITS -> apsbits [label="includes"];
       {demo_instr demo_qserver} -> BITS_Starter [label="source for"];
       BITS_Starter -> new_instrument [label="template for"];
       apsbits -> {demo_instr demo_qserver} [label="provides"];
       BITS -> apstools [label="uses"];
       apstools -> {apst_devices apst_plans apst_callbacks apst_utils} [label="includes"];
       {apst_devices apst_plans apst_callbacks apst_utils} -> new_instrument [label="provides"];
       BITS -> guarneri [label="uses"];
       guarneri -> guarneri_maker [label="includes"];
       guarneri_maker -> new_instrument [label="provides"];
       BITS -> hklpy2 [label="uses"];
       training -> BITS [label="supports"];
   }

Repository Descriptions
-----------------------

- `BITS <https://github.com/BCDA-APS/BITS>`_

  The central repository for APS efforts to integrate Bluesky into beamline environments. It provides configuration, utilities, and architectural support for deploying Bluesky-based instruments at the APS.

- `BITS-Starter <https://github.com/BCDA-APS/BITS-Starter/>`_

  A template repository for creating new BITS-compatible Bluesky instruments. Offers a boilerplate structure to streamline deployment.

- **apsbits (submodule in BITS)**

  Core BITS functionality. Encapsulates the logic and base configurations used by BITS instruments.

  - `apsbits/demo_instrument`: A reference Bluesky instrument showcasing a standard BITS-compliant setup.
  - `apsbits/demo_qserver`: A reference QServer that integrates with the demo instrument.

- `apstools <https://github.com/BCDA-APS/apstools>`_

  A general-purpose utility library with reusable Bluesky components:

  - `apstools.devices`: Collection of commonly used Ophyd devices across APS beamlines.
  - `apstools.plans`: Frequently used Bluesky plans tailored to APS experiments.
  - `apstools.callbacks`: Ready-made Bluesky callbacks for logging, visualization, and monitoring.

- `guarneri <https://github.com/spc-group/guarneri>`_

  A device registry and dynamic loader for Ophyd. Simplifies the instantiation and reuse of instrument configurations.

- `hklpy2 <https://prjemian.github.io/hklpy2/>`_

  Diffractometer as ophyd PseudoPositioner.  Supports Bluesky operations with various diffractometer geometries in both reciprocal space and real space.

- **`Bluesky_training`** (Work In Progress)


  A complete training suite developed to support APS beamline scientists and users adopting the Bluesky ecosystem. Includes examples, tutorials, and curriculum materials.

Summary
-------

These packages form a modular and extensible software stack supporting the transition to Bluesky at APS. They emphasize reuse, standardization, and training, enabling robust and scalable data acquisition workflows across beamlines.
