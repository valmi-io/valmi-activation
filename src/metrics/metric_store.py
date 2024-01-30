"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, March 8th 2023, 11:38:42 am
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
"""

# TODO: serve samples from intermediate_storage


from pydantic.types import UUID4
import duckdb
import uuid
import random
from datetime import datetime

METRICS_TABLE = "metrics"
DB_NAME = "/data/valmi_metrics.db"

MAGIC_CHUNK_ID = 2**31 - 1


class Metrics:
    __initialized = False

    def __new__(cls, delete_db=False, *args, **kwargs) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(
                Metrics,
                cls,
            ).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, delete_db=False, *args, **kwargs) -> None:
        if Metrics.__initialized:
            return

        Metrics.__initialized = True
        self.con = duckdb.connect(DB_NAME)

        metric_table_found = False
        if delete_db:
            self.con.execute(f"DROP TABLE IF EXISTS {METRICS_TABLE}")
        else:
            self.con.execute("SHOW TABLES")
            tables = self.con.fetchall()

            for table in tables:
                if table[0] == METRICS_TABLE:
                    metric_table_found = True

        if not metric_table_found:
            self.con.sql(
                f"CREATE TABLE {METRICS_TABLE} (sync_id VARCHAR, connector_id VARCHAR, run_id VARCHAR, \
                    chunk_id BIGINT, metric_type VARCHAR,\
                    count BIGINT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )

    def clear_metrics(self, sync_id: UUID4, run_id: UUID4) -> None:
        try:
            self.con.sql(f"DELETE FROM {METRICS_TABLE} WHERE sync_id = '{sync_id}' AND run_id = '{run_id}'")
        except Exception as e:
            self.con.rollback()
            raise e

    def get_metrics(self, sync_id: UUID4, run_id: UUID4, ingore_chunk_id: int = None) -> dict[str, dict[str, int]]:
        # get the metrics of the run
        # deduplicate by chunk_id and return
        try:
            ignore_clause = " AND m.chunk_id != %s" % ingore_chunk_id if ingore_chunk_id is not None else ""
            aggregated_metrics = self.con.sql(
                f"SELECT deduped_chunks.connector_id AS connector_id,  deduped_chunks.metric_type AS metric_type, SUM(count) as count \
                    FROM {METRICS_TABLE} m2 RIGHT JOIN \
                            ( SELECT m.connector_id AS connector_id, m.chunk_id AS chunk_id, m.metric_type as metric_type, max(m.created_at) AS created_at \
                            FROM {METRICS_TABLE} m \
                            WHERE m.sync_id = '{sync_id}' AND m.run_id = '{run_id}' \
                                {ignore_clause} \
                            GROUP BY  m.connector_id, m.chunk_id, m.metric_type ) deduped_chunks \
                        ON m2.chunk_id = deduped_chunks.chunk_id AND \
                            m2.created_at = deduped_chunks.created_at AND \
                            m2.connector_id = deduped_chunks.connector_id AND \
                            m2.metric_type = deduped_chunks.metric_type \
                    WHERE sync_id = '{sync_id}' AND run_id = '{run_id}' \
                    GROUP BY  deduped_chunks.connector_id, deduped_chunks.metric_type"
            ).fetchall()

            ret_map = {}
            for x, y, z in aggregated_metrics:
                # print(x, y, z)
                metric_map = ret_map.get(x, {})
                ret_map[x] = metric_map
                metric_map[y] = z
            return ret_map
        except Exception as e:
            self.con.rollback()
            raise e

    def put_metrics(
        self, sync_id: UUID4, connector_id: UUID4, run_id: UUID4, chunk_id: int, metrics: dict[str, int], **kwargs
    ) -> None:
        try:
            """
            DISABLE AGGREGATION IF IT IS SLOW
            """
            # aggregate for every MAX chunks
            MAX = 10
            sync_info = self.con.sql(
                f"SELECT COUNT(*) FROM {METRICS_TABLE} WHERE sync_id = '{sync_id}' \
                            AND run_id = '{run_id}' AND connector_id= '{connector_id}'"
            ).fetchone()
            if (
                False and sync_info[0] > MAX
            ):  # TODO: Disabling aggregation until we inject state into connectors, otherwise metrics are counted multiple times when connectors are retried
                print("AGGREGATING")
                # aggregate ignoring the latest chunk
                old_metrics = self.get_metrics(sync_id=sync_id, run_id=run_id, ingore_chunk_id=chunk_id)
                print("old metrics below")
                print(old_metrics)
                for conn, old_metric in old_metrics.items():
                    if len(old_metric.keys()) > 0 and conn == connector_id:
                        self.con.begin()
                        self.con.sql(
                            f"DELETE FROM {METRICS_TABLE} WHERE sync_id = '{sync_id}' \
                                AND run_id = '{run_id}' AND connector_id= '{connector_id}' AND chunk_id != {chunk_id}"
                        )
                        # generate CHUNK_ID
                        print("inserting magical chunk")
                        print(old_metric)
                        self._insert_metrics(sync_id, connector_id, run_id, MAGIC_CHUNK_ID, old_metric)
                        self.con.commit()

            self.con.begin()
            self._insert_metrics(sync_id, connector_id, run_id, chunk_id, metrics)
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            raise e

    def _insert_metrics(
        self, sync_id: UUID4, connector_id: UUID4, run_id: UUID4, chunk_id: int, metrics: dict[str, int]
    ):
        # put the metrics of the run
        now = datetime.now()
        inserts = []

        for metric_type, count in metrics.items():
            inserts.append(f"('{sync_id}', '{connector_id}', '{run_id}', {chunk_id},'{metric_type}',{count},'{now}')")

        print(inserts)
        if inserts:
            self.con.sql(f"INSERT INTO {METRICS_TABLE} VALUES {','.join(inserts)}")

    def get_samples(self, sync_id: UUID4, run_id: UUID4):
        # get the samples from the intermediate store
        pass

    def finalise(self, sync_id: UUID4, run_id: UUID4):
        # aggregate and store the finalised metrics into the metastore
        pass

    def size(self) -> int:
        return self.con.sql(f"SELECT COUNT(*) as count FROM {METRICS_TABLE}").fetchone()[0]

    def shutdown(self) -> None:
        self.con.close()


if __name__ == "__main__":
    metrics = Metrics(delete_db=True)
    for i in range(0, 10):
        sync_id = uuid.uuid4()
        connector_id = random.choice(["SRC", "DEST"])
        for j in range(0, 10):
            run_id = uuid.uuid4()
            for k in range(0, 100):
                chunk_id = k
                metric_type = random.choice(["failed", "succeeded"])
                # count = random.choice(range(0, 1000))
                count = 1
                metrics.put_metrics(sync_id, connector_id, run_id, chunk_id, {metric_type: count})

                # inserting again to test deduplication
                count = 2
                metrics.put_metrics(sync_id, connector_id, run_id, chunk_id, {metric_type: count})

            print(f"{sync_id} {run_id} {chunk_id}")
        # print(metrics.get_metrics(sync_id, run_id))

    print(metrics.get_metrics(sync_id, run_id))
    print("db size: ", metrics.size())
    # metrics.finalise()
