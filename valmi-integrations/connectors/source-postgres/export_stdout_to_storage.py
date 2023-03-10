#!env python
import json
import os
import sys
from os.path import join
import json

buffer_size = 2
lines = []
counter = 0

MAGIC_NUM = 0x7FFFFFFF


def store(lines, last=False):
    store_config = json.loads(os.environ["VALMI_INTERMEDIATE_STORE"])
    if store_config["provider"] == "local":
        path_name = join(store_config["local"]["directory"], os.environ.get("DAGSTER_RUN_JOB_NAME", "valmi-store"))
        os.makedirs(path_name, exist_ok=True)

        list_dir = sorted([f.lower() for f in os.listdir(path_name)], key=lambda x: int(x[:-5]))
        new_file_name = f"{MAGIC_NUM}.vald" if last else (list_dir[-1] if len(list_dir) > 0 else "0.vald")
        with open(join(path_name, f"{int(new_file_name[:-5])+1}.vald"), "w") as f:
            for line in lines:
                f.write(line)


for line in sys.stdin:
    lines.append(line)
    if(json.loads(line)['type'] != 'LOG'):
        print(line)
    counter = counter + 1
    if counter >= buffer_size:
        store(lines)
        lines = []
        counter = 0
store(lines, last=True)
