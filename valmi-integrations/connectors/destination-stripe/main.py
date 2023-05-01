#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_stripe import DestinationStripe

if __name__ == "__main__":
    DestinationStripe().run(sys.argv[1:])
