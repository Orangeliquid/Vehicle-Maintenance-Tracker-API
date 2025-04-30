from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User
from app.utils.security import get_current_user
from app.schemas.statistics import UserMaintenanceStatsResponse
from app.crud.statistics import crud_fetch_user_maintenance_statistics


router = APIRouter()


@router.get("/statistics/", response_model=UserMaintenanceStatsResponse)
def get_user_maintenance_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_fetch_user_maintenance_statistics(db=db, current_user=current_user)
