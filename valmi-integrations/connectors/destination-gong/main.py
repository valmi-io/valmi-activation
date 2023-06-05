#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_gong import DestinationGong

if __name__ == "__main__":
    DestinationGong().run(sys.argv[1:])
