"""Read the SPEC data file format."""

import datetime
import os

import numpy
from spec2nexus import spec
from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
from tiled.structures.core import Spec as TiledSpec

EXTENSIONS = []  # no uniform standard exists, many common patterns
MIMETYPE = "text/x-spec_data"
SPEC_FILE_SPECIFICATION = TiledSpec("SPEC_file", version="1.0")
SPEC_SCAN_SPECIFICATION = TiledSpec("SPEC_scan", version="1.0")


def has(parent, attr):
    """Cautious alternative to hasattr()."""
    if attr in dir(parent):
        obj = getattr(parent, attr)
        return obj is not None
    return False



def read_diffractometer_metadata(diffractometer):
    # special cases
    simple_attrs = """
        UB
        geometry_name
        geometry_name_full
        mode
        sector
        variant
        wavelength
    """.split()
    # fmt: off
    md = {
        k: getattr(diffractometer, k)
        for k in simple_attrs
        if has(diffractometer, k)
    }

    if has(diffractometer, "reflections"):
        md["reflections"] = {
            f"R{r}": refl._asdict()
            for r, refl in enumerate(diffractometer.reflections)
        }
    if has(diffractometer, "geometry_parameters"):
        md["geometry_parameters"] = {
            k: dict(
                key=v.key,
                description=v.description,
                value=v.value,
            )
            for k, v in diffractometer.geometry_parameters.items()
        }
    if has(diffractometer, "lattice"):
        md["lattice"] = diffractometer.lattice._asdict()
    # fmt: on
    return md


def read_spec_scan(scan):
    try:
        arrays = {
            k: ArrayAdapter.from_array(numpy.array(v))
            # TODO: xref name as metadata?
            for k, v in scan.data.items()
        }
        # fmt: off
        attrs = """
            G L M S
            column_first column_last
            date epoch metadata positioner
            scanCmd scanNum time_name
        """.split()
        md = {
            k: getattr(scan, k)
            for k in attrs
            if has(scan, k)
        }
        if has(scan, "diffractometer"):
            md.update(read_diffractometer_metadata(scan.diffractometer))
        # fmt: on
    except ValueError as exc:
        arrays = {}
        md = dict(ValueError=exc, disposition="skipping")
    return MapAdapter(arrays, metadata=md, specs=[SPEC_SCAN_SPECIFICATION])


def read_spec_data(filename, **kwargs):
    # kwargs has metadata known to the tiled database
    if not spec.is_spec_file_with_header(filename):
        raise spec.NotASpecDataFile(str(filename))
    sdf = spec.SpecDataFile(str(filename))
    md = dict(
        fileName=str(sdf.fileName),
        specFile=str(sdf.specFile),
    )
    # header metadata  (sdf.headers is a list)
    if has(sdf, "headers") and len(sdf.headers) > 0:
        md["headers"] = {}
        for h, header in enumerate(sdf.headers, start=1):
            h_md = md["headers"][f"H{h}"] = {}
            for key in "date epoch counter_xref positioner_xref".split():
                if has(header, key):
                    h_md[key] = getattr(header, key)
            if has(header, "file"):
                h_md["file"] = str(header.file)
            if has(header, "epoch"):
                h_md["iso8601"] = f"{datetime.datetime.fromtimestamp(header.epoch)}"
            if has(header, "comments") and len(header.comments) > 0:
                h_md["comments"] = {
                    f"C{c}": comment
                    for c, comment in enumerate(header.comments, start=1)
                }

    # fmt: off
    return MapAdapter(
        {
            f"S{scan_number}": read_spec_scan(scan)
            for scan_number, scan in sdf.scans.items()
        },
        metadata=md,
        specs=[SPEC_FILE_SPECIFICATION]
    )
    # fmt: on


def developer():
    import pathlib

    # spec2nexus_data_path = (
    #     pathlib.Path().home()
    #     / "Documents"
    #     / "projects"
    #     / "prjemian"
    #     / "spec2nexus"
    #     / "src"
    #     / "spec2nexus"
    #     / "data"
    # )
    test_data_path = pathlib.Path(__file__).parent / "data"
    # sixc_data_path = test_data_path / "diffractometer" / "sixc"
    usaxs_data_path = test_data_path / "usaxs" / "2019"
    path = usaxs_data_path
    for filename in sorted(path.iterdir()):
        print(f"{filename.name=}")
        if not os.path.isfile(filename):
            continue
        try:
            structure = read_spec_data(filename)
            print(f"{structure}")
        except spec.NotASpecDataFile:
            pass


if __name__ == "__main__":
    developer()
