import os

from dagster_docker import docker_container_op

from dagster import DefaultScheduleStatus, ScheduleDefinition, graph, op

first_op = docker_container_op.configured(
    {
        "image": "valmi/source-postgres:dev",
        "command": ["spec"],
    },
    name="first_op",
)
second_op = docker_container_op.configured(
    {
        "image": "valmi/destination-webhook:dev",
        "command": ["spec"],
    },
    name="second_op",
)


@op
def finalizer(context, a, b) -> None:
    context.log.info("finalizer")


def job():
    @graph
    def inputs_and_outputs():
        a = first_op()
        b = second_op()
        finalizer(a, b)

    return inputs_and_outputs.to_job(name=os.path.basename(__file__)[:-3].capitalize())


def schedule():
    return ScheduleDefinition(
        cron_schedule="0 0 * * *",
        job=job(),
        default_status=DefaultScheduleStatus.RUNNING,
        execution_timezone="US/Central",
    )
