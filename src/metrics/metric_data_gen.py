import uuid
import duckdb
import random


def main():
    con = duckdb.connect("metrics.db")
    # create a table and load data into it
    con.sql("DROP TABLE IF EXISTS metrics")
    con.sql(
        "CREATE TABLE metrics (sync_id VARCHAR, connector_id VARCHAR, run_id VARCHAR,\
              chunk_id VARCHAR, metric_type VARCHAR, count BIGINT)"
    )

    inserts = []
    for i in range(0, 100):
        sync_id = uuid.uuid4()
        connector_id = random.choice(["SRC", "DEST"])
        for j in range(0, 100):
            run_id = uuid.uuid4()
            for k in range(0, 100):
                chunk_id = uuid.uuid4()
                metric_type = random.choice(["failed", "succeeded"])
                count = random.choice(range(0, 1000))
                print((i) * 100 * 100 + (j) * 100 + (k + 1), " of 1000000")
                inserts.append(
                    f"('{sync_id}', '{connector_id}', '{run_id}',\
                        '{chunk_id}','{metric_type}','{count}')"
                )

    con.sql(f"INSERT INTO metrics VALUES {', '.join(inserts)}")
    con.table("metrics").show()


if __name__ == "__main__":
    main()
