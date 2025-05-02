from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
from datetime import datetime

from app.schemas.vehicles import VehicleSummary


class MaintenanceBase(BaseModel):
    maintenance_provider: Optional[str] = Field(None, example="Valvoline")
    maintenance_type: str = Field(None, example="Oil Change")
    description: Optional[str] = Field(None, example="Changed to synthetic oil.")
    mileage: int = Field(None, example=133150)
    cost: float = Field(None, example=89.56)
    serviced_at: Optional[datetime] = Field(None, example="2024-04-10T10:00:00")

    @field_validator('mileage', 'cost', mode='before')
    def validate_positive_fields(cls, v, field):
        if v is not None and v < 0:
            raise ValueError(f'{field.name.capitalize()} cannot be negative.')
        return v

    class Config:
        from_attributes = True


class MaintenanceCreate(MaintenanceBase):
    vehicle_id: int


class MaintenanceCreateResponse(MaintenanceBase):
    id: int
    vehicle_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceResponse(MaintenanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    vehicle: VehicleSummary

    class Config:
        from_attributes = True


class MaintenanceListResponse(BaseModel):
    maintenance: List[MaintenanceResponse]


class MaintenanceUpdate(MaintenanceBase):
    maintenance_type: Optional[str] = None
    maintenance_provider: Optional[str] = None
    description: Optional[str] = None
    mileage: Optional[int] = None
    cost: Optional[float] = None
    serviced_at: Optional[datetime] = None


class MaintenanceUpdateResponse(BaseModel):
    old_data: MaintenanceResponse
    updated_data: MaintenanceResponse
    changes: dict
    update_message: str


class MaintenanceDeleteResponse(BaseModel):
    id: int
    message: str
