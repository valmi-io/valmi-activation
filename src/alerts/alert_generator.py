'''
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Thursday, January 4th 2024, 6:04:15 pm
Author: Rajashekar Varkala @ valmi.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import logging
import threading
import time
from vyper import v
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(v.get("LOGGER_NAME"))


class AlertGenerator:
    __initialized = False

    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(AlertGenerator, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if AlertGenerator.__initialized:
            return

        self.arr_acc_mutex = threading.RLock()
        self.alerts = []
        AlertGenerator.__initialized = True

        self.alert_list_handler_thread = AlertListHandlerThread(128, "AlertListHandlerThread")
        self.alert_list_handler_thread.start()

    def sync_status_alert(self, sync_id: str, run_id: str, status: str, value: str) -> None:
        if not v.get("ALERTS_ENABLED"):
            return

        def alert_fn():
            sync = None
            try:
                sync = requests.get(
                    f"http://{v.get('APP_BACKEND')}:{v.get('APP_BACKEND_PORT')}/api/v1/workspaces/{'DUMMY'}/syncs/{sync_id}",
                    timeout=v.get("HTTP_REQ_TIMEOUT"),
                    auth=HTTPBasicAuth(v.get("ADMIN_EMAIL"), v.get("ADMIN_PASSWORD")),
                ).json()
            except Exception:
                logger.exception("Sync Details Fetch failed while alerting.")
                return

            try:
                requests.post(
                    v.get("ALERTS_API_URL"),
                    timeout=v.get("HTTP_REQ_TIMEOUT"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": v.get("ALERTS_API_AUTH_HEADER_VALUE")
                    },
                    json={
                        "correlate": [
                            "SyncRun" + status.capitalize()
                        ],
                        "environment": v.get("DEPLOYMENT_ENVIRONMENT"),
                        "event": "SyncRun" + status.capitalize(),
                        "group": "SyncRuns",
                        "origin": v.get("ALERTS_ORIGIN"),
                        "resource": "Sync: " + sync['name'] + " Run: " + str(run_id),
                        "service": [
                            str(run_id)
                        ],
                        "severity": "normal" if status == "terminated" else "major",
                        "text": "Run with id (" + str(run_id) + ") " + status + " for " + sync['name'] + " sync.",
                        "value": value
                    },
                )
            except Exception:
                logger.exception("Failed to send sync run status alert.")
                return

        with self.arr_acc_mutex:
            self.alerts.append(alert_fn)

    def destroy(self) -> None:
        self.cleaner_thread.exit_flag = True


class AlertListHandlerThread(threading.Thread):
    def __init__(self, thread_id: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.exit_flag = False
        self.name = name

    def run(self) -> None:
        while not self.exit_flag:
            try:
                logger.info("Running alerts")

                alerts = []
                with AlertGenerator().arr_acc_mutex:
                    alerts = AlertGenerator().alerts.copy()
                    AlertGenerator().alerts.clear()

                for alert in alerts:
                    alert()

                time.sleep(15)
            except Exception:
                logger.exception("Error while sending alerts")
                time.sleep(15)
