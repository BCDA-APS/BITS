import numpy
from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
from tiled.structures.core import Spec as TiledSpec

IGNORE_SPECIFICATION = TiledSpec("ignore", version="1.0")


def read_ignore(filename, **kwargs):
    arrays = dict(
        ignore=ArrayAdapter.from_array(
            numpy.array([0, 0]),
            metadata=dict(ignore="placeholder, ignore"),
            specs=[IGNORE_SPECIFICATION],
        )
    )
    return MapAdapter(
        arrays,
        metadata=dict(filename=str(filename), purpose="ignore this file's contents"),
        specs=[IGNORE_SPECIFICATION],
    )
