from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User
from app.utils.security import get_current_user
from app.schemas.maintenance import MaintenanceCreate, MaintenanceCreateResponse, MaintenanceListResponse
from app.schemas.maintenance import MaintenanceUpdate, MaintenanceUpdateResponse, MaintenanceDeleteResponse
from app.crud.maintenance import crud_create_maintenance_record, crud_fetch_all_vehicle_maintenance_records
from app.crud.maintenance import crud_fetch_all_vehicle_maintenance_records_filtered, crud_update_maintenance_record
from app.crud.maintenance import crud_delete_maintenance_record


router = APIRouter()


@router.post("/maintenance_records/", response_model=MaintenanceCreateResponse)
def create_maintenance_record(
        maintenance_create: MaintenanceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_create_maintenance_record(db=db, current_user=current_user, maintenance_create=maintenance_create)


@router.get("/maintenance_records/", response_model=MaintenanceListResponse)
def fetch_all_vehicle_maintenance_records(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_fetch_all_vehicle_maintenance_records(db=db, current_user=current_user)


@router.get("/maintenance_records/filtered/", response_model=MaintenanceListResponse)
def fetch_all_vehicle_maintenance_records_filtered(
        vehicle_id: Optional[int] = Query(None),
        maintenance_provider: Optional[str] = Query(None),
        maintenance_type: Optional[str] = Query(None),
        description: Optional[str] = Query(None),
        mileage: Optional[int] = Query(None),
        cost: Optional[float] = Query(None),
        serviced_at: Optional[datetime] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_fetch_all_vehicle_maintenance_records_filtered(
        vehicle_id=vehicle_id,
        maintenance_provider=maintenance_provider,
        maintenance_type=maintenance_type,
        description=description,
        mileage=mileage,
        cost=cost,
        serviced_at=serviced_at,
        db=db,
        current_user=current_user
    )


@router.put("/maintenance_records/", response_model=MaintenanceUpdateResponse)
def update_maintenance_record(
        maintenance_record_id: int,
        update_data: MaintenanceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_update_maintenance_record(
        db=db,
        current_user=current_user,
        maintenance_record_id=maintenance_record_id,
        update_data=update_data
    )


@router.delete("/maintenance_records/", response_model=MaintenanceDeleteResponse)
def delete_maintenance_record(
        maintenance_record_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_delete_maintenance_record(db=db, current_user=current_user, maintenance_record_id=maintenance_record_id)
