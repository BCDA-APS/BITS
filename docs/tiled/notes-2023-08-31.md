# NOTES with new tiled a105

terse notes collected from conversation 2023-08-31

```bash
    tiled catalog init catalog.db
    tiled catalog register catalog.db \
        --verbose \
        --ext '.nx5=application/x-hdf5' \
        --ext '.nexus.hdf5=application/x-hdf5' \
        ./dev_data/hdf5
    tiled serve catalog catalog.db -r ./dev_data/hdf5/ --host 0.0.0.0  --public
```


```bash
    tiled catalog init catalog.db
    PYTHONPATH=. \
        tiled catalog register \
        catalog.db \
        --verbose \
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
        ./dev_data
    tiled serve catalog catalog.db -r ./dev_data/ --host 0.0.0.0  --public
```

