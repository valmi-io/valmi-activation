#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_slack import DestinationSlack

if __name__ == "__main__":
    DestinationSlack().run(sys.argv[1:])
