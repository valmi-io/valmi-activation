from vyper import v
from api.schemas import MetricCreate, MetricBase
from metrics import Metrics


class MetricsService(object):
    def __init__(self):
        self.metrics = Metrics(delete_db=v.get_bool("DELETE_METRICS_DB"))

    def create(self, obj: MetricCreate) -> None:
        """
        sync_schedule: SyncSchedule = self.model(**obj.dict())
        self.db_session.add(sync_schedule)
        self.db_session.flush()
        self.db_session.commit()
        return sync_schedule
        """
        self.metrics.put_metrics(**obj.dict())

    def get_metrics(self, obj: MetricBase) -> dict[str, dict[str | int]]:
        return self.metrics.get_metrics(**obj.dict())
