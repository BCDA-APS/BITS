"""
Tests for the import side-effect fixes.

Covers:
- BSDEV logging level idempotency (configure_logging called twice)
- Specwriter/file_extension guards (calling before init raises RuntimeError)
- Metadata caching (_collect_metadata computed once, cached thereafter)
"""

import logging

import pytest


class TestBsdevIdempotency:
    """Test that configure_logging() can be called multiple times safely."""

    def test_configure_logging_twice_no_crash(self):
        """Calling configure_logging() twice must not raise AttributeError."""
        from apsbits.utils.logging_setup import configure_logging

        # First call registers BSDEV
        configure_logging()
        assert hasattr(logging, "BSDEV")

        # Second call must not crash (idempotency guard)
        configure_logging()
        assert hasattr(logging, "BSDEV")

    def test_bsdev_level_registered_after_configure(self):
        """BSDEV level should be available after configure_logging()."""
        from apsbits.utils.logging_setup import configure_logging

        configure_logging()
        assert hasattr(logging, "BSDEV")
        assert logging.BSDEV == logging.INFO - 5


class TestSpecwriterGuards:
    """Test that specwriter functions raise RuntimeError before init."""

    def test_spec_comment_before_init(self):
        """spec_comment() before init_specwriter_with_RE() raises RuntimeError."""
        # Reset module state
        import apsbits.demo_instrument.callbacks.demo_spec_callback as mod

        mod.specwriter = None
        mod.file_extension = None

        with pytest.raises(RuntimeError, match="init_specwriter_with_RE"):
            mod.spec_comment("test comment")

    def test_new_spec_file_before_init(self):
        """newSpecFile() before init_specwriter_with_RE() raises RuntimeError."""
        import apsbits.demo_instrument.callbacks.demo_spec_callback as mod

        mod.specwriter = None
        mod.file_extension = None

        with pytest.raises(RuntimeError, match="init_specwriter_with_RE"):
            mod.newSpecFile("test")


class TestMetadataCaching:
    """Test that _collect_metadata() caches its result."""

    def test_collect_metadata_returns_same_object(self):
        """Second call to _collect_metadata() returns the cached object."""
        # Reset cache
        import apsbits.utils.metadata as mod
        from apsbits.utils.metadata import _collect_metadata

        mod._cached_metadata = None

        first = _collect_metadata()
        second = _collect_metadata()
        assert first is second

    def test_collect_metadata_has_expected_keys(self):
        """_collect_metadata() returns dict with hostname, username, versions."""
        import apsbits.utils.metadata as mod
        from apsbits.utils.metadata import _collect_metadata

        mod._cached_metadata = None

        result = _collect_metadata()
        assert "hostname" in result
        assert "username" in result
        assert "versions" in result
        assert isinstance(result["versions"], dict)
