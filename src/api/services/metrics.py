from sqlalchemy.orm import Session
from vyper import v
from api.schemas import MetricCreate, Metric
from metrics.metrics import Metrics


class MetricsService(object):
    def __init__(self, db_session: Session):
        self.metrics = Metrics(delete_db=v.get_bool("DELETE_METRICS_DB"))

    def create(self, obj: MetricCreate) -> Metric:
        """
        sync_schedule: SyncSchedule = self.model(**obj.dict())
        self.db_session.add(sync_schedule)
        self.db_session.flush()
        self.db_session.commit()
        return sync_schedule
        """
        return self.metrics.put_metrics(**obj.dict())
