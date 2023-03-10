from typing import Any, Dict
from uuid import uuid4

import dagster._check as check
from dagster import DagsterRunStatus

from dagster_graphql.client.client_queries import (
    GET_PIPELINE_RUN_STATUS_QUERY,
)

from dagster_graphql.client.utils import (
    DagsterGraphQLClientError,
)

from dagster_graphql import DagsterGraphQLClient
from pydantic import UUID4

GET_PIPELINE_RUN_STATUS_LOGS_QUERY = """
query($runId: ID!) {
  pipelineRunOrError(runId: $runId) {
    __typename
    ... on PipelineRun {
        status
    }
    ... on PipelineRunNotFoundError {
      message
    }
    ... on PythonError {
      message
    }
  }
}
"""


class ValmiDagsterClient(DagsterGraphQLClient):
    def get_run_status(self, run_id: str) -> DagsterRunStatus:
        """Get the status of a given Pipeline Run.

        Args:
            run_id (str): run id of the requested pipeline run.

        Raises:
            DagsterGraphQLClientError("PipelineNotFoundError", message): if the requested run id is not found
            DagsterGraphQLClientError("PythonError", message): on internal framework errors

        Returns:
            DagsterRunStatus: returns a status Enum describing the state of the requested pipeline run
        """
        check.str_param(run_id, "run_id")

        res_data: Dict[str, Dict[str, Any]] = self._execute(GET_PIPELINE_RUN_STATUS_QUERY, {"runId": run_id})
        query_result: Dict[str, Any] = res_data["pipelineRunOrError"]
        query_result_type: str = query_result["__typename"]
        if query_result_type == "PipelineRun" or query_result_type == "Run":
            return DagsterRunStatus(query_result["status"]), query_result
        else:
            raise DagsterGraphQLClientError(query_result_type, query_result["message"])

    # sanitise uuid
    def su(self, uuid: UUID4) -> str:
        return str(uuid).replace("-", "_")

    # desanitise uuid
    def du(self, uuid: str) -> UUID4:
        return uuid4(uuid.replace("_", "-"))
