from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User
from app.utils.security import get_current_user

from app.schemas.reminder import MaintenanceReminderCreateResponse, MaintenanceReminderCreate
from app.schemas.reminder import MaintenanceReminderListResponse, MaintenanceReminderDeleteResponse
from app.schemas.reminder import MaintenanceReminderUpdateResponse, MaintenanceReminderUpdate
from app.crud.reminder import crud_create_maintenance_reminder, crud_fetch_all_maintenance_reminders
from app.crud.reminder import crud_delete_maintenance_reminder, crud_fetch_all_maintenance_reminders_filtered
from app.crud.reminder import crud_update_maintenance_reminder

router = APIRouter()


@router.post("/reminders/", response_model=MaintenanceReminderCreateResponse)
def create_maintenance_reminder(
        maintenance_reminder: MaintenanceReminderCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_create_maintenance_reminder(
        db=db,
        current_user=current_user,
        maintenance_reminder=maintenance_reminder
    )


@router.get("/reminders/", response_model=MaintenanceReminderListResponse)
def fetch_all_maintenance_reminders(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return crud_fetch_all_maintenance_reminders(
        db=db,
        current_user=current_user
    )


@router.get("/reminders/filtered/", response_model=MaintenanceReminderListResponse)
def fetch_all_maintenance_reminders_filtered(
        vehicle_id: Optional[int] = Query(None),
        maintenance_type: Optional[str] = Query(None),
        details: Optional[str] = Query(None),
        interval_miles: Optional[int] = Query(None),
        interval_months: Optional[int] = Query(None),
        last_serviced_mileage: Optional[int] = Query(None),
        last_serviced_date: Optional[datetime] = Query(None),
        notify_before_miles: Optional[int] = Query(None),
        notify_before_days: Optional[int] = Query(None),
        is_active: Optional[bool] = Query(None),
        vehicle_make: Optional[str] = Query(None),
        vehicle_model: Optional[str] = Query(None),
        vehicle_year: Optional[int] = Query(None),
        vehicle_vin: Optional[str] = Query(None),
        vehicle_nickname: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_fetch_all_maintenance_reminders_filtered(
        vehicle_id=vehicle_id,
        maintenance_type=maintenance_type,
        details=details,
        interval_miles=interval_miles,
        interval_months=interval_months,
        last_serviced_mileage=last_serviced_mileage,
        last_serviced_date=last_serviced_date,
        notify_before_miles=notify_before_miles,
        notify_before_days=notify_before_days,
        is_active=is_active,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        vehicle_year=vehicle_year,
        vehicle_vin=vehicle_vin,
        vehicle_nickname=vehicle_nickname,
        db=db,
        current_user=current_user
    )


@router.put("/reminder/", response_model=MaintenanceReminderUpdateResponse)
def update_maintenance_reminder(
        maintenance_reminder_id: int,
        update_data: MaintenanceReminderUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_update_maintenance_reminder(
        maintenance_reminder_id=maintenance_reminder_id,
        update_data=update_data,
        db=db,
        current_user=current_user
    )


@router.delete("/reminder/", response_model=MaintenanceReminderDeleteResponse)
def delete_maintenance_reminder(
        maintenance_reminder_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_delete_maintenance_reminder(
        db=db,
        current_user=current_user,
        maintenance_reminder_id=maintenance_reminder_id
    )
