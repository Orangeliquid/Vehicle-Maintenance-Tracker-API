from typing import Type

from app.models import MaintenanceReminder
from app.schemas.reminder import MaintenanceReminderResponse


def make_maintenance_reminder_response(maintenance_reminder: Type[MaintenanceReminder]) -> MaintenanceReminderResponse:
    return MaintenanceReminderResponse(
        maintenance_type=maintenance_reminder.maintenance_type,
        details=maintenance_reminder.details,
        interval_miles=maintenance_reminder.interval_miles,
        interval_months=maintenance_reminder.interval_months,
        last_serviced_mileage=maintenance_reminder.last_serviced_mileage,
        last_serviced_date=maintenance_reminder.last_serviced_date,
        notify_before_miles=maintenance_reminder.notify_before_miles,
        notify_before_days=maintenance_reminder.notify_before_days,
        estimated_miles_driven_per_month=maintenance_reminder.estimated_miles_driven_per_month,
        is_active=maintenance_reminder.is_active,
        id=maintenance_reminder.id,
        created_at=maintenance_reminder.created_at,
        updated_at=maintenance_reminder.updated_at,
        vehicle=maintenance_reminder.vehicle
    )
