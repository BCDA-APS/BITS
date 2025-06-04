"""
Identify new MongoDB catalogs for the tiled server.

This code prints additional lines that could be added
to the tiled `config.yml` file.  The lines describe catalogs
with known intake descriptions that are not already configured
in the `config.yml` file.
"""

import pathlib

import yaml


def tiled_test():
    from tiled.client import from_uri

    client = from_uri("http://otz:8000", "dask")
    cat = client["6idd"]
    print(f"{cat=}")


def read_intake_yaml(file) -> dict:
    with open(file) as f:
        db_cfg = yaml.load(f, Loader=yaml.Loader)
        return db_cfg["sources"]


def main():
    home = pathlib.Path.home()
    # print(f"{home=}")
    databroker_configs = home / ".local" / "share" / "intake"
    # print(f"exists:{databroker_configs.exists()}  {databroker_configs}")

    master = {
        k: v
        for intake_yml in databroker_configs.iterdir()
        if intake_yml.is_file() and intake_yml.suffix == ".yml"
        for k, v in read_intake_yaml(intake_yml).items()
    }

    local_config = pathlib.Path(__file__).parent / "config.yml"
    # print(f"exists:{local_config.exists()}  {local_config}")
    with open(local_config) as f:
        config = yaml.load(f, Loader=yaml.Loader)
        trees = {tree["path"]: tree for tree in config.get("trees", {})}

    new_entries = []
    for k, source in master.items():
        if k not in trees:
            if source.get("driver") == "bluesky-mongo-normalized-catalog":
                uri = source.get("args", {}).get("metadatastore_db")
                if uri is not None:
                    entry = dict(
                        path=k,
                        tree="databroker.mongo_normalized:Tree.from_uri",
                        args=dict(uri=uri),
                    )
                    new_entries.append(entry)
    print(yaml.dump(new_entries, indent=4))


if __name__ == "__main__":
    main()
