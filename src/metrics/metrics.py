# Metric Server - API to query metrics of the runs
# Finalizer of the jobs stores summary metrics in the db
# Samples will be stored in the intermediate_storage
# metrics of the running jobs are in memory :: aggregated until the last checkpoint
# Reinit metrics of running jobs on RESTART from intermediate_storage
# API to receive the last uploaded metrics from the connector about the url of the file.


from pydantic.types import UUID4
import duckdb
import uuid
import random
from datetime import datetime

METRICS_TABLE = "metrics"
SYNC_INFO_TABLE = "sync_info"
DB_NAME = "valmi_metrics.db"


class Metrics:
    def __new__(cls, delete_db=False, *args, **kwargs) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(
                Metrics,
                cls,
            ).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, delete_db=False, *args, **kwargs) -> None:
        self.con = duckdb.connect(DB_NAME)

        metric_table_found = False
        info_table_found = False
        if delete_db:
            self.con.execute(f"DROP TABLE IF EXISTS {METRICS_TABLE}")
            self.con.execute(f"DROP TABLE IF EXISTS {SYNC_INFO_TABLE}")
        else:
            self.con.execute("SHOW TABLES")
            tables = self.con.fetchall()

            for table in tables:
                if table[0] == METRICS_TABLE:
                    metric_table_found = True
                if table[0] == SYNC_INFO_TABLE:
                    info_table_found = True

        if not metric_table_found:
            self.con.sql(
                f"CREATE TABLE {METRICS_TABLE} (chunk_id VARCHAR, metric_type VARCHAR,\
                      count BIGINT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
        if not info_table_found:
            self.con.sql(
                f"CREATE TABLE {SYNC_INFO_TABLE} (sync_id VARCHAR, connector_id VARCHAR, run_id VARCHAR,\
                chunk_id VARCHAR, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, \
                PRIMARY KEY (sync_id, connector_id, run_id, chunk_id))"
            )

    def get_metrics(self, sync_id: UUID4, run_id: UUID4):
        # get the metrics of the run
        # deduplicate by chunk_id and return
        aggregated_metrics = self.con.sql(
            f"SELECT metric_type, SUM(count) as count \
                FROM {METRICS_TABLE} m2 INNER JOIN \
                        ( SELECT s.chunk_id AS chunk_id, max(m.created_at) AS created_at \
                        FROM {METRICS_TABLE} m INNER JOIN {SYNC_INFO_TABLE} s ON s.chunk_id = m.chunk_id \
                        WHERE s.sync_id = '{sync_id}' AND s.run_id = '{run_id}' \
                        GROUP BY s.chunk_id ) deduped_chunks \
                    ON m2.chunk_id = deduped_chunks.chunk_id AND \
                        m2.created_at = deduped_chunks.created_at\
            GROUP BY metric_type"
        ).fetchall()
        return {x: y for x, y in aggregated_metrics}

    def put_metrics(
        self, sync_id: UUID4, container_id: UUID4, run_id: UUID4, chunk_id: UUID4, metrics: list[dict[str, str | int]]
    ):
        # put the metrics of the run
        now = datetime.now()

        inserts = []
        for metric in metrics:
            for metric_type, count in metric.items():
                inserts.append(f"('{chunk_id}','{metric_type}','{count}','{now}')")

        self.con.begin()
        self.con.sql(
            f"INSERT INTO {SYNC_INFO_TABLE} VALUES \
                ('{sync_id}', '{connector_id}', '{run_id}','{chunk_id}', '{now}') \
                    ON CONFLICT DO NOTHING"
        )
        self.con.sql(f"INSERT INTO {METRICS_TABLE} VALUES {', '.join(inserts)}")
        self.con.commit()

    def finalise(self, sync_id: UUID4, run_id: UUID4):
        # aggregate and store the finalised metrics into the metastore
        pass

    def size(self) -> int:
        return self.con.sql(f"SELECT COUNT(*) as count FROM {METRICS_TABLE}").fetchone()[0]


if __name__ == "__main__":
    metrics = Metrics(delete_db=True)
    for i in range(0, 10):
        sync_id = uuid.uuid4()
        connector_id = random.choice(["SRC", "DEST"])
        for j in range(0, 10):
            run_id = uuid.uuid4()
            for k in range(0, 100):
                chunk_id = uuid.uuid4()
                print(f"{sync_id} {run_id} {chunk_id}")

                metric_type = random.choice(["failed", "succeeded"])
                # count = random.choice(range(0, 1000))
                count = 1
                metrics.put_metrics(sync_id, connector_id, run_id, chunk_id, [{metric_type: count}])

    print(metrics.get_metrics(sync_id, run_id))
    print("db size: ", metrics.size())
    # metrics.finalise()
