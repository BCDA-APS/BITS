"""Storage-backed Dictionary
=========================

A dictionary that writes its contents to a YAML file. This mutable mapping automatically
synchronizes its in-memory state to a human-readable YAML file on disk shortly after
updates. It replaces ``bluesky.utils.PersistentDict`` and
ensures that all contents are JSON serializable.

.. autosummary::
    ~StoredDict
"""

__all__ = ["StoredDict"]

import collections.abc
import datetime
import inspect
import json
import logging
import pathlib
import threading
import time
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import yaml

logger = logging.getLogger(__name__)


class StoredDict(collections.abc.MutableMapping):
    """
    Dictionary that synchronizes its contents to a YAML storage file.

    This mutable mapping stores key-value pairs in an internal cache and
    periodically writes its contents to a YAML file on disk. Changes are
    flushed after a configurable delay. The YAML serialization and
    deserialization are handled by the static methods `dump` and `load`.

    """

    def __init__(
        self,
        file: Union[str, pathlib.Path],
        delay: float = 5,
        title: Optional[str] = None,
        serializable: bool = True,
    ) -> None:
        """
        Initialize the StoredDict instance.

        Args:
            file (str or pathlib.Path): Path to the YAML file for storing dictionary
            contents.
            delay (float): Time delay in seconds after the last update before
            synchronizing to storage. Defaults to 5 seconds.
            title (str, optional): Comment to include at the top of the YAML file.
            If not provided, defaults to "Written by StoredDict.".
            serializable (bool): If True, ensure that new dictionary entries
            are JSON serializable.

        Returns:
            None
        """
        self._file: pathlib.Path = pathlib.Path(file)
        self._delay: float = max(0, delay)
        self._title: str = title or f"Written by {self.__class__.__name__}."
        self.test_serializable: bool = serializable
        self.sync_in_progress: bool = False
        self._sync_deadline: float = time.time()
        self._sync_key: str = f"sync_agent_{id(self):x}"
        self._sync_loop_period: float = 0.005

        self._cache: Dict[Any, Any] = {}
        self.reload()

    def __delitem__(self, key: Any) -> None:
        """
        Delete an item from the dictionary by its key.

        Args:
            key (Any): The key of the item to delete.

        Raises:
            KeyError: If the key does not exist in the dictionary.
        """
        del self._cache[key]

    def __getitem__(self, key: Any) -> Any:
        """
        Retrieve the value associated with the given key.

        Args:
            key (Any): The key to retrieve.

        Returns:
            Any: The value corresponding to the specified key.
        """
        return self._cache[key]

    def __iter__(self):
        """Iterate over the dictionary keys."""
        yield from self._cache

    def __len__(self):
        """Number of keys in the dictionary."""
        return len(self._cache)

    def __repr__(self):
        """representation of this object."""
        return f"<{self.__class__.__name__} {dict(self)!r}>"

    def __setitem__(self, key, value):
        """Write to the dictionary."""
        outermost_frame = inspect.getouterframes(inspect.currentframe())[-1]
        if "sphinx-build" in outermost_frame.filename:
            # Seems that Sphinx is building the documentation.
            # Ignore all the objects it tries to add.
            return

        if self.test_serializable:
            json.dumps({key: value})
        self._cache[key] = value  # Store the new (or revised) content.

        # Reset the deadline.
        self._sync_deadline = time.time() + self._delay
        logger.debug("new sync deadline in %f s.", self._delay)
        if not self.sync_in_progress:
            # Start the sync_agent (thread).
            self._delayed_sync_to_storage()

    def _delayed_sync_to_storage(self):
        """
        Sync the metadata to storage.
        Start a time-delay thread.  New writes to the metadata dictionary will
        extend the deadline.  Sync once the deadline is reached.
        """

        def sync_agent():
            """Threaded task."""
            logger.debug("Starting sync_agent...")
            self.sync_in_progress = True
            while time.time() < self._sync_deadline:
                time.sleep(self._sync_loop_period)
            logger.debug("Sync waiting period ended")
            self.sync_in_progress = False

            StoredDict.dump(self._file, self._cache, title=self._title)

        thred = threading.Thread(target=sync_agent)
        thred.start()

    def flush(self):
        """Force a write of the dictionary to disk"""
        logger.debug("flush()")
        if not self.sync_in_progress:
            StoredDict.dump(self._file, self._cache, title=self._title)
        self._sync_deadline = time.time()
        self.sync_in_progress = False

    def popitem(self):
        """
        Remove and return a (key, value) pair as a 2-tuple.

        Raises:
            KeyError: If the dictionary is empty.
        """
        return self._cache.popitem()

    def reload(self):
        """Read dictionary from storage."""
        logger.debug("reload()")
        self._cache = StoredDict.load(self._file)

    @staticmethod
    def dump(file, contents, title=None):
        """Write dictionary to YAML file."""
        logger.debug("_dump(): file='%s', contents=%r, title=%r", file, contents, title)
        with open(file, "w") as f:
            if isinstance(title, str) and len(title) > 0:
                f.write(f"# {title}\n")
            f.write(f"# Dictionary contents written: {datetime.datetime.now()}\n\n")
            f.write(yaml.dump(contents, indent=2))

    @staticmethod
    def load(file):
        """Read dictionary from YAML file."""
        from apsbits.utils.config_loaders import load_config_yaml

        file = pathlib.Path(file)
        logger.debug("_load('%s')", file)
        md: Optional[Dict[Any, Any]] = None
        if file.exists():
            md = load_config_yaml(file)
        return md or {}
