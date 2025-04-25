from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Type, List, Optional
from datetime import datetime

from app.models import User, Vehicle, MaintenanceReminder
from app.schemas.reminder import MaintenanceReminderCreate, MaintenanceReminderUpdate, MaintenanceReminderResponse
from app.utils.reminder import make_maintenance_reminder_response


def crud_create_maintenance_reminder(
        db: Session,
        current_user: User,
        maintenance_reminder: MaintenanceReminderCreate
) -> MaintenanceReminder:

    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == maintenance_reminder.vehicle_id, Vehicle.user_id == current_user.id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle ID {maintenance_reminder.vehicle_id} not found or not owned by you."
        )

    if (maintenance_reminder.last_serviced_mileage is not None and
            maintenance_reminder.last_serviced_mileage > vehicle.mileage):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Last serviced mileage({maintenance_reminder.last_serviced_mileage}) "
                   f"cannot be greater than current vehicle mileage({vehicle.mileage})"
        )

    if (maintenance_reminder.last_serviced_date is not None and
            maintenance_reminder.last_serviced_date > datetime.utcnow()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last serviced date cannot be in the future."
        )

    new_record = MaintenanceReminder(
        maintenance_type=maintenance_reminder.maintenance_type,
        details=maintenance_reminder.details,
        interval_miles=maintenance_reminder.interval_miles,
        interval_months=maintenance_reminder.interval_months,
        last_serviced_mileage=maintenance_reminder.last_serviced_mileage,
        last_serviced_date=maintenance_reminder.last_serviced_date,
        notify_before_miles=maintenance_reminder.notify_before_miles,
        notify_before_days=maintenance_reminder.notify_before_days,
        is_active=maintenance_reminder.is_active,
        vehicle_id=maintenance_reminder.vehicle_id
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def base_maintenance_reminders_query(db: Session, current_user: User, load_vehicle: bool = False):
    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    user_vehicle_ids = select(Vehicle.id).where(Vehicle.user_id == current_user.id)

    query = db.query(MaintenanceReminder)

    if load_vehicle:
        query = query.join(Vehicle).options(joinedload(MaintenanceReminder.vehicle))

    query = query.filter(MaintenanceReminder.vehicle_id.in_(user_vehicle_ids))
    query = query.order_by(MaintenanceReminder.created_at.asc())

    return query


def crud_fetch_all_maintenance_reminders(db: Session, current_user: User) -> dict:
    query = base_maintenance_reminders_query(db=db, current_user=current_user)
    return {"reminders": query.all()}


def crud_fetch_all_maintenance_reminders_filtered(
        db: Session,
        current_user: User,
        vehicle_id: Optional[int],
        maintenance_type: Optional[str],
        details: Optional[str],
        interval_miles: Optional[int],
        interval_months: Optional[int],
        last_serviced_mileage: Optional[int],
        last_serviced_date: Optional[datetime],
        notify_before_miles: Optional[int],
        notify_before_days: Optional[int],
        is_active: Optional[bool],
        vehicle_make: Optional[str],
        vehicle_model: Optional[str],
        vehicle_year: Optional[int],
        vehicle_vin: Optional[str],
        vehicle_nickname: Optional[str]
) -> dict:

    filters = {
        "vehicle_id": vehicle_id,
        "maintenance_type": maintenance_type,
        "details": details,
        "interval_miles": interval_miles,
        "interval_months": interval_months,
        "last_serviced_mileage": last_serviced_mileage,
        "last_serviced_date": last_serviced_date,
        "notify_before_miles": notify_before_miles,
        "notify_before_days": notify_before_days,
        "is_active": is_active,
        "make": vehicle_make,
        "model": vehicle_model,
        "year": vehicle_year,
        "vin": vehicle_vin,
        "nickname": vehicle_nickname
    }

    if all(value is None for value in filters.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one filter parameter must be provided."
        )

    query = base_maintenance_reminders_query(db=db, current_user=current_user, load_vehicle=True)

    for attr, value in filters.items():
        if value is None:
            continue

        if hasattr(MaintenanceReminder, attr):
            column = getattr(MaintenanceReminder, attr)
        elif hasattr(Vehicle, attr):
            column = getattr(Vehicle, attr)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filter field: '{attr}'"
            )

        if isinstance(value, str):
            query = query.filter(column.ilike(f"%{value}%"))
        else:
            query = query.filter(column == value)

    return {"reminders": query.all()}


def crud_update_maintenance_reminder(
        db: Session,
        current_user: User,
        maintenance_reminder_id: int,
        update_data: MaintenanceReminderUpdate
) -> dict:

    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    reminder = db.query(MaintenanceReminder).filter(MaintenanceReminder.id == maintenance_reminder_id).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder: {maintenance_reminder_id} not found"
        )

    if reminder.vehicle_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this record."
        )

    old_data = make_maintenance_reminder_response(maintenance_reminder=reminder)

    excluded_fields = {"id", "created_at", "updated_at"}
    changes = {
        field: False for field in MaintenanceReminderResponse.model_fields.keys() if field not in excluded_fields
    }

    for field, value in update_data.dict(exclude_unset=True).items():
        if value == getattr(reminder, field):
            continue
        setattr(reminder, field, value)
        changes[field] = True

    if not any(changes.values()):
        return {
            "old_data": old_data,
            "updated_data": old_data,
            "changes": changes,
            "update_message": f"No updates were made to Maintenance Record ID {maintenance_reminder_id}."
        }

    db.commit()
    db.refresh(reminder)

    updated_data = make_maintenance_reminder_response(reminder)

    update_message = f"Maintenance Record ID {maintenance_reminder_id} updated successfully."

    return {"old_data": old_data, "updated_data": updated_data, "changes": changes, "update_message": update_message}


def crud_delete_maintenance_reminder(db: Session, current_user: User, maintenance_reminder_id: int) -> dict:
    reminder = db.query(MaintenanceReminder).filter(MaintenanceReminder.id == maintenance_reminder_id).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance Reminder not found."
        )

    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == reminder.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to delete reminder for Vehicle ID {reminder.vehicle_id}."
        )

    db.delete(reminder)
    db.commit()

    return {
        "id": maintenance_reminder_id,
        "message": f"Maintenance Record ID: {maintenance_reminder_id} deleted successfully."
    }

