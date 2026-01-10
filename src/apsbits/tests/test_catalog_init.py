"""Test the catalog_init module."""

from contextlib import nullcontext as does_not_raise
from unittest.mock import patch

import pytest
from tiled.profiles import ProfileNotFound

# Run these tests without running startup.py.
with patch("logging.Logger.bsdev"):
    # from apsbits.core.catalog_init import _tiled_temporary_catalog
    from apsbits.core.catalog_init import _databroker_named_catalog
    from apsbits.core.catalog_init import _databroker_temporary_catalog
    from apsbits.core.catalog_init import _tiled_profile_client
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
        # TODO: pytest.param(
        #     {},
        #     _tiled_temporary_catalog,
        #     does_not_raise(),
        #     id="temporary tiled catalog",
        # ),
    ],
)
def test_handlers(iconfig, handler, cat_type, context):
    """Test the handlers that create 'cat' onbjects."""
    with context:
        cat = handler(iconfig)
        assert type(cat).__name__ == cat_type
