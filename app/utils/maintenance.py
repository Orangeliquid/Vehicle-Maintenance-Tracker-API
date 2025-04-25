from typing import Type

from app.models import MaintenanceRecord
from app.schemas.maintenance import MaintenanceResponse


def make_maintenance_response(maintenance_record: Type[MaintenanceRecord]) -> MaintenanceResponse:
    return MaintenanceResponse(
        maintenance_provider=maintenance_record.maintenance_provider,
        maintenance_type=maintenance_record.maintenance_type,
        description=maintenance_record.description,
        mileage=maintenance_record.mileage,
        cost=maintenance_record.cost,
        serviced_at=maintenance_record.serviced_at,
        id=maintenance_record.id,
        created_at=maintenance_record.created_at,
        updated_at=maintenance_record.updated_at,
        vehicle=maintenance_record.vehicle
    )
