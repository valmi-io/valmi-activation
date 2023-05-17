"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, May 4th 2023, 20:44:42 pm
Author: Srinivas @ valmi.io

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
"""

from typing import Any, List
from airbyte_cdk import AirbyteLogger
from google.ads.googleads.client import GoogleAdsClient

class GoogleAdsAccount:

    def __init__(self, logger: AirbyteLogger, client: GoogleAdsClient, customer_id: str) -> None:
        self.logger = logger
        self.client = client
        self.customer_id = customer_id

    def get_custom_audiences(self) -> List[Any]:

        googleads_service_client = self.client.get_service("GoogleAdsService")

        # Creates a query that retrieves the user list.
        query = f"""
            SELECT
              user_list.id,
              user_list.name,
              user_list.resource_name
            FROM user_list
        """

        # Issues a search request.
        search_results = googleads_service_client.search(
            customer_id=self.customer_id, query=query
        )

        user_lists = [ row.user_list for row in search_results ]
        return user_lists

    def create_customer_match_user_list(
        self, 
        name:str, 
        description:str,
        membership_life_span:int
    ) -> str:
        """Creates a Customer Match user list.

        Returns:
            The string resource name of the newly created user list.
        """
        # Creates the UserListService client.
        user_list_service_client = self.client.get_service("UserListService")

        # Creates the user list operation.
        user_list_operation = self.client.get_type("UserListOperation")

        # Creates the new user list.
        user_list = user_list_operation.create
        user_list.name = name
        user_list.description = description

        # Sets the upload key type to indicate the type of identifier that is used
        # to add users to the list. This field is immutable and required for a
        # CREATE operation.
        user_list.crm_based_user_list.upload_key_type = (
            self.client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
        )
        # Customer Match user lists can set an unlimited membership life span;
        # to do so, use the special life span value 10000. Otherwise, membership
        # life span must be between 0 and 540 days inclusive. See:
        # https://developers.devsite.corp.google.com/google-ads/api/reference/rpc/latest/UserList#membership_life_span
        # Sets the membership life span to 30 days.

        user_list.membership_life_span = membership_life_span

        response = user_list_service_client.mutate_user_lists(
            customer_id=self.customer_id, operations=[user_list_operation]
        )
        user_list_resource_name = response.results[0].resource_name
        self.logger.info(
            f"User list with resource name '{user_list_resource_name}' was created."
        )

        return str(user_list_resource_name)
