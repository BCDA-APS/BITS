"""
Test the utils.stored_dict module.
"""

import copy
import pathlib
import tempfile
import time
from contextlib import nullcontext as does_not_raise

import pytest

from apsbits.utils.config_loaders import load_config_yaml
from apsbits.utils.stored_dict import StoredDict


def luftpause(delay=0.05):
    """A brief wait for content to flush to storage."""
    time.sleep(max(0, delay))


@pytest.fixture
def md_file():
    """Provide a temporary file (deleted on close)."""
    tfile = tempfile.NamedTemporaryFile(
        prefix="re_md_",
        suffix=".yml",
        delete=False,
    )
    path = pathlib.Path(tfile.name)
    yield pathlib.Path(tfile.name)

    if path.exists():
        path.unlink()  # delete the file


def test_StoredDict(md_file):
    """Test the StoredDict class."""
    assert md_file.exists()
    assert len(open(md_file).read().splitlines()) == 0  # empty

    sdict = StoredDict(md_file, delay=0.2, title="unit testing")
    assert sdict is not None
    assert len(sdict) == 0
    assert sdict._delay == 0.2
    assert sdict._title == "unit testing"
    assert len(open(md_file).read().splitlines()) == 0  # still empty
    assert sdict._sync_key == f"sync_agent_{id(sdict):x}"
    assert not sdict.sync_in_progress

    # Write an empty dictionary.
    sdict.flush()
    luftpause()
    buf = open(md_file).read().splitlines()
    assert len(buf) == 4, f"{buf=}"
    assert buf[-1] == "{}"  # The empty dict.
    assert buf[0].startswith("# ")
    assert buf[1].startswith("# ")
    assert "unit testing" in buf[0]

    # Add a new {key: value} pair.
    assert not sdict.sync_in_progress
    sdict["a"] = 1
    assert sdict.sync_in_progress
    sdict.flush()
    assert time.time() >= sdict._sync_deadline
    luftpause()
    assert not sdict.sync_in_progress
    assert len(open(md_file).read().splitlines()) == 4

    # Change the only value.
    sdict["a"] = 2
    sdict.flush()
    luftpause()
    assert len(open(md_file).read().splitlines()) == 4  # Still.

    # Add another key.
    sdict["bee"] = "bumble"
    sdict.flush()
    print(f"\n\nthis is the md_file: {md_file}\n\n")
    luftpause()
    assert len(open(md_file).read().splitlines()) == 5

    # Test _delayed_sync_to_storage.
    sdict["bee"] = "queen"
    md = load_config_yaml(md_file)
    assert len(md) == 2  # a & bee
    assert "a" in md
    assert md["bee"] == "bumble"  # The old value.

    time.sleep(sdict._delay / 2)
    # Still not written ...
    assert load_config_yaml(md_file)["bee"] == "bumble"

    time.sleep(sdict._delay)
    # Should be written by now.
    assert load_config_yaml(md_file)["bee"] == "queen"

    del sdict["bee"]  # __delitem__
    assert "bee" not in sdict  # __getitem__
    sdict.flush()  # cancel the debounce timer scheduled by the deletion (S4)


@pytest.mark.parametrize(
    "md, xcept, text",
    [
        [{"a": 1}, None, str(None)],  # int value is ok
        [{"a": 2.2}, None, str(None)],  # float value is ok
        [{"a": "3"}, None, str(None)],  # str value is ok
        [{"a": [4, 5, 6]}, None, str(None)],  # list value is ok
        [{"a": {"bb": [4, 5, 6]}}, None, str(None)],  # nested value is ok
        [{1: 1}, None, str(None)],  # int key is ok
        [{"a": object()}, TypeError, "not JSON serializable"],
        [{object(): 1}, TypeError, "keys must be str, int, float, "],
        [{"a": [4, object(), 6]}, TypeError, "not JSON serializable"],
        [{"a": {object(): [4, 5, 6]}}, TypeError, "keys must be str, int, "],
    ],
)
def test_set_exceptions(md, xcept, text, md_file):
    """Cases that might raise an exception."""
    sdict = StoredDict(md_file, delay=0.2, title="unit testing")
    context = does_not_raise() if xcept is None else pytest.raises(xcept)
    with context as reason:
        sdict.update(md)
    assert text in str(reason), f"{reason=}"


def test_popitem(md_file):
    """Can't popitem from empty dict."""
    sdict = StoredDict(md_file, delay=0.2, title="unit testing")
    with pytest.raises(KeyError) as reason:
        sdict.popitem()
    assert "dictionary is empty" in str(reason), f"{reason=}"


def test_flush_durable_during_sync(md_file):
    """flush() must write even while a debounce sync is still pending (B9)."""
    # A long delay guarantees the debounce timer will not fire on its own
    # during the test, so the only path to disk is flush().
    sdict = StoredDict(md_file, delay=30, title="unit testing")
    sdict["a"] = 1
    assert sdict.sync_in_progress  # timer scheduled, not yet fired
    assert open(md_file).read().strip() == ""  # nothing on disk yet

    sdict.flush()

    assert not sdict.sync_in_progress
    # Before B9, flush() short-circuited while sync_in_progress and lost this.
    assert load_config_yaml(md_file) == {"a": 1}


def test_deletion_persisted(md_file):
    """__delitem__ and popitem schedule a durable write (S4)."""
    sdict = StoredDict(md_file, delay=0.1, title="unit testing")
    sdict.update({"a": 1, "bee": 2})
    sdict.flush()
    assert load_config_yaml(md_file) == {"a": 1, "bee": 2}

    # __delitem__ persists the removal with no explicit flush.
    del sdict["a"]
    luftpause(0.3)  # let the debounce timer (delay=0.1) fire
    assert load_config_yaml(md_file) == {"bee": 2}

    # popitem persists the removal too.
    sdict.popitem()
    luftpause(0.3)
    assert load_config_yaml(md_file) == {}


def test_deepcopy(md_file):
    """StoredDict must survive copy.deepcopy.

    ``RE.md`` is a StoredDict and bluesky deep-copies the RunEngine metadata
    during a run; the transient lock/timer would otherwise raise
    ``TypeError: cannot pickle '_thread.RLock'``.
    """
    sdict = StoredDict(md_file, delay=0.2, title="unit testing")
    sdict["a"] = 1
    sdict["b"] = {"nested": [1, 2, 3]}

    clone = copy.deepcopy(sdict)

    assert dict(clone) == {"a": 1, "b": {"nested": [1, 2, 3]}}
    assert clone._cache is not sdict._cache  # deep copy, not shared
    assert clone._cache["b"] is not sdict._cache["b"]
    assert clone._lock is not sdict._lock  # fresh transient primitives
    assert clone._sync_timer is None
    assert not clone.sync_in_progress


def test_repr(md_file):
    """__repr__"""
    sdict = StoredDict(md_file, delay=0.1, title="unit testing")
    sdict["a"] = 1
    assert repr(sdict) == "<StoredDict {'a': 1}>"
    assert str(sdict) == "<StoredDict {'a': 1}>"
