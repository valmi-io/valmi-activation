#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

from typing import Any, Dict, Mapping
from airbyte_cdk import AirbyteLogger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.ads.googleads.client import GoogleAdsClient

# the list of required scopes/permissions
# more info: https://developers.google.com/sheets/api/guides/authorizing#OAuth2Authorizing
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/adwords"
]

class GoogleClient:
    logger = AirbyteLogger()

    def __init__(self, config: Mapping[str, Any]):
        self.config = config
        self.retries = 100  # max number of backoff retries

    def get_credentials(self) -> Credentials:
        input_creds = self.config.get("credentials")

        self.logger.info(f"Scopes : {SCOPES}")
        creds = Credentials.from_authorized_user_info(info=input_creds, scopes=SCOPES)

        # check if token is expired and refresh it
        if creds and creds.expired and creds.refresh_token:
            self.logger.info("Auth session is expired. Refreshing...")
            refresh_attempts = 0
            session = Request()
            while True:
                try:
                    creds.refresh(session)
                    if not creds.expired:
                        self.logger.info("Successfully refreshed auth session")
                        break
                except Exception as e:
                    refresh_attempts += 1

                    if refresh_attempts >= self.retries:
                        self.logger.fatal(
                            "The token is expired and could not be refreshed, please check the credentials are still valid!"
                        )
                        print("Max refresh attempts reached. Exiting.")
                        break
        return creds

    def authorize(self, manager_id: Any = None) -> GoogleAdsClient:
        creds = self.get_credentials()
        creds_dict = json.loads(creds.to_json())
        creds_dict["developer_token"] = self.config["credentials"].get("developer_token")
        creds_dict["use_proto_plus"] = True

        if manager_id:
            creds_dict["login_customer_id"] = manager_id

        self.logger.info(json.dumps(creds_dict))

        googleads_client = GoogleAdsClient.load_from_dict(config_dict=creds_dict, version="v13")
        return googleads_client

