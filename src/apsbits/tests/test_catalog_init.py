"""Test the catalog_init module."""

from contextlib import nullcontext as does_not_raise
from unittest.mock import patch

import pytest
from tiled.profiles import ProfileNotFound

# Run these tests without running startup.py.
with patch("logging.Logger.bsdev"):
    from apsbits.core.catalog_init import _databroker_named_catalog
    from apsbits.core.catalog_init import _databroker_temporary_catalog
    from apsbits.core.catalog_init import _tiled_profile_client
    from apsbits.core.catalog_init import _tiled_temporary_catalog
    from apsbits.core.catalog_init import init_catalog


@pytest.mark.parametrize(
    "iconfig, handler, cat_type, context",
    [
        pytest.param(
            {},
            _databroker_temporary_catalog,
            "BlueskyMsgpackCatalog",
            does_not_raise(),
            id="temporary databroker catalog",
        ),
        pytest.param(
            {},
            init_catalog,
            "BlueskyMsgpackCatalog",
            does_not_raise(),
            id="default to temporary databroker catalog",
        ),
        pytest.param(
            dict(
                DATABROKER_CATALOG="no_such_catalog",
                TILED_PROFILE_NAME="no_such_profile",
            ),
            init_catalog,
            "BlueskyMsgpackCatalog",
            does_not_raise(),
            id="invalid catalog & profile: fallback to temporary catalog",
        ),
        pytest.param(
            {},
            _databroker_named_catalog,
            "NoneType",
            does_not_raise(),
            id="no databroker catalog name",
        ),
        pytest.param(
            dict(DATABROKER_CATALOG="no_such_catalog"),
            _databroker_named_catalog,
            "ignored",
            pytest.raises(KeyError, match="'no_such_catalog'"),
            id="no such databroker catalog name",
        ),
        pytest.param(
            {},
            _tiled_profile_client,
            "NoneType",
            does_not_raise(),
            id="no tiled profile name",
        ),
        pytest.param(
            dict(TILED_PROFILE_NAME="no_such_profile"),
            _tiled_profile_client,
            "ignored",
            pytest.raises(
                ProfileNotFound,
                match="Profile 'no_such_profile' not found.",
            ),
            id="no such tiled profile name",
        ),
        # TODO: _tiled_profile_client with:
        #    valid TILED_PROFILE_NAME
        #    valid TILED_PROFILE_NAME & valid TILED_PATH_NAME
        #    valid TILED_PROFILE_NAME & invalid TILED_PATH_NAME
        pytest.param(
            {},
            _tiled_temporary_catalog,
            "Container",
            does_not_raise(),
            id="temporary tiled catalog",
        ),
        # TODO: _tiled_temporary_catalog & valid TILED_SAVE_PATH
        # TODO: _tiled_temporary_catalog & invalid TILED_SAVE_PATH
    ],
)
def test_handlers(iconfig, handler, cat_type, context):
    """Test the handlers that create 'cat' objects."""
    with context:
        cat = handler(iconfig)
        assert type(cat).__name__ == cat_type


def test_use_temporary_tiled_catalog():
    """Typical use of the tiled temporary catalog."""
    import bluesky
    from bluesky_tiled_plugins import TiledWriter
    from ophyd.sim import noisy_det

    cat = _tiled_temporary_catalog({})
    tw = TiledWriter(cat, batch_size=1)
    RE = bluesky.RunEngine()
    RE.subscribe(tw)

    delay = 0.1
    npts = 15
    nruns = len(cat)
    (uid,) = RE(bluesky.plans.count([noisy_det], num=npts, delay=delay))
    assert isinstance(uid, str)
    assert len(cat) == 1 + nruns
    run = cat[uid]
    assert run.stop["num_events"]["primary"] == npts
    assert (run.stop["time"] - run.start["time"]) >= delay * npts

    data = run.primary.read()
    assert "noisy_det" in data
    assert len(data["noisy_det"]) == npts
