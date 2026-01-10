"""
Test that instrument can be started.

Here is just enough testing to get a CI workflow started. More are possible.
"""

import time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

# Import required modules from demo_instrument.startup
from apsbits.demo_instrument.plans.sim_plans import sim_count_plan
from apsbits.demo_instrument.plans.sim_plans import sim_print_plan
from apsbits.demo_instrument.plans.sim_plans import sim_rel_scan_plan
from apsbits.demo_instrument.startup import bec
from apsbits.demo_instrument.startup import cat
from apsbits.demo_instrument.startup import peaks
from apsbits.demo_instrument.startup import sd
from apsbits.demo_instrument.startup import specwriter
from apsbits.utils.config_loaders import get_config
from apsbits.utils.helper_functions import running_in_queueserver


def test_startup(runengine_with_devices: object) -> None:
    """
    Test that standard startup works and the RunEngine has initialized the devices.

    Parameters
    ----------
    runengine_with_devices : object
        Fixture providing initialized RunEngine with devices.
    """
    assert runengine_with_devices is not None
    assert cat is not None
    assert bec is not None
    assert peaks is not None
    assert sd is not None
    assert specwriter is not None

    iconfig = get_config()
    if iconfig.get("DATABROKER_CATALOG", "temp") == "temp":
        assert len(cat) == 0
    assert not running_in_queueserver()


@pytest.mark.parametrize(
    "plan, n_uids",
    [
        [sim_print_plan, 0],
        [sim_count_plan, 1],
        [sim_rel_scan_plan, 1],
    ],
)
def test_sim_plans(runengine_with_devices: object, plan: object, n_uids: int) -> None:
    """
    Test supplied simulator plans using the RunEngine with devices.
    """
    bec.disable_plots()
    # Get the initial number of runs in the catalog
    n_runs = len(cat)

    # Use the fixture-provided run engine to run the plan
    # The @with_registry decorator will automatically inject the registry
    uids = runengine_with_devices(plan())
    assert len(uids) == n_uids
    # Add a small delay to ensure data is saved
    time.sleep(0.1)
    # For sim_print_plan, we don't expect any new runs
    if plan == sim_print_plan:
        assert len(cat) == n_runs
    else:
        assert len(cat) == n_runs + len(uids)


def test_iconfig() -> None:
    """
    Test the instrument configuration.
    """
    iconfig = get_config()

    # test the version of the iconfig file (identify if too old for BITS)
    version: str = iconfig.get("ICONFIG_VERSION", "0.0.0")
    assert version >= "2.0.0"

    # Check that bluesky run documents will be saved.
    # Configure for databroker catalog and/or tiled profile.
    cat_name: str = iconfig.get("DATABROKER_CATALOG")
    profile_name: str = iconfig.get("TILED_PROFILE_NAME")
    assert (cat_name or profile_name) is not None

    assert "RUN_ENGINE" in iconfig
    assert "DEFAULT_METADATA" in iconfig["RUN_ENGINE"]

    default_md = iconfig["RUN_ENGINE"]["DEFAULT_METADATA"]
    assert "beamline_id" in default_md
    assert "instrument_name" in default_md
    assert "proposal_id" in default_md
    # Note: databroker_catalog may not be in default_md depending on config version

    xmode = iconfig.get("XMODE_DEBUG_LEVEL")
    assert xmode is not None
