#!/bin/bash

# re-create the SQLite catalog for the ./dev_sampler/ directory

#  ./recreate_sampler.sh 2>&1 | tee recreate.log

SQL_CATALOG=dev_sampler.sql
FILE_DIR=./dev_sampler

echo "Deleting '${SQL_CATALOG}', if it exists."
/bin/rm -f "${SQL_CATALOG}"

echo "Creating '${SQL_CATALOG}' for directory '${FILE_DIR}'."
tiled catalog init "${SQL_CATALOG}"

PYTHONPATH=. \
    tiled catalog register \
    "${SQL_CATALOG}" \
    -vvv \
    --keep-ext \
    --ext '.avif=image/avif' \
    --ext '.dat=text/x-spec_data' \
    --ext '.docx=application/octet-stream' \
    --ext '.DS_Store=text/plain' \
    --ext '.h5=application/x-hdf5' \
    --ext '.hdf=application/x-hdf5' \
    --ext '.mda=application/x-mda' \
    --ext '.nexus.hdf5=application/x-hdf5' \
    --ext '.nx5=application/x-hdf5' \
    --ext '.pptx=application/octet-stream' \
    --ext '.pyc=application/octet-stream' \
    --ext '.spc=text/x-spec_data' \
    --ext '.spe=text/x-spec_data' \
    --ext '.spec=text/x-spec_data' \
    --ext '.webp=image/webp' \
    --mimetype-hook 'custom:detect_mimetype' \
    --adapter 'application/json=ignore_data:read_ignore' \
    --adapter 'application/octet-stream=ignore_data:read_ignore' \
    --adapter 'application/x-mda=synApps_mda:read_mda' \
    --adapter 'application/xop+xml=ignore_data:read_ignore' \
    --adapter 'application/zip=ignore_data:read_ignore' \
    --adapter 'image/avif=ignore_data:read_ignore' \
    --adapter 'image/bmp=image_data:read_image' \
    --adapter 'image/gif=image_data:read_image' \
    --adapter 'image/jpeg=image_data:read_image' \
    --adapter 'image/png=image_data:read_image' \
    --adapter 'image/svg+xml=ignore_data:read_ignore' \
    --adapter 'image/tiff=image_data:read_image' \
    --adapter 'image/vnd.microsoft.icon=image_data:read_image' \
    --adapter 'image/webp=image_data:read_image' \
    --adapter 'image/x-ms-bmp=image_data:read_image' \
    --adapter 'text/markdown=ignore_data:read_ignore' \
    --adapter 'text/plain=ignore_data:read_ignore' \
    --adapter 'text/x-python=ignore_data:read_ignore' \
    --adapter 'text/x-spec_data=spec_data:read_spec_data' \
    --adapter 'text/xml=ignore_data:read_ignore' \
    "${FILE_DIR}"
