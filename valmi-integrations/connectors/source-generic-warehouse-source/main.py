


import sys

from airbyte_cdk.entrypoint import launch
from source_generic_warehouse_source import SourceGenericWarehouseSource

if __name__ == "__main__":
    source = SourceGenericWarehouseSource()
    launch(source, sys.argv[1:])
