"""Test the catalog_init module."""

from contextlib import nullcontext as does_not_raise
from unittest.mock import patch

import pytest
import yaml
from tiled.profiles import ProfileNotFound
from tiled.server import SimpleTiledServer

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
        # Cases needing a live tiled server / profile (valid TILED_PROFILE_NAME,
        # TILED_PATH_NAME, TILED_SAVE_PATH) are covered by the dedicated tests
        # below — they need fixtures, not just an iconfig dict.
        pytest.param(
            {},
            _tiled_temporary_catalog,
            "Container",
            does_not_raise(),
            id="temporary tiled catalog",
        ),
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


PROFILE_NAME = "apsbits_unit_test_profile"


@pytest.fixture
def tiled_profile(tmp_path):
    """A live temporary tiled server exposed as a named profile.

    Registers a profile pointing at a SimpleTiledServer and creates a ``sub``
    container so both the valid and invalid TILED_PATH_NAME cases are testable.
    """
    import tiled.profiles
    from tiled.client import from_uri

    server = SimpleTiledServer()
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    (profile_dir / "unit_test.yml").write_text(
        yaml.dump({PROFILE_NAME: {"uri": server.uri}})
    )
    tiled.profiles.paths.insert(0, profile_dir)
    tiled.profiles.load_profiles.cache_clear()  # load_profiles is lru_cached
    from_uri(server.uri).create_container("sub")  # a valid TILED_PATH_NAME
    try:
        yield PROFILE_NAME
    finally:
        server.close()
        tiled.profiles.paths.remove(profile_dir)
        tiled.profiles.load_profiles.cache_clear()  # drop the now-stale profile


def test_tiled_profile_client_valid_profile(tiled_profile):
    """Valid TILED_PROFILE_NAME connects and returns a tiled container."""
    cat = _tiled_profile_client({"TILED_PROFILE_NAME": tiled_profile})
    assert type(cat).__name__ == "Container"


def test_tiled_profile_client_valid_path(tiled_profile):
    """Valid TILED_PROFILE_NAME + valid TILED_PATH_NAME returns the sub-node."""
    cat = _tiled_profile_client(
        {"TILED_PROFILE_NAME": tiled_profile, "TILED_PATH_NAME": "sub"}
    )
    assert type(cat).__name__ == "Container"


def test_tiled_profile_client_invalid_path(tiled_profile):
    """Valid TILED_PROFILE_NAME + invalid TILED_PATH_NAME raises KeyError."""
    with pytest.raises(KeyError):
        _tiled_profile_client(
            {"TILED_PROFILE_NAME": tiled_profile, "TILED_PATH_NAME": "no_such_path"}
        )


def test_tiled_temporary_catalog_valid_save_path(tmp_path):
    """A writable TILED_SAVE_PATH yields a tiled container."""
    cat = _tiled_temporary_catalog({"TILED_SAVE_PATH": str(tmp_path)})
    assert type(cat).__name__ == "Container"
    del cat


def test_tiled_temporary_catalog_invalid_save_path(tmp_path):
    """A non-directory TILED_SAVE_PATH raises NotADirectoryError."""
    bad = tmp_path / "not_a_dir"
    bad.write_text("x")
    with pytest.raises(NotADirectoryError):
        _tiled_temporary_catalog({"TILED_SAVE_PATH": str(bad)})
