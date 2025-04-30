from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserMaintenanceStats(BaseModel):
    total_amount_of_vehicles: int = 0
    total_maintenance_records: int = 0
    total_maintenance_cost: float = 0.0
    total_maintenance_reminders: int = 0
    upcoming_reminder_count: int = 0
    overdue_reminder_count: int = 0
    highest_cost_maintenance_record: float = 0.0
    most_maintained_vehicle: Optional[str] = None


class UserMaintenanceStatsResponse(BaseModel):
    stats: UserMaintenanceStats
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    message: str = "User maintenance stats fetched successfully"
