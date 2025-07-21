# tiled

APS local tiled data server template: databroker catalog

- [tiled](#tiled)
  - [Overview](#overview)
  - [Startup](#startup)
    - [Features](#features)
      - [Additional file content served](#additional-file-content-served)
  - [File Directories](#file-directories)
    - [Indexing](#indexing)
    - [Serve the catalog file](#serve-the-catalog-file)
    - [Index the directory into the catalog file](#index-the-directory-into-the-catalog-file)
      - [Custom file types](#custom-file-types)
    - [Start tiled server with directory HDF5 files](#start-tiled-server-with-directory-hdf5-files)
  - [Links](#links)
  - [Install](#install)
  - [Files](#files)
    - [bluesky.yml](#blueskyyml)

## Overview

Run the *tiled* data server locally on workstation `SERVER`.  Since this server
provides open access, it is only accessible within the APS firewall.

- [x] databroker/MongoDB catalogs
- [x] file directories
- [ ] Authentication

## Startup

To start this tiled server (after configuring as described in the
[Install](#install} section), navigate to this directory and run the server
within a [screen](https://www.man7.org/linux/man-pages/man1/screen.1.html)
session:

```bash
in-screen.sh
```

<details>
<summary>Tutorial: screen</summary>

See also: https://www.hostinger.com/tutorials/how-to-install-and-use-linux-screen/

</details>

Then, use any web browser (within the APS firewall) to visit URL:
`http://SERVER:8000`.

The web interface is a simple (simplistic yet informative) User Interface
demonstrating many features of the tiled server and also providing access to
online documentation. Visit the documentation to learn how to build your own
interface to tiled.

### Features

- serve data from Bluesky databroker catalogs
- (optional) serve data from user experiment file directory

#### Additional file content served

- [x] Identify NeXus/HDF5 files with arbitrary names.
- [x] Identify SPEC data files with arbitrary names and read them.
- [x] Read `.jpg` (and other image format) files.
- [x] Read the [synApps MDA format](https://github.com/epics-modules/sscan/blob/master/documentation/saveData_fileFormat.txt) ([Python support](https://github.com/EPICS-synApps/utils/blob/master/mdaPythonUtils/INSTALL.md))
- [x] Write a custom data file identifier.
- [x] Write a custom data file loader.
- [x] Learn how to ignore files such as `.xml` (without startup comments).

## File Directories

Since tiled tag 0.1.0a104, serving a directory of files from tiled has become a
two-step process:

1. Index the directory of files (into a SQLite file).
2. Serve the directory based on the index file.

### Indexing

Each tiled *tree* of a file directory, needs its own index.  The index is a
local SQLite database file, (a.k.a., a *catalog*) that contains metadata
collected from each of the files and subdirectories for this tree.

### Serve the catalog file

Serve the catalog file.  The name of this file can be anything (permissable by
the OS).  To be consistent with the *tiled* documentation, we'll use
`catalog.db` for these examples.  This is a one-time command, unless you wish to
remove any existing content from this SQL database.

```bash
tiled catalog init catalog.db
```

### Index the directory into the catalog file

Index the entire directory (and any subdirectories).  This example walks through
the (local) `.dev_data/hdf` directory and indexes any files already recognized
by tiled.  Also, it recognizes any files with suffixes `.nx5` and `.nexus.hdf5`
as HDF5.  *tiled* already handles HDF5 as a file type, so no additional code is
required to parse and provide that content.

```bash
tiled catalog register catalog.db \
   --verbose \
   --ext '.nx5=application/x-hdf5' \
   --ext '.nexus.hdf5=application/x-hdf5' \
   ./dev_data/hdf5
```

#### Custom file types

The `config.yml.template` has examples for custom file types.  The command to
index changes.  First, it is necessary to add the `*.py` files in this
directory, by prefixing the command with an environment definition for just this
command: `PYTHONPATH=. tiled catalog register ...`

Next, add `--ext` options for each file suffix to be recognized.  The
`--mimetype-hook` option identifies the local code to associate mimetypes with
any other unrecognized files.  (For example, SPEC data files are text and may
not even have a common file suffix.)  The `--adapter` lines define the local
custom code associated with each additional mimetype.

Here's an example for the custom handlers in this repository.  Note this example
uses the `./dev_data/` directory, so the `catalog.db` must first be
[recreated](#serve-the-catalog-file).

```bash
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
```

### Start tiled server with directory HDF5 files

If there is only one catalog (this catalog of directories) to be served by
tiled, then start the server (with this `command.db` file and `./dev_data/hdf5/`
directory) from the command line, such as:

```bash
   tiled serve catalog catalog.db -r ./dev_data/hdf5/ --host 0.0.0.0  --public
```

To run a tiled server for multiple catalogs, use a `config.yml` file.  To
configure tiled for this example directory of HDF5 files, add this to the
`config.yml` file:

```yaml
   - path: HDF5-files
      tree: tiled.catalog:from_uri
      args:
      uri: ./catalog.db
      readable_storage:
         - ./dev_data/hdf5
```

then start the *tiled* server with `./start-tiled.sh` or similar.

## Links

- <https://github.com/bluesky/tiled/issues/175>
- <https://blueskyproject.io/tiled/how-to/read-custom-formats.html#case-2-no-file-extension>
- `screen` tutorial: See also: https://www.hostinger.com/tutorials/how-to-install-and-use-linux-screen/

## Install

1. Setup and activate a custom conda environment as directed
   in [`environment.yml`](./environment.yml).

   Note: This step defines a `CONDA_PREFIX` environment variable in the bash shell.  Used below.
2. tiled's configuration file: `config.yml`:
   1. Copy the template file `config.yml.template` to `config.yml`
   2. `path` is the name that will be seen by the tiled clients.
   3. `tree` should not be changed
   4. for databroker catalogs, `uri` is the address
      of the mongodb catalog for this `path`
   5. for file directories, `directory` is the path to
      the directory.  Either absolute or relative to the
      directory of this README.md file.
   6. Uncomment and edit the second catalog (`tree: databroker `...),
      copy and edit if more catalogs are to be served.
   7. Uncomment and edit the file directory (`tree: files`)
      if you wish tomake a file directory available.
3. Edit bash starter shell script file [`start-tiled.sh`](./start-tiled.sh)
   1. Override definition of `MY_DIR` at your choice.
   2. (optional) Activate the micromamba/conda environment (if not done
      in step 1 above).  You may need to change the definition of
      `CONDA_ENV` which is the name of the conda environment to use.
   3. (optional) Change the `HOST` and `PORT` if needed.
   4. (optional) Remove the `--public` option if you want to require an
      authentication token (shown on the console at startup of tiled).
4. Edit web interface to display additional columns:
   1. In the `$CONDA_PREFIX` directory, edit file
      `share/tiled/ui/config/bluesky.yml` so it has the
      content indicated by the [`bluesky.yml`](#blueskyyml)
      below.
   2. Edit file `share/tiled/ui/configuration_manifest.yml` and
      add a line at the bottom to include the `bluesky.yml` file:

      ```yml
        - config/bluesky.yml
      ```

## Files

### bluesky.yml

```yml
specs:
  - spec: CatalogOfBlueskyRuns
    columns:
      - header: Bluesky Plan
        select_metadata: start.plan_name
        field: plan_name
      - header: Scan ID
        select_metadata: start.scan_id
        field: scan_id
      - header: Time
        select_metadata: start.time
        field: start_time
    default_columns:
      - plan_name
      - scan_id
      - start_time
```
