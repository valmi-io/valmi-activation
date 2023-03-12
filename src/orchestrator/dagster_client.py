import uuid
from dagster_graphql import DagsterGraphQLClient
from pydantic import UUID4


class ValmiDagsterClient(DagsterGraphQLClient):
    # sanitise uuid
    def su(self, uuid: UUID4) -> str:
        return str(uuid).replace("-", "_")

    # desanitise uuid
    def du(self, uuid_str: str) -> UUID4:
        return uuid.UUID(uuid_str.replace("_", "-"))
