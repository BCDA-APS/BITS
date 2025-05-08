# Guide: APS Data Management Plans

Provides a few examples of the plans that interact with APS Data Management (DM)
tools.

## Required

The DM tools rely on the existence of a set of environment variables that define various aspects of the DM system.

## Show any DM jobs still processing

Use the `dm_list_processing_jobs()` plan stub to show DM any workflow jobs that
are still running or pending.  These are installed by calling
`aps_dm_setup(DM_SETUP_SCRIPT)` in each session before you call any other DM
code.

Here, `DM_SETUP_SCRIPT` is the full path to the bash setup shell script provided
by DM for this account.  The exact path can be different for some installations.
If unsure, contact the APS DM team for advice.

Note: `aps_dm_setup` is not a bluesky plan stub.  Call it as a standard Python
function.

Here's an example:

```py
from apsbits.utils.aps_functions import aps_dm_setup

aps_dm_setup("/home/dm/etc/dm.setup.sh")
```

## Start a new workflow job

The `dm_kickoff_workflow()` plan can be used to start a DM workflow job.  See
the source code for additional options (such as how often to report progress and
how to wait for the workflow to finish before the bluesky plan proceeds).

```py
from new_instrument.plans.dm_plans import dm_kickoff_workflow

# Use the run with `uid` from the catalog `cat`.
run = cat[uid]

# Create the dictionary of arguments for the chosen workflow.
argsDict = {
    "filePath": "path/to/data/file.mda",  # example
    "experimentName": "testing-2024-11",  # example
    "workflowName": "processing",  # existing workflow name
    # ... any other items required by the workflow
}

# Start the workflow job from the command line:
RE(dm_kickoff_workflow(run, argsDict))
```

In a plan, replace the call to `RE(...)` with `yield from ...`, such as:

```py
def a_plan():
    # earlier steps
    yield from dm_kickoff_workflow(run, argsDict)
    # later steps
```

## Start a new workflow job (Low-level)

If the `dm_kickoff_workflow()` plan stub does more than you want, you might consider the `dm_submit_workflow_job()`
plan stub.  The `dm_submit_workflow_job()` plan stub is
a thin wrapper around DM's `startProcessingJob()` function.
The plan stub converts this DM function into a bluesky plan, and reports the DM workflow job `id` once the job has been submitted.

As above, you'll need the `workflowName` and the `argsDict`.

From the command line: `RE(dm_submit_workflow_job(workflowName, argsDict))`

In a plan: `yield from dm_submit_workflow_job(workflowName, argsDict)`

## References

The `apstools`
[package](https://bcda-aps.github.io/apstools/latest/api/_utils.html#aps-data-management)
has more support to integrate various capabilities of the DM tools.

For more information about DM, see its [API
Reference](https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/Beamline-Services/API-Reference).
