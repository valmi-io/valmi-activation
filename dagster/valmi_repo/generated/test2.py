import os

from dagster import DefaultScheduleStatus, ScheduleDefinition, graph, op


@op
def hello():
    return 1


@op
def goodbye(foo):
    if foo != 1:
        raise Exception("Bad io manager")
    return foo * 2


def job():
    @graph
    def my_graph():
        goodbye(hello())

    return my_graph.to_job(name=os.path.basename(__file__)[:-3].capitalize())


def schedule():
    return ScheduleDefinition(
        cron_schedule="0 0 * * *",
        job=job(),
        default_status=DefaultScheduleStatus.RUNNING,
        execution_timezone="US/Central",
    )
