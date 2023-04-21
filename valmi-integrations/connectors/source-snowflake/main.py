import sys

from airbyte_cdk.entrypoint import launch
from source_snowflake import SourceSnowflake

if __name__ == "__main__":
    source = SourceSnowflake()
    launch(source, sys.argv[1:])
