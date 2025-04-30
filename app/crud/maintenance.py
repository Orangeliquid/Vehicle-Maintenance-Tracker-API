from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime

from app.models import User, Vehicle, MaintenanceRecord
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse
from app.utils.maintenance import make_maintenance_response


def crud_create_maintenance_record(
        db: Session,
        current_user: User,
        maintenance_create: MaintenanceCreate
) -> MaintenanceRecord:

    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == maintenance_create.vehicle_id, Vehicle.user_id == current_user.id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle ID {maintenance_create.vehicle_id} not found or not owned by you."
        )

    if maintenance_create.mileage < vehicle.mileage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maintenance mileage({maintenance_create.mileage}) "
                   f"cannot be less than current vehicle mileage({vehicle.mileage})"
        )

    if maintenance_create.mileage > vehicle.mileage:
        vehicle.mileage = maintenance_create.mileage

    new_record = MaintenanceRecord(
        vehicle_id=vehicle.id,
        maintenance_provider=maintenance_create.maintenance_provider,
        maintenance_type=maintenance_create.maintenance_type,
        description=maintenance_create.description,
        mileage=maintenance_create.mileage,
        cost=maintenance_create.cost,
        serviced_at=maintenance_create.serviced_at
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def base_maintenance_records_query(db: Session, current_user: User):
    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    user_vehicle_ids = select(Vehicle.id).where(Vehicle.user_id == current_user.id)

    query = (
        db.query(MaintenanceRecord)
        .options(joinedload(MaintenanceRecord.vehicle))
        .filter(MaintenanceRecord.vehicle_id.in_(user_vehicle_ids))
        .order_by(MaintenanceRecord.created_at.asc())
    )
    return query


def crud_fetch_all_vehicle_maintenance_records(db: Session, current_user: User) -> dict:
    query = base_maintenance_records_query(db=db, current_user=current_user)
    return {"maintenance": query.all()}


def crud_fetch_all_vehicle_maintenance_records_filtered(
        db: Session,
        current_user: User,
        vehicle_id: Optional[int],
        maintenance_provider: Optional[str],
        maintenance_type: Optional[str],
        description: Optional[str],
        mileage: Optional[int],
        cost: Optional[float],
        serviced_at: Optional[datetime]
) -> dict:

    filters = {
        "vehicle_id": vehicle_id,
        "maintenance_provider": maintenance_provider,
        "maintenance_type": maintenance_type,
        "description": description,
        "mileage": mileage,
        "cost": cost,
        "serviced_at": serviced_at
    }

    if all(value is None for value in filters.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one filter parameter must be provided."
        )

    query = base_maintenance_records_query(db=db, current_user=current_user)

    for attr, value in filters.items():
        if value is not None:
            column = getattr(MaintenanceRecord, attr)
            if isinstance(value, str):
                query = query.filter(column.ilike(f"%{value}%"))
            else:
                query = query.filter(column == value)

    return {"maintenance": query.all()}


def crud_update_maintenance_record(
        db: Session,
        current_user: User,
        maintenance_record_id: int,
        update_data: MaintenanceUpdate
) -> dict:

    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == maintenance_record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found."
        )

    if record.vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this record."
        )

    old_data = make_maintenance_response(maintenance_record=record)

    excluded_fields = {"id", "created_at", "updated_at"}
    changes = {field: False for field in MaintenanceResponse.model_fields.keys() if field not in excluded_fields}

    for field, value in update_data.dict(exclude_unset=True).items():
        if value == getattr(record, field):
            continue
        setattr(record, field, value)
        changes[field] = True

    if not any(changes.values()):
        return {
            "old_data": old_data,
            "updated_data": old_data,
            "changes": changes,
            "update_message": f"No updates were made to Maintenance Record ID {maintenance_record_id}."
        }

    db.commit()
    db.refresh(record)

    updated_data = make_maintenance_response(record)

    update_message = f"Maintenance Record ID {maintenance_record_id} updated successfully."

    return {"old_data": old_data, "updated_data": updated_data, "changes": changes, "update_message": update_message}


def crud_delete_maintenance_record(db: Session, current_user: User, maintenance_record_id: int) -> dict:
    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == maintenance_record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found."
        )

    if record.vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this record."
        )

    db.delete(record)
    db.commit()

    return {
        "id": maintenance_record_id,
        "message": f"Maintenance Record ID: {maintenance_record_id} deleted successfully."
    }
