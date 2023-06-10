#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_android_push_notifications import DestinationAndroidPushNotifications

if __name__ == "__main__":
    DestinationAndroidPushNotifications().run(sys.argv[1:])
