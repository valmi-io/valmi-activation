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

import hashlib

from typing import Any, Mapping, Dict, List
from airbyte_cdk import AirbyteLogger
from collections import defaultdict
from time import sleep

from valmi_connector_lib.valmi_protocol import (
    ValmiStream,
    ConfiguredValmiSink,
)

from valmi_connector_lib.common.run_time_args import RunTimeArgs

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Number of retries to be run in case of a RateExceededError.
NUM_RETRIES = 6

# Minimum number of seconds to wait before a retry.
RETRY_SECONDS = 30

MAX_CHUNK_SIZE = 3000  # limit is (10000/(3 identifies)) for a single job request


def normalize_and_hash(s: str, remove_all_whitespace: bool) -> str:
    """Normalizes and hashes a string with SHA-256.

    Args:
        s: The string to perform this operation on.
        remove_all_whitespace: If true, removes leading, trailing, and
            intermediate spaces from the string before hashing. If false, only
            removes leading and trailing spaces from the string before hashing.

    Returns:
        A normalized (lowercase, remove whitespace) and SHA-256 hashed string.
    """
    # Normalizes by first converting all characters to lowercase, then trimming
    # spaces.
    if remove_all_whitespace:
        # Removes leading, trailing, and intermediate whitespace.
        s = "".join(s.split())
    else:
        # Removes only leading and trailing spaces.
        s = s.strip().lower()

    # Hashes the normalized string using the hashing algorithm.
    return hashlib.sha256(s.encode()).hexdigest()


class GoogleAdsUtils:

    def __init__(
            self,
            logger: AirbyteLogger,
            client: GoogleAdsClient,
            run_time_args: RunTimeArgs = None
    ) -> None:
        self.logger = logger
        self.client = client
        self.runtime_args = run_time_args
        self.num_identifiers: dict[str, int] = defaultdict(lambda: 0)
        self.offline_user_data_job_resource_names: dict[str, str] = defaultdict(str)
        self.operations: dict[str, list[Any]] = defaultdict(list)

        # Max cap on chunk size
        self.chunk_size = MAX_CHUNK_SIZE
        if run_time_args and run_time_args.chunk_size:
            if run_time_args.chunk_size < MAX_CHUNK_SIZE:
                self.chunk_size = run_time_args.chunk_size

    def get_custom_audience_schema(self) -> Mapping[str, Any]:
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "phone_number": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "country_code": {"type": "string"},
                "postal_code": {"type": "string"},
                "street_address": {"type": "string"},
            },
        }

        return json_schema

    def get_accounts(self) -> List[Dict[str, Any]]:
        """Gets the account mapping from client id to manager id and descriptive name.
        """

        # Gets instances of the GoogleAdsService and CustomerService clients.
        googleads_service = self.client.get_service("GoogleAdsService")
        customer_service = self.client.get_service("CustomerService")

        # A collection of customer IDs to handle.
        seed_customer_ids: List[str] = []

        # Creates a query that retrieves all child accounts of the manager
        # specified in search calls below.
        query = """
            SELECT
              customer_client.client_customer,
              customer_client.level,
              customer_client.manager,
              customer_client.descriptive_name,
              customer_client.currency_code,
              customer_client.time_zone,
              customer_client.id
            FROM customer_client
            WHERE customer_client.level <= 1
        """

        customer_resource_names = (
            customer_service.list_accessible_customers().resource_names
        )

        seed_customer_ids = []

        # Mapping from client customer ID to manager customer ID.
        # root customer will not have any manger customer ID.
        # All other customers will have root customer ID as a manager customer ID.
        client_to_manager: List[Dict[str, Any]] = []

        for customer_resource_name in customer_resource_names:
            customer_id = googleads_service.parse_customer_path(
                customer_resource_name)["customer_id"]

            self.logger.info(f"Customer ID: {customer_id}")
            seed_customer_ids.append(customer_id)

        for seed_customer_id in seed_customer_ids:
            # Performs a breadth-first search to build a Dictionary that maps
            # managers to their child accounts (customerIdsToChildAccounts).
            unprocessed_customer_ids = [seed_customer_id]
            customer_ids_to_child_accounts: Dict[str, Any] = dict()

            root_customer_client = None

            while unprocessed_customer_ids:
                customer_id = int(unprocessed_customer_ids.pop(0))
                response = googleads_service.search(
                    customer_id=str(customer_id), query=query
                )

                # Iterates over all rows in all pages to get all customer
                # clients under the specified customer's hierarchy.
                for googleads_row in response:
                    customer_client = googleads_row.customer_client
                    name = customer_client.descriptive_name
                    name = name if name.strip() != "" else "Google Ads Account"

                    # The customer client that with level 0 is the specified
                    # customer.
                    if customer_client.level == 0:
                        if root_customer_client is None:
                            root_customer_client = customer_client

                            client_to_manager.append({
                                "account": customer_client.id,
                                "manager": None,
                                "name": name,
                            })
                        continue

                    # For all level-1 (direct child) accounts that are a
                    # manager account, the above query will be run against them
                    # to create a Dictionary of managers mapped to their child
                    # accounts for printing the hierarchy afterwards.
                    if customer_id not in customer_ids_to_child_accounts:
                        customer_ids_to_child_accounts[customer_id] = []

                    customer_ids_to_child_accounts[customer_id].append(
                        customer_client
                    )

                    client_to_manager.append({
                        "account": customer_client.id,
                        "manager": seed_customer_id,
                        "name": name,
                    })

                    if customer_client.manager:
                        # A customer can be managed by multiple managers, so to
                        # prevent visiting the same customer many times, we
                        # need to check if it's already in the Dictionary.
                        if (customer_client.id not in customer_ids_to_child_accounts 
                                and customer_client.level == 1):
                            unprocessed_customer_ids.append(customer_client.id)

        return client_to_manager

    def prepare_user_data_from_record(self, record: Mapping[str, Any]) -> Any:
        # Creates a UserData object that represents a member of the user list.
        user_data = self.client.get_type("UserData")

        # Checks if the record has email, phone, or address information, and
        # adds a SEPARATE UserIdentifier object for each one found. For example,
        # a record with an email address and a phone number will result in a
        # UserData with two UserIdentifiers.

        # IMPORTANT: Since the identifier attribute of UserIdentifier
        # (https://developers.google.com/google-ads/api/reference/rpc/latest/UserIdentifier)
        # is a oneof
        # (https://protobuf.dev/programming-guides/proto3/#oneof-features), you
        # must set only ONE of hashed_email, hashed_phone_number, mobile_id,
        # third_party_user_id, or address-info. Setting more than one of these
        # attributes on the same UserIdentifier will clear all the other members
        # of the oneof. For example, the following code is INCORRECT and will
        # result in a UserIdentifier with ONLY a hashed_phone_number:

        # incorrect_user_identifier = client.get_type("UserIdentifier")
        # incorrect_user_identifier.hashed_email = "..."
        # incorrect_user_identifier.hashed_phone_number = "..."

        # The separate 'if' statements below demonstrate the correct approach
        # for creating a UserData object for a member with multiple
        # UserIdentifiers.

        # Checks if the record has an email address, and if so, adds a
        # UserIdentifier for it.
        if "email" in record:
            user_identifier = self.client.get_type("UserIdentifier")
            user_identifier.hashed_email = normalize_and_hash(
                record["email"], True
            )
            # Adds the hashed email identifier to the UserData object's list.
            user_data.user_identifiers.append(user_identifier)

        # Checks if the record has a phone number, and if so, adds a
        # UserIdentifier for it.
        if "phone" in record:
            user_identifier = self.client.get_type("UserIdentifier")
            user_identifier.hashed_phone_number = normalize_and_hash(
                record["phone"], True
            )
            # Adds the hashed phone number identifier to the UserData object's
            # list.
            user_data.user_identifiers.append(user_identifier)

        # Checks if the record has all the required mailing address elements,
        # and if so, adds a UserIdentifier for the mailing address.
        if "first_name" in record:
            required_keys = ("last_name", "country_code", "postal_code")
            # Checks if the record contains all the other required elements of
            # a mailing address.
            if not all(key in record for key in required_keys):
                # Determines which required elements are missing from the
                # record.
                missing_keys = record.keys() - required_keys
                self.logger.info(
                    "Skipping addition of mailing address information "
                    "because the following required keys are missing: "
                    f"{missing_keys}"
                )
            else:
                user_identifier = self.client.get_type("UserIdentifier")
                address_info = user_identifier.address_info
                address_info.hashed_first_name = normalize_and_hash(
                    record["first_name"], False
                )
                address_info.hashed_last_name = normalize_and_hash(
                    record["last_name"], False
                )
                address_info.country_code = record["country_code"]
                address_info.postal_code = record["postal_code"]
                user_data.user_identifiers.append(user_identifier)

        return user_data

    def add_to_queue(self, 
                     data: Mapping[str, Any], 
                     configured_stream: ValmiStream, 
                     sink: ConfiguredValmiSink
                     ) -> bool:
        # At max 20 identifiers can be added to a user data object.
        # Ref: https://developers.google.com/google-ads/api/docs/remarketing/audience-types/customer-match#customer_match_considerations

        user_data = self.prepare_user_data_from_record(data)
        self.logger.info(f"Adding user data: {user_data}")

        if user_data.user_identifiers:
            operation = self.client.get_type("OfflineUserDataJobOperation")
            sync_op = data["_valmi_meta"]["_valmi_sync_op"]
            self.num_identifiers[sync_op] += len(user_data.user_identifiers)

            if sync_op == "delete":
                operation.remove = user_data
            else:
                operation.create = user_data
                # Treating all other operations as create ( operation.create will handle update and insert )
                sync_op = "create"

            self.operations[sync_op].append(operation)

            # Check if any of the `delete` or `upsert` operations reaches max_identifiers limit 
            # we will publish them
            publish_operations: bool = False
            for key, value in self.num_identifiers.items():
                if value >= self.chunk_size:
                    publish_operations = True
                    break

            if publish_operations:
                self.flush(sink)
                self.num_identifiers = defaultdict(int)
                return True

        return False

    def create_offline_user_data_job(self, user_list_resource_name: str, customer_id: str) -> str:
        """ 
        Creates new OfflineUserDataJob and returns the resource name of the newly created job.

        Args:
            user_list_resource_name: User List resource name 
            customer_id: Customer ID

        Returns:
            str: offline user data job resource name
        """
        # Creates a new offline user data job.
        offline_user_data_job = self.client.get_type("OfflineUserDataJob")
        offline_user_data_job.type_ = (
            self.client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST
        )
        offline_user_data_job.customer_match_user_list_metadata.user_list = (
            user_list_resource_name
        )
        # Issues a request to create an offline user data job.
        offline_user_data_job_service_client = self.client.get_service(
            "OfflineUserDataJobService"
        )
        create_offline_user_data_job_response = offline_user_data_job_service_client.create_offline_user_data_job(
            customer_id=customer_id, job=offline_user_data_job
        )
        # Note 
        # The job resource name looks like this:
        #   customers/{customer_id}/offlineUserDataJobs/{offline_user_data_update_id}

        offline_user_data_job_resource_name = (
            create_offline_user_data_job_response.resource_name
        )

        self.logger.info(
            "Created an offline user data job with resource name: "
            f"'{offline_user_data_job_resource_name}'."
        )

        return offline_user_data_job_resource_name

    def request_offline_user_data_job(
        self,
        job_resource_name: str,
        operations: list[Any]
    ) -> None:
        """Requests offline user data job"""
        offline_user_data_job_service_client = self.client.get_service(
            "OfflineUserDataJobService"
        )
        # Issues a request to add the operations to the offline user data job.

        # Best Practice: This example only adds a few operations, so it only sends
        # one AddOfflineUserDataJobOperations request. If your application is adding
        # a large number of operations, split the operations into batches and send
        # multiple AddOfflineUserDataJobOperations requests for the SAME job. See
        # https://developers.google.com/google-ads/api/docs/remarketing/audience-types/customer-match#customer_match_considerations
        # and https://developers.google.com/google-ads/api/docs/best-practices/quotas#user_data
        # for more information on the per-request limits.
        self.logger.info(f"Number of user operations to be created: {len(operations)}")
        request = self.client.get_type("AddOfflineUserDataJobOperationsRequest")
        request.resource_name = job_resource_name
        request.operations = operations
        request.enable_partial_failure = True

        # Issues a request to add the operations to the offline user data job.
        response = offline_user_data_job_service_client.add_offline_user_data_job_operations(
            request=request
        )

        # Prints the status message if any partial failure error is returned.
        # Note: the details of each partial failure error are not printed here.
        # Refer to the error_handling/handle_partial_failure.py example to learn
        # more.
        # Extracts the partial failure from the response status.
        partial_failure = getattr(response, "partial_failure_error", None)
        if getattr(partial_failure, "code", None) != 0:
            error_details = getattr(partial_failure, "details", [])
            for error_detail in error_details:
                failure_message = self.client.get_type("GoogleAdsFailure")
                # Retrieve the class definition of the GoogleAdsFailure instance
                # in order to use the "deserialize" class method to parse the
                # error_detail string into a protobuf message object.
                failure_object = type(failure_message).deserialize(
                    error_detail.value
                )

                for error in failure_object.errors:
                    self.logger.info(
                        "A partial failure at index "
                        f"{error.location.field_path_elements[0].index} occurred.\n"
                        f"Error message: {error.message}\n"
                        f"Error code: {error.error_code}"
                    )


    def flush(self, sink: ConfiguredValmiSink) -> None:
        # Note
        # sink.id is actually userlist resource name 
        # It will be in the format : customers/{customer_id}/userLists/{user_list_id}
        customer_id = sink.sink.id.split("/")[1]

        quota_error_enum = self.client.get_type("QuotaErrorEnum").QuotaError
        resource_exhausted = quota_error_enum.RESOURCE_EXHAUSTED
        temp_resource_exhausted = quota_error_enum.RESOURCE_TEMPORARILY_EXHAUSTED

        # This will be thrown when two or more jobs are running on same user list resource
        database_error_enum = self.client.get_type("DatabaseErrorEnum").DatabaseError
        concurrent_modification = database_error_enum.CONCURRENT_MODIFICATION

        # We will send `delete` and `upsert` operations in separate `OfflineUserDataJob`
        # Delete actions will be performed first and then `upsert` actions
        ops = ["delete", "create"]
        for op in ops:
            self.logger.info(f"{len(self.operations[op])} Operations for {op}")

            if not len(self.operations[op]):
                continue

            offline_user_data_job_resource_name = self.offline_user_data_job_resource_names[op]

            if not offline_user_data_job_resource_name:
                offline_user_data_job_resource_name = self.create_offline_user_data_job(
                    sink.sink.id, customer_id
                )
                self.offline_user_data_job_resource_names[op] = offline_user_data_job_resource_name

            try:
                retry_count = 0
                retry_seconds = RETRY_SECONDS

                while retry_count < NUM_RETRIES:
                    try:
                        job_operations = self.operations[op]

                        self.logger.info(f"Retry count: {retry_count} for {op}")
                        self.request_offline_user_data_job(
                            offline_user_data_job_resource_name, job_operations
                        )
                        self.operations[op] = []
                        break

                    except GoogleAdsException as ex:
                        retrying = False
                        self.logger.info(f"GoogleAdsException: {ex}")
                        for googleads_error in ex.failure.errors:
                            # Checks if any of the errors are
                            # QuotaError.RESOURCE_EXHAUSTED or
                            # QuotaError.RESOURCE_TEMPORARILY_EXHAUSTED or
                            # DatabaseError.CONCURRENT_MODIFICATION
                            quota_error = googleads_error.error_code.quota_error
                            database_error = googleads_error.error_code.database_error

                            if (
                                quota_error == resource_exhausted
                                or quota_error == temp_resource_exhausted
                                or database_error == concurrent_modification
                            ):
                                self.logger.info(
                                    "Received rate exceeded error/concurrent modification error, retry after"
                                    f"{retry_seconds} seconds."
                                )
                                sleep(retry_seconds)
                                retrying = True
                                retry_count += 1
                                # Here exponential backoff is employed to ensure
                                # the account doesn't get rate limited by making
                                # too many requests too quickly. This increases the
                                # time to wait between requests by a factor of 2.
                                retry_seconds *= 2
                                break
                        # Bubbles up when there is not a RateExceededError
                        if not retrying:
                            raise ex
                    finally:
                        if retry_count == NUM_RETRIES:
                            raise Exception(
                                "Could not recover after making "
                                f"{retry_count} attempts."
                            )
            except Exception as ex:
                # Prints any unhandled exception and bubbles up.
                self.logger.info(f"Failed to validate keywords: {ex}")
                raise ex

    def check_job_status(self, customer_id, offline_user_data_job_resource_name):
        """Retrieves, checks, and prints the status of the offline user data job.

        If the job is completed successfully, information about the user list is
        printed. Otherwise, a GAQL query will be printed, which can be used to
        check the job status at a later date.

        Offline user data jobs may take 6 hours or more to complete, so checking the
        status periodically, instead of waiting, can be more efficient.

        Args:
            customer_id: The ID for the customer that owns the user list.
        """
        query = f"""
            SELECT
              offline_user_data_job.resource_name,
              offline_user_data_job.id,
              offline_user_data_job.status,
              offline_user_data_job.type,
              offline_user_data_job.failure_reason,
              offline_user_data_job.customer_match_user_list_metadata.user_list
            FROM offline_user_data_job
            WHERE offline_user_data_job.resource_name =
              '{offline_user_data_job_resource_name}'
            LIMIT 1"""

        # Issues a search request using streaming.
        google_ads_service = self.client.get_service("GoogleAdsService")
        results = google_ads_service.search(customer_id=customer_id, query=query)
        offline_user_data_job = next(iter(results)).offline_user_data_job
        status_name = offline_user_data_job.status.name
        user_list_resource_name = (
            offline_user_data_job.customer_match_user_list_metadata.user_list
        )

        self.logger.info(
            f"Offline user data job ID '{offline_user_data_job.id}' with type "
            f"'{offline_user_data_job.type_.name}' has status: {status_name}"
        )

        if status_name == "SUCCESS":
            self.print_customer_match_user_list_info(customer_id, user_list_resource_name)
        elif status_name == "FAILED":
            self.logger.info(f"\tFailure Reason: {offline_user_data_job.failure_reason}")
        elif status_name in ("PENDING", "RUNNING"):
            self.logger.info(
                "To check the status of the job periodically, use the following "
                f"GAQL query with GoogleAdsService.Search: {query}"
            )

    def print_customer_match_user_list_info(
        self, customer_id, user_list_resource_name
    ):
        """Prints information about the Customer Match user list.

        Args:
            client: The Google Ads client.
            customer_id: The ID for the customer that owns the user list.
            user_list_resource_name: The resource name of the user list to which to
                add users.
        """
        googleads_service_client = self.client.get_service("GoogleAdsService")

        # Creates a query that retrieves the user list.
        query = f"""
            SELECT
              user_list.size_for_display,
              user_list.size_for_search
            FROM user_list
            WHERE user_list.resource_name = '{user_list_resource_name}'"""

        # Issues a search request.
        search_results = googleads_service_client.search(
            customer_id=customer_id, query=query
        )

        # Prints out some information about the user list.
        user_list = next(iter(search_results)).user_list
        self.logger.info(
            "The estimated number of users that the user list "
            f"'{user_list.resource_name}' has is "
            f"{user_list.size_for_display} for Display and "
            f"{user_list.size_for_search} for Search."
        )
        self.logger.info(
            "Reminder: It may take several hours for the user list to be "
        )

    def submit_offline_jobs(self, sink: ConfiguredValmiSink):
        """Submits offline user data job operations to the Google Ads API.

        Returns:
            A list of offline user data job operations.
        """
        customer_id = sink.sink.id.split("/")[1]

        # Creates the OfflineUserDataJobService client.
        offline_user_data_job_service_client = self.client.get_service(
            "OfflineUserDataJobService"
        )

        # Submit delete operations
        delete_job_resource_name = self.offline_user_data_job_resource_names.get("delete", None)
        if delete_job_resource_name:
            self.logger.info(f"Offline user data job for delete operations: {delete_job_resource_name}")

            # Issues a request to run the offline user data job for executing all
            # added operations.
            request_response = offline_user_data_job_service_client.run_offline_user_data_job(
                resource_name=delete_job_resource_name
            )

            self.check_job_status(customer_id, delete_job_resource_name)

            # Waits until the next day to create a new job.
            self.logger.info("Waiting until request is finished...")
            request_response.result()

        # Submit create operations
        create_job_resource_name = self.offline_user_data_job_resource_names.get("create", None)
        if create_job_resource_name:
            self.logger.info(f"Offline user data job for create operations: {create_job_resource_name}")
            request_response = offline_user_data_job_service_client.run_offline_user_data_job(
                resource_name=create_job_resource_name
            )
            self.check_job_status(customer_id, create_job_resource_name)
