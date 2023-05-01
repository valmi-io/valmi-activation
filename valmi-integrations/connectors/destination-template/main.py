#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_template import DestinationTemplate

if __name__ == "__main__":
    DestinationTemplate().run(sys.argv[1:])
