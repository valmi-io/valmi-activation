from fastapi import HTTPException
import sqlalchemy
from sqlalchemy.orm import Session

from metastore.models import SyncSchedule
from api.schemas import SyncScheduleCreate
from typing import Any, Dict
from .base import BaseService


class SyncsService(BaseService[SyncSchedule, SyncScheduleCreate, Any]):
    def __init__(self, db_session: Session):
        super(SyncsService, self).__init__(SyncSchedule, db_session)

    def create(self, obj: SyncScheduleCreate) -> SyncSchedule:
        """
        sync_schedule: SyncSchedule = self.model(**obj.dict())
        self.db_session.add(sync_schedule)
        self.db_session.flush()
        self.db_session.commit()
        return sync_schedule
        """
        return super().create(obj)

    def insert_or_update_list_of_schedules(self, sync_schedules: Dict[str, SyncScheduleCreate]) -> None:
        saved_sync_schedules = (
            self.db_session.query(self.model).filter(SyncSchedule.sync_id.in_(sync_schedules.keys())).all()
        )
        # update old schedules
        for saved_schedule in saved_sync_schedules:
            new_schedule = sync_schedules[saved_schedule.sync_id]

            # keep only the last run time and update the status and run_interval
            new_schedule.last_run_at = saved_schedule.last_run_at

            self.update(saved_schedule.sync_id, new_schedule)
            del sync_schedules[saved_schedule.sync_id]

        # insert new schedules
        for new_schedule in sync_schedules.values():
            db_obj: SyncSchedule = self.model(**new_schedule.dict())
            self.db_session.add(db_obj)

        try:
            self.db_session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
