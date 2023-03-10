from datetime import datetime
from fastapi import HTTPException
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import func

from metastore.models import SyncSchedule, SyncRun
from api.schemas import SyncScheduleCreate, SyncRunCreate
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.sql.functions import concat
from typing import Any, Dict, List

from metastore.models import SyncConfigStatus, SyncStatus
from .base import BaseService
from datetime import datetime
from sqlalchemy import or_, and_


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

            # update saved objects
            db_obj = self.get(new_schedule.sync_id)
            for column, value in new_schedule.dict(exclude_unset=True).items():
                setattr(db_obj, column, value)
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

    def update_sync_and_create_run(self, sync: SyncSchedule, run: SyncRunCreate) -> None:
        db_obj: SyncRun = SyncRun(**run.dict())
        self.db_session.add(db_obj)
        try:
            self.db_session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e

    def update_sync_and_run(self, sync: SyncSchedule, run: SyncRun) -> None:
        try:
            self.db_session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e

    def get_syncs_to_run(self) -> List[SyncSchedule]:
        return (
            self.db_session.query(self.model)
            .filter(
                or_(
                    and_(
                        SyncSchedule.status == SyncConfigStatus.ACTIVE,
                        or_(
                            SyncSchedule.run_status == SyncStatus.FAILED,
                            SyncSchedule.run_status == SyncStatus.RUNNING,
                            SyncSchedule.run_status == SyncStatus.SCHEDULED,
                            and_(
                                (datetime.now() - SyncSchedule.last_run_at)
                                >= SyncSchedule.run_interval * func.cast(concat(1, " millisecond"), INTERVAL),
                                SyncSchedule.run_status == SyncStatus.STOPPED,
                            ),
                        ),
                    ),
                    and_(
                        SyncSchedule.status != SyncConfigStatus.ACTIVE, SyncSchedule.run_status == SyncStatus.RUNNING
                    ),
                )
            )
            .all()
        )
