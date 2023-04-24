#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_hubspot import DestinationHubspot

if __name__ == "__main__":
    DestinationHubspot().run(sys.argv[1:])
