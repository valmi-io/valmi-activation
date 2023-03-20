from api.schemas import MetricBase
from api.services import MetricsService
from metastore.models import SyncRun


def to_camel(string: str) -> str:
    if "_" not in string:
        return string
    words = string.split("_")
    words = [words[0]] + [word.capitalize() for word in words[1:]]
    return "".join(words)


def assign_metrics_to_run(sync_run: SyncRun, metric_service: MetricsService) -> SyncRun:
    if not sync_run.metrics:
        metrics = metric_service.get_metrics(MetricBase(run_id=sync_run.run_id, sync_id=sync_run.sync_id))
        if metrics:
            sync_run.metrics = metrics
    return sync_run
