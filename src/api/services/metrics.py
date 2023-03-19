from vyper import v
from api.schemas import MetricCreate, MetricBase
from metrics.metric_store import Metrics


class MetricsService(object):
    def __init__(self):
        self.metrics = Metrics(delete_db=v.get_bool("DELETE_METRICS_DB"))

    def create(self, obj: MetricCreate) -> None:
        self.metrics.put_metrics(**obj.dict())

    def get_metrics(self, obj: MetricBase) -> dict[str, dict[str | int]]:
        return self.metrics.get_metrics(**obj.dict())

    def shutdown(self):
        self.metrics.shutdown()
