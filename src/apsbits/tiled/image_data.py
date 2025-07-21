"""
Read a variety of image file formats as input for tiled.
"""

import os
import pathlib

import numpy
import yaml
from PIL import Image
from PIL.TiffImagePlugin import IFDRational
from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
from tiled.structures.core import Spec as TiledSpec

from ignore_data import IGNORE_SPECIFICATION

ROOT = pathlib.Path(__file__).parent

EXTENSIONS = []
# https://mimetype.io/all-types#image
MIMETYPES = """
    image/bmp
    image/gif
    image/jpeg
    image/png
    image/tiff
    image/vnd.microsoft.icon
    image/webp
""".split()
# TODO:     image/avif  not handled by PIL
# TODO:     image/svg+xml  not handled by PIL

EMPTY_ARRAY = numpy.array([0, 0])
IMAGE_FILE_SPECIFICATION = TiledSpec("image_file", version="1.0")


def interpret_IFDRational(data):
    if not isinstance(data, IFDRational):
        raise TypeError(f"{data} is not of type {IFDRational.__class__}")
    attrs = "numerator denominator imag".split()
    md = {k: getattr(data, k) for k in attrs}
    md["real"] = float(data.numerator) / data.denominator
    return md


def interpret_exif(image):
    from PIL.ExifTags import TAGS

    exif = image.getexif()
    md = {}
    for tag_id in exif:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exif.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        if isinstance(data, IFDRational):
            data = interpret_IFDRational(data)
        md[tag] = data
    return md


def image_metadata(image):
    attrs = """
        bits
        filename
        format
        format_description
        is_animated
        layer
        layers
        mode
        n_frames
        size
        text
    """.split()
    md = {k: getattr(image, k) for k in attrs if hasattr(image, k)}

    if len(image.info) > 0:
        md["info"] = {}
        md["info"].update(image.info)
    info = md.get("info")
    if info is not None:
        for k in "exif icc_profile xmp".split():
            if k in info:
                info.pop(k)
        for k in "dpi resolution".split():
            # fmt: off
            if k in info:
                items = []
                for data in info[k]:
                    if isinstance(data, IFDRational):
                        v = interpret_IFDRational(data)
                    else:
                        v = data
                    items.append(v)
                info[k] = tuple(items)
            # fmt: on
        value = info.get("version")
        if isinstance(value, bytes):
            info["version"] = value.decode()
        value = info.get("extension")
        if isinstance(value, tuple) and isinstance(value[0], bytes):
            info["extension"] = (value[0].decode(), value[1])

    # print(yaml.dump(md))

    exif = interpret_exif(image)
    if len(exif) > 0:
        md["exif"] = exif

    md["extrema"] = image.getextrema()

    return md


def read_image(filename, **kwargs):
    fn = pathlib.Path(filename).name
    try:
        if not os.path.isfile(filename):
            raise TypeError(f"'{filename}' is not a file.")
        image = Image.open(filename)
        md = image_metadata(image)

        # # special cases
        # if image.format == "AVIF":
        #     pass

        im = image.getdata()
        pixels = list(im)  # 1-D array of int or tuple
        shape = list(reversed(im.size))
        if im.bands > 1:
            shape.append(im.bands)
        pixels = numpy.array(pixels).reshape(shape)
        if len(shape) > 2:
            pixels = numpy.moveaxis(pixels, -1, 0)  # put the colors first
        return ArrayAdapter.from_array(
            pixels, metadata=md, specs=[IMAGE_FILE_SPECIFICATION]
        )

    except Exception as exc:
        arrays = dict(
            ignore=ArrayAdapter.from_array(
                numpy.array([0, 0]),
                metadata=dict(ignore="placeholder, ignore"),
                specs=[IGNORE_SPECIFICATION],
            )
        )
        return MapAdapter(
            arrays,
            metadata=dict(
                filename=str(filename),
                exception=exc,
                purpose="some problem reading this file as an image",
                specs=[IGNORE_SPECIFICATION],
            ),
        )


def main():
    testdir = ROOT / "data" / "usaxs" / "2021"
    for filepath in testdir.iterdir():
        read_image(filepath)

    testdir = ROOT / "data" / "images"
    for filepath in testdir.iterdir():
        read_image(filepath)


if __name__ == "__main__":
    main()
