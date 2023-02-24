#!env python
import json
import os
import time
from os.path import join

MAGIC_NUM = 0x7FFFFFFF


def read():
    store_config = json.loads(os.environ["VALMI_INTERMEDIATE_STORE"])
    if store_config["provider"] == "local":
        path_name = join(store_config["local"]["directory"], os.environ.get("DAGSTER_RUN_JOB_NAME", "valmi-store"))

        if not os.path.exists(path_name):
            time.sleep(5)
            yield ""
        list_dir = sorted([f.lower() for f in os.listdir(path_name)], key=lambda x: int(x[:-5]))
        for f in list_dir:
            if f.endswith(".vald"):
                with open(join(path_name, f), "r") as f:
                    for line in f.readlines():
                        yield line
            if f.startswith(f"{MAGIC_NUM}"):
                return


print(read(), end="")
