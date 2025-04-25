from pydantic import BaseModel, model_validator, Field
from typing import Optional, List, Type
from typing_extensions import Self
from datetime import datetime

from app.schemas.vehicles import VehicleSummary


class MaintenanceReminderBase(BaseModel):
    maintenance_type: str
    details: Optional[str] = None
    interval_miles: Optional[int] = None
    interval_months: Optional[int] = None
    last_serviced_mileage: Optional[int] = None
    last_serviced_date: Optional[datetime] = None
    notify_before_miles: Optional[int] = Field(default=500, description="Miles before due to trigger notification")
    notify_before_days: Optional[int] = Field(default=14, description="Days before due to trigger notification")
    is_active: Optional[bool] = Field(default=True, description="Is the car active or not in use?")

    class Config:
        from_attributes = True


class MaintenanceReminderCreate(MaintenanceReminderBase):
    vehicle_id: int

    @model_validator(mode="after")
    def validate_reminder(self) -> Self:
        mileage_valid = (
                self.interval_miles is not None and
                self.last_serviced_mileage is not None
        )
        time_valid = (
                self.interval_months is not None and
                self.last_serviced_date is not None
        )

        if not mileage_valid and not time_valid:
            raise ValueError(
                "You must provide either: "
                "(1) mileage-based reminder (interval_miles and last_serviced_mileage), "
                "(2) time-based reminder (interval_months and last_serviced_date), "
                "or (3) both 1 and 2."
            )

        return self

    class Config:
        from_attributes = True


class MaintenanceReminderCreateResponse(MaintenanceReminderBase):
    id: int
    vehicle_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceReminderResponse(MaintenanceReminderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    vehicle: VehicleSummary

    class Config:
        from_attributes = True


class MaintenanceReminderListResponse(BaseModel):
    reminders: List[MaintenanceReminderResponse]


class MaintenanceReminderUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    details: Optional[str] = None
    interval_miles: Optional[int] = None
    interval_months: Optional[int] = None
    last_serviced_mileage: Optional[int] = None
    last_serviced_date: Optional[datetime] = None
    notify_before_miles: Optional[int] = None
    notify_before_days: Optional[int] = None
    is_active: Optional[bool] = None


class MaintenanceReminderUpdateResponse(BaseModel):
    old_data: MaintenanceReminderResponse
    updated_data: MaintenanceReminderResponse
    changes: dict
    update_message: str


class MaintenanceReminderDeleteResponse(BaseModel):
    id: int
    message: str
