"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Thursday, March 9th 2023, 1:39:35 pm
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
from sqlalchemy import or_, and_
import threading


class SyncsService(BaseService[SyncSchedule, SyncScheduleCreate, Any]):
    def __init__(self, db_session: Session):
        super(SyncsService, self).__init__(SyncSchedule, db_session)
        self._api_and_run_manager_mutex = threading.RLock()

    @property
    def api_and_run_manager_mutex(self):
        return self._api_and_run_manager_mutex
    
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
            new_schedule.last_run_at = datetime(1970, 1, 1)
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
        except Exception as e:
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
                            SyncSchedule.run_status == SyncStatus.ABORTING,
                            and_(
                                (datetime.now() - SyncSchedule.last_run_at)
                                >= SyncSchedule.run_interval * func.cast(concat(1, " millisecond"), INTERVAL),
                                SyncSchedule.run_status == SyncStatus.STOPPED,
                            ),
                        ),
                    ),
                    and_(
                        SyncSchedule.status != SyncConfigStatus.ACTIVE,
                        or_(
                            SyncSchedule.run_status == SyncStatus.ABORTING,
                            SyncSchedule.run_status == SyncStatus.RUNNING,
                        ),
                    ),
                )
            )
            .all()
        )

    def get_sync(self, sync_id) -> SyncSchedule: 
        return self.db_session.query(self.model).filter(SyncSchedule.sync_id == sync_id).first()