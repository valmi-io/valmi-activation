
import sys

from airbyte_cdk.entrypoint import launch
from source_postgres import SourcePostgres

if __name__ == "__main__":
    source = SourcePostgres()
    launch(source, sys.argv[1:])
