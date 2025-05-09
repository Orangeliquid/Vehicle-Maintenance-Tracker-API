from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User
from app.utils.security import get_current_user
from app.schemas.vehicles import VehicleCreate, VehicleCreateResponse, VehicleListResponse, VehicleUpdate
from app.schemas.vehicles import VehicleUpdateResponse, VehicleDeleteResponse
from app.crud.vehicles import crud_register_new_vehicle, crud_fetch_user_vehicles, crud_filter_user_vehicles
from app.crud.vehicles import crud_update_vehicle, crud_delete_vehicle

router = APIRouter()


@router.post("/vehicles/", response_model=VehicleCreateResponse)
def register_new_vehicle(
        vehicle_create: VehicleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    return crud_register_new_vehicle(db=db, vehicle_create=vehicle_create, current_user=current_user)


@router.get("/vehicles/", response_model=VehicleListResponse)
def fetch_user_vehicles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_fetch_user_vehicles(db=db, current_user=current_user)


@router.get("/vehicles/filtered/", response_model=VehicleListResponse)
def fetch_user_vehicles_filtered(
    vehicle_type: Optional[str] = Query(None),
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    mileage: Optional[int] = Query(None),
    vin: Optional[str] = Query(None),
    license_plate: Optional[str] = Query(None),
    registration_state: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    transmission_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    nickname: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_filter_user_vehicles(
        db=db,
        current_user=current_user,
        vehicle_type=vehicle_type,
        make=make,
        model=model,
        color=color,
        year=year,
        mileage=mileage,
        vin=vin,
        license_plate=license_plate,
        registration_state=registration_state,
        fuel_type=fuel_type,
        transmission_type=transmission_type,
        is_active=is_active,
        nickname=nickname
    )


@router.put("/vehicles/{vehicle_id}", response_model=VehicleUpdateResponse)
def update_vehicle(
        vehicle_id: int,
        update_data: VehicleUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_update_vehicle(db=db, current_user=current_user, vehicle_id=vehicle_id, update_data=update_data)


@router.delete("/vehicles/{vehicle_id}/", response_model=VehicleDeleteResponse)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_delete_vehicle(db=db, current_user=current_user, vehicle_id=vehicle_id)
