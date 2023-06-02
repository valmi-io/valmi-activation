import uuid

from pydantic import UUID4
from typing import Any, Dict

from dagster_graphql import DagsterGraphQLClient
from dagster_graphql import DagsterGraphQLClientError

from dagster import check

TERMINATE_RUN_JOB_MUTATION = """
mutation TerminateRun($runId: String!) {
  terminateRun(runId: $runId, terminatePolicy: MARK_AS_CANCELED_IMMEDIATELY){
    __typename
    ... on TerminateRunSuccess{
      run {
        runId
      }
    }
    ... on TerminateRunFailure {
      message
    }
    ... on RunNotFoundError {
      runId
    }
    ... on PythonError {
      message
      stack
    }
  }
}
"""


class ValmiDagsterClient(DagsterGraphQLClient):
    # sanitise uuid
    def su(self, uuid: UUID4) -> str:
        return str(uuid).replace("-", "_")

    # desanitise uuid
    def du(self, uuid_str: str) -> UUID4:
        return uuid.UUID(uuid_str.replace("_", "-"))

    def terminate_run_force(self, run_id: str):
        """Terminates a pipeline run. This method it is useful when you would like to stop a pipeline run
        based on a external event.

        Args:
            run_id (str): The run id of the pipeline run to terminate
        """
        check.str_param(run_id, "run_id")

        res_data: Dict[str, Dict[str, Any]] = self._execute(
            TERMINATE_RUN_JOB_MUTATION, {"runId": run_id}
        )

        query_result: Dict[str, Any] = res_data["terminateRun"]
        query_result_type: str = query_result["__typename"]
        if query_result_type == "TerminateRunSuccess":
            return

        elif query_result_type == "RunNotFoundError":
            raise DagsterGraphQLClientError("RunNotFoundError", f"Run Id {run_id} not found")
        else:
            raise DagsterGraphQLClientError(query_result_type, query_result["message"])
