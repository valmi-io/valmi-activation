#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_template import DestinationWebhook

if __name__ == "__main__":
    DestinationWebhook().run(sys.argv[1:])
