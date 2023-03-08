# Metric Server - API to query metrics of the runs
# Finalizer of the jobs stores summary metrics in the db
# metrics of the running jobs are in memory :: aggregated until the last checkpoint
# serve samples from intermediate_storage


import time
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

    def get_metrics(self, sync_id: UUID4, run_id: UUID4, ingore_chunk_id: UUID4 = None) -> dict[str, int]:
        # get the metrics of the run
        # deduplicate by chunk_id and return
        ignore_clause = " AND s.chunk_id != '%s'" % ingore_chunk_id if ingore_chunk_id else ""
        aggregated_metrics = self.con.sql(
            f"SELECT metric_type, SUM(count) as count \
                FROM {METRICS_TABLE} m2 INNER JOIN \
                        ( SELECT s.chunk_id AS chunk_id, max(m.created_at) AS created_at \
                        FROM {METRICS_TABLE} m INNER JOIN {SYNC_INFO_TABLE} s ON s.chunk_id = m.chunk_id \
                        WHERE s.sync_id = '{sync_id}' AND s.run_id = '{run_id}' \
                            {ignore_clause} \
                        GROUP BY s.chunk_id ) deduped_chunks \
                    ON m2.chunk_id = deduped_chunks.chunk_id AND \
                        m2.created_at = deduped_chunks.created_at\
            GROUP BY metric_type"
        ).fetchall()
        return {x: y for x, y in aggregated_metrics}

    def put_metrics(
        self, sync_id: UUID4, connector_id: UUID4, run_id: UUID4, chunk_id: UUID4, metrics: dict[str, str | int]
    ):
        """
        DISABLE AGGREGATION IF IT IS SLOW
        """
        # aggregate for every MAX chunks
        MAX = 10
        sync_info = self.con.sql(
            f"SELECT COUNT(*) FROM {SYNC_INFO_TABLE} WHERE sync_id = '{sync_id}' \
                        AND run_id = '{run_id}' AND connector_id= '{connector_id}'"
        ).fetchone()
        if sync_info[0] > MAX:
            print("AGGREGATING")
            # new chunk
            # aggregate until the last checkpoint
            old_metrics = self.get_metrics(sync_id=sync_id, run_id=run_id, ingore_chunk_id=chunk_id)
            if len(old_metrics.keys()) > 0:
                self.con.begin()
                self.con.sql(
                    f"DELETE FROM {SYNC_INFO_TABLE} WHERE sync_id = '{sync_id}' \
                        AND run_id = '{run_id}' AND connector_id= '{connector_id}'"
                )
                self.con.sql(f"DELETE FROM {METRICS_TABLE} WHERE chunk_id = '{chunk_id}'")
                # generate CHUNK_ID
                self._insert_metrics(sync_id, connector_id, run_id, uuid.uuid4(), old_metrics)
                self.con.commit()

        self.con.begin()
        self._insert_metrics(sync_id, connector_id, run_id, chunk_id, metrics)
        self.con.commit()

    def _insert_metrics(
        self, sync_id: UUID4, connector_id: UUID4, run_id: UUID4, chunk_id: UUID4, metrics: dict[str, str | int]
    ):
        # put the metrics of the run
        now = datetime.now()
        inserts = []

        for metric_type, count in metrics.items():
            inserts.append(f"('{chunk_id}','{metric_type}','{count}','{now}')")

        self.con.sql(
            f"INSERT INTO {SYNC_INFO_TABLE} VALUES \
                ('{sync_id}', '{connector_id}', '{run_id}','{chunk_id}', '{now}') \
                    ON CONFLICT DO NOTHING"
        )
        self.con.sql(f"INSERT INTO {METRICS_TABLE} VALUES {', '.join(inserts)}")

    def get_samples(self, sync_id: UUID4, run_id: UUID4):
        # get the samples from the intermediate store
        pass

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
                metric_type = random.choice(["failed", "succeeded"])
                # count = random.choice(range(0, 1000))
                count = 2
                metrics.put_metrics(sync_id, connector_id, run_id, chunk_id, {metric_type: count})

                # inserting again to test deduplication
                time.sleep(0.001)
                count = 1

                metrics.put_metrics(sync_id, connector_id, run_id, chunk_id, {metric_type: count})

            print(f"{sync_id} {run_id} {chunk_id}")
        # print(metrics.get_metrics(sync_id, run_id))

    print(metrics.get_metrics(sync_id, run_id))
    print("db size: ", metrics.size())
    # metrics.finalise()
