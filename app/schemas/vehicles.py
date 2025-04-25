from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class VehicleBase(BaseModel):
    vehicle_type: str
    make: str
    model: str
    color: str
    year: int
    mileage: int
    vin: str
    license_plate: str
    registration_state: str
    fuel_type: str
    transmission_type: str
    is_active: bool
    nickname: str

    @field_validator(
        'vehicle_type',
        'make',
        'model',
        'color',
        'registration_state',
        'fuel_type',
        'transmission_type',
        'nickname'
    )
    def capitalize_fields(cls, v):
        return v.strip().title() if v else v

    class Config:
        from_attributes = True


class VehicleSummary(BaseModel):
    id: int
    make: str
    model: str
    year: int
    vin: str
    nickname: str

    class Config:
        from_attributes = True


class VehicleCreate(VehicleBase):
    pass


class VehicleCreateResponse(VehicleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleResponse(VehicleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class VehicleListResponse(BaseModel):
    vehicles: List[VehicleResponse]


class VehicleUpdate(VehicleBase):
    vehicle_type: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[int] = None
    vin: Optional[str] = None
    license_plate: Optional[str] = None
    registration_state: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission_type: Optional[str] = None
    is_active: Optional[bool] = None
    nickname: Optional[str] = None


class VehicleUpdateResponse(BaseModel):
    old_data: VehicleResponse
    updated_data: VehicleResponse
    changes: dict
    update_message: str


class VehicleDeleteResponse(BaseModel):
    vehicle_id: int
    message: str
