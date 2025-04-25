from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.models import Vehicle, User
from app.schemas.vehicles import VehicleCreate, VehicleUpdate, VehicleResponse
from app.utils.vehicles import make_vehicle_response


def crud_register_new_vehicle(db: Session, current_user: User, vehicle_create: VehicleCreate) -> Vehicle:
    db_vehicle_vin = db.query(Vehicle).filter(Vehicle.vin == vehicle_create.vin).first()
    if db_vehicle_vin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{vehicle_create.vin} already registered."
        )

    # Pycharm does not like '==' comparator for SQL queries - works fine at runtime
    db_vehicle_nickname = (
        db.query(Vehicle)
        .filter(Vehicle.nickname == vehicle_create.nickname, Vehicle.user_id == current_user.id)
        .first()
    )

    if db_vehicle_nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{vehicle_create.nickname}' is already being used by you."
        )

    new_vehicle = Vehicle(
        user_id=current_user.id,
        vehicle_type=vehicle_create.vehicle_type,
        make=vehicle_create.make,
        model=vehicle_create.model,
        color=vehicle_create.color,
        year=vehicle_create.year,
        mileage=vehicle_create.mileage,
        vin=vehicle_create.vin,
        license_plate=vehicle_create.license_plate,
        registration_state=vehicle_create.registration_state,
        fuel_type=vehicle_create.fuel_type,
        transmission_type=vehicle_create.transmission_type,
        is_active=vehicle_create.is_active,
        nickname=vehicle_create.nickname
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle


def crud_fetch_user_vehicles(db: Session, current_user: User) -> dict:
    return {"vehicles": db.query(Vehicle).filter_by(user_id=current_user.id).all()}

    # Pycharm doesn't like the '==' comparator but works just fine at runtime
    # return {"vehicles": db.query(Vehicle).filter(Vehicle.user_id == current_user.id).all()}


def crud_filter_user_vehicles(
    db: Session,
    current_user: User,
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    color: Optional[str] = None,
    year: Optional[int] = None,
    mileage: Optional[int] = None,
    vin: Optional[str] = None,
    license_plate: Optional[str] = None,
    registration_state: Optional[str] = None,
    fuel_type: Optional[str] = None,
    transmission_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    nickname: Optional[str] = None
) -> dict:

    filters = {
        "vehicle_type": vehicle_type,
        "make": make,
        "model": model,
        "color": color,
        "year": year,
        "mileage": mileage,
        "vin": vin,
        "license_plate": license_plate,
        "registration_state": registration_state,
        "fuel_type": fuel_type,
        "transmission_type": transmission_type,
        "is_active": is_active,
        "nickname": nickname
    }

    if all(value is None for value in filters.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one filter parameter must be provided."
        )

    # Pycharm does not like '==' comparator for SQL queries - works fine at runtime
    query = db.query(Vehicle).filter(Vehicle.user_id == current_user.id)

    for attr, value in filters.items():
        if value is not None:
            column = getattr(Vehicle, attr)
            if isinstance(value, str):
                query = query.filter(column.ilike(f"%{value}%"))
            else:
                query = query.filter(column == value)

    return {"vehicles": query.all()}


def crud_update_vehicle(db: Session, current_user: User, vehicle_id: int, update_data: VehicleUpdate) -> dict:
    # Pycharm does not like '==' comparator for SQL queries - works fine at runtime
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.user_id == current_user.id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle ID {vehicle_id} not found or not owned by you."
        )

    old_data = make_vehicle_response(vehicle)

    excluded_fields = {"id", "created_at", "updated_at"}
    changes = {field: False for field in VehicleResponse.model_fields.keys() if field not in excluded_fields}

    for field, value in update_data.dict(exclude_unset=True).items():
        if value == getattr(vehicle, field):
            continue
        setattr(vehicle, field, value)
        changes[field] = True

    if not any(changes.values()):
        return {
            "old_data": old_data,
            "updated_data": old_data,
            "changes": changes,
            "update_message": f"No updates were made to vehicle ID {vehicle_id}."
        }

    db.commit()
    db.refresh(vehicle)

    updated_data = make_vehicle_response(vehicle)

    update_message = f"Vehicle ID {vehicle_id} updated successfully."

    return {"old_data": old_data, "updated_data": updated_data, "changes": changes, "update_message": update_message}


def crud_delete_vehicle(db: Session, current_user: User, vehicle_id: int) -> dict:
    # Pycharm does not like '==' comparator for SQL queries - works fine at runtime
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.user_id == current_user.id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle ID {vehicle_id} not found or not owned by you."
        )

    db.delete(vehicle)
    db.commit()

    return {"vehicle_id": vehicle_id, "message": f"Vehicle ID: {vehicle_id} deleted successfully."}
