# Guide to Creating a `tiled` Server

There are a few steps to create a `tiled` server for bluesky data.

Jan Ilavsky has created an [article](https://github.com/jilavsky/SAXS_IgorCode/wiki/Reading-data-from-Tiled-server)
about reading data from such a server.

CONTENTS

- [Guide to Creating a `tiled` Server](#guide-to-creating-a-tiled-server)
  - [Download the template](#download-the-template)
  - [Create conda environment](#create-conda-environment)
  - [Configure](#configure)
    - [`config.yml`](#configyml)
      - [databroker catalogs](#databroker-catalogs)
      - [EPICS Area Detector data files](#epics-area-detector-data-files)
      - [local data files](#local-data-files)
  - [Run the server](#run-the-server)
  - [Enable auto (re)start](#enable-auto-restart)
  - [Clients](#clients)

## Download the template

The download steps must be done on a workstation that can reach the public
network.  Use the same account that will be used to run the tiled server.

The tiled server should run on a workstation that has access to the controls
subnet and any relevant filesystems with data to be served.

```bash
cd your/projects/directory
git clone https://github.com/BCDA-APS/tiled-template ./tiled-server
cd ./tiled-server
```

TODO: What about changing the cloned repo origin?

## Create conda environment

```bash
conda env create --force -n tiled -f environment.yml --solver=libmamba
conda activate tiled
```

This may install a few hundred packages, including databroker v2+.

<details>
<summary>Might seem slow...</summary>

In a networked scenario like the APS, with many filesystems provided by NFS
exports and file backup & cache automation, processes that write many files to
NFS filesystems (such as creating a conda environment) may be very slow.  It
could take 5-10 minutes to create this conda environment.  Compare with the
procedures for creating a [conda environment for bluesky
operations](https://bcda-aps.github.io/bluesky_training/reference/_create_conda_env.html).
Many of the same advisories apply here, too.

</details>

## Configure

### `config.yml`

Create your tiled configuration file from the template provided.

```bash
cp config.yml.template config.yml
```

Keep in mind, YAML, like Python uses indentation as syntax.

#### databroker catalogs

Edit `config.yml` for your databroker catalog information:

- `path`: name of this catalog (use this name from your bluesky sessions); can be found in:
  - `bluesky/instrument/iconfig.yml`
  - catalog name is at the end of line ~8: `DATABROKER_CATALOG: &databroker_catalog some_catalog_name`
- `uri` : address of your MongoDB catalog; in `mongodb://DB_SERVER.xray.aps.anl.gov:27017/45id_instrument-bluesky` replace:
  - `DB_SERVER` with `db_host_name` (can be found in 2nd column of [APS list table](https://github.com/BCDA-APS/bluesky_training/wiki))
  - `45id_instrument` with `catalog_name`
- In line 4 `http://SERVER.xray.aps.anl.gov:8020/`:
  - replace `SERVER` with the host name (computer running the tiled server)
  - make sure the port number is consistent with the `./start-tiled.sh` script

WARNING: consider whether you want this information publicly available or not (i.e. host tiled repo on aps gitlab or github)
  
Repeat this block if you have more than one catalog to be served (such as
retired catalogs).  A comment section of the template shows how to add addtional
catalogs.

<details>

Sharp-eyed observers will note that the databroker configuration details specified for tiled are different than the ones they have been using with databroker v1.2.
The config for tiled uses the same info but in databroker v2 format.

databroker v1.2 format

```yaml
  example:
    args:
      asset_registry_db: mongodb://mymongoserver.localdomain:27017/example
      metadatastore_db: mongodb://mymongoserver.localdomain:27017/example
    driver: bluesky-mongo-normalized-catalog
```

same content in tiled format

```yaml
  - path: example
    tree: databroker.mongo_normalized:Tree.from_uri
    args:
      uri: mongodb://mymongoserver.localdomain:27017/example
```

Why the change?  databroker is moving away from the intake library (the one that
reads the v1.2 format).  `intake` seems to be slow to load (you see that when
importing databroker v1.2).  New databroker v2 does not use intake.  And is
faster to import.  (Other improvements under the hood.)

</details>

#### EPICS Area Detector data files

If your files are written by EPICS area detector during bluesky runs, you do not
need to add file directories to your tiled server configuration if these
conditions are met:

- Lightweight references to the file(s) and image(s) were written in databroker
  (standard ophyd practice).
- Referenced files are available to the tiled server when their data is
  requested by a client of the tiled server.

<details>
<summary>Missing files...</summary>

If a client requests data that comes from a referenced file and that file is not
available at the time of the request, the tiled server will return a *500
Internal Server Error* to the client.  For security reasons, a more detailed
answer is not provided to the tiled client.  The tiled server console will
usually provide the detail that the file could not be found.

</details>

#### local data files

Skip this section if you are just getting started.

*If* you want tiled to serve data files, the config file becomes longer.  The
`config.yml` file has examples.  Each file directory tree (including all its
subdirectories) is a separate entry in the `config.yml` file and a separate
SQLite file.

Note: Very likely that details are missing in this section.  Ask for help or
create an [issue](https://github.com/BCDA-APS/tiled-template/issues/new).

<details>
<summary>Steps to add a directory tree</summary>

Note: This is documentation is preliminary.

For each directory tree, these steps:

1. Identify a data file directory tree to be served by tiled.
    1. Create a new block in `config.yml` for the tree.
    1. Assign a name (like a catalog name) to identify the directory tree.
1. Recognize files by *mimetype*.
    1. Prepare Python code that recognizes new file types and assigns *mimetype* to each.
        1. Recognized by common file extension (such as `.mda` or `.xml`).
        1. Recognized by content analysis (such as NeXus, SPEC, or XML).
    1. Prepare Python tiled *adapter* code for each new *mimetype*.
    1. Add line(s) for each new *mimetype* to `config.yml`.
1. Create an SQLite catalog for the directory tree.
    1. Shell script `recreate_sampler.sh`
        1. `SQL_CATALOG=dev_sampler.sql`: name of SQLite file to be (re)created
        1. `FILE_DIR=./dev_sampler` : directory to be served
    1. Example (hypothetical) local directory
        1. Directory: `./dev_sampler` (does not exist in template here)
        1. Contains these types of file: MDA, NeXus, SPEC, images, XML, HDF4, text
1. Add SQLite file details to `config.yml` file:

    ```yaml
    args:
        uri: ./dev_sampler.sql
        readable_storage:
        - ./dev_sampler
    ```

</details>

<details>
<summary>Details</summary>

You specify data files by providing their directory (which includes all
subdirectories within).

Files are recognized by
[*mimetype*](https://stackoverflow.com/questions/3828352/what-is-a-mime-type).
The configuration template has several examples.  Here is an example for a SPEC
data file:

```yaml
    text/x-spec_data: spec_data:read_spec_data
```

The *mimetype* is `text/x-spec_data`.  The adapter is the `read_spec_data()`
function in file `spec_data.py` (in the same directory as the `config.yml`).

Custom *mimetype*s, such as `text/x-spec_data` are assigned in function
`detect_mimetype()` (in local file `custom.py`).  This code identifies SPEC,
NeXus, and (non-NeXus) HDF5 files.

Well-known file types, such as JPEG, TIFF, PNG, plain text, are recognized by
library functions called by the tiled server library code.

For the SQLite file (at least at APS beamlines), keep in mind that NFS file
access is noticeably slower than local file access.  It is recommended to store
the SQLite file on a local filesystem for the tiled server.

</details>

## Run the server

A bash shell script is available to run your tiled server.  Take note of two important environment variables:

- `HOST`: What client IP numbers will this server respond to?  If `0.0.0.0`, the
  server will respond to clients from any IP number.  If `127.0.0.1`, the server
  will only respond to clients on this workstation (localhost).
- `PORT`: What port will this server listen to?  Your choice here.  The default
  choice here is arbitrary yet advised.  Port 8000 is common but may be used by
  some other local web server software.  We choose port 8020 to avoid this
  possibility.

Once the `config.yml` and `start-tiled.sh` (and any configured SQLite) files are
prepared, start the tiled server for testing:

<pre>
<b>$</b> ./start-tiled.sh
</pre>

Here is the output from my tiled server as it starts:

```bash
Using configuration from /home/beams1/JEMIAN/Documents/projects/BCDA-APS/tiled-template/config.yml

    Tiled server is running in "public" mode, permitting open, anonymous access
    for reading. Any data that is not specifically controlled with an access
    policy will be visible to anyone who can connect to this server.


    Navigate a web browser or connect a Tiled client to:

    http://0.0.0.0:8020?api_key=d8edc247909a0246b4e2dd8ca8d75443f87f2c5facd627b703d6635284e2f2fc


    Because this server is public, the '?api_key=...' portion of
    the URL is needed only for _writing_ data (if applicable).


INFO:     Started server process [2033851]
INFO:     Waiting for application startup.
OBJECT CACHE: Will use up to 1_190_568_960 bytes (15% of total physical RAM)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8020 (Press CTRL+C to quit)
```

Note:  In this example, the `api_key` is randomly chosen by the server as it
starts.  With this option for tiled server startup, a new key is generated each
time.  A local installation should make a different choice, to provide its own
key to allow authorized clients to write data (as bluesky documents from a
RunEngine subscription).

Enter the server URL (above: `http://0.0.0.0:8020`, not `https`) in a web
browser to test the server responds.  Observe the server's console output each
time the web browser makes a new request.

Press `^C` to quit the server.

## Enable auto (re)start

A bash shell script is available to help you manage the tiled server.  It runs
the tiled server in a screen sessions (so the server does not quit when you
logout).  The help command shows the commands available:

<pre>
<b>$</b> ./tiled-manage.sh help
Usage: ./tiled-manage.sh {start|stop|restart|checkup|status}
</pre>

For example, this linux command shows the server status on my workstation:

```bash
./tiled-manage.sh status
# [2023-12-08T11:06:36-06:00 ./tiled-manage.sh] running fine, so it seems
```

Launch the server (for regular use):

```bash
./tiled-manage.sh start
```

The `checkup` command may be used to (re)start the server.  For example, to
enable automatic (re)start, add this line to your linux `cron` tasks.

```cron
*/5 * * * * /full/path/to/your/tiled-server/tiled-manage.sh checkup 2>&1 > /dev/null
```

Linux command `crontab -e` will open an editor where you can paste this line.
The `tiled-manage.sh checkup` task will run every 5 minutes (9:10, 9:15, 9:20,
...).  Within 5 minutes of a workstation reboot, the tiled server will be
started.

## Clients

Enter the server URL (above: `http://0.0.0.0:8020`, not `https`) in a web
browser to test the server responds.  Observe the server's console output each
time the web browser makes a new request.

You can use a web browser or find it more convenient to develop your own code
that makes requests using either URIs or Python `tiled.client` calls.


[`Gemviz`](https://bcda-aps.github.io/gemviz/), a Python Qt5 GUI program, is
being developed to browse and visualize data from your databroker catalogs.
