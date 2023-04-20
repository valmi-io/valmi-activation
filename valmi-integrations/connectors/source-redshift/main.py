import sys

from airbyte_cdk.entrypoint import launch
from source_redshift import SourceRedshift

if __name__ == "__main__":
    source = SourceRedshift()
    launch(source, sys.argv[1:])
