#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_facebook_ads import DestinationFacebookAds

if __name__ == "__main__":
    DestinationFacebookAds().run(sys.argv[1:])
