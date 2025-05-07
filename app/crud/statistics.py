from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import Counter

from app.models import User, Vehicle, MaintenanceRecord, MaintenanceReminder
from app.schemas.statistics import UserMaintenanceStats


def crud_fetch_user_maintenance_statistics(db: Session, current_user: User) -> dict:
    """
    total_maintenance_records: int = 0
    total_maintenance_cost: float = 0.0
    total_maintenance_reminders: int = 0
    upcoming_reminder_count: int = 0
    overdue_reminder_count: int = 0
    highest_cost_maintenance_record: float = 0.0
    most_common_maintenance_type: Optional[str] = None
    most_maintained_vehicle: Optional[str] = None
    """

    user_vehicles = db.query(Vehicle).filter(Vehicle.user_id == current_user.id).all()
    vehicle_ids = [v.id for v in user_vehicles]

    maintenance_stats = query_maintenance_records(db=db, vehicle_ids=vehicle_ids)

    maintenance_reminder_stats = query_maintenance_reminders(db=db, vehicle_ids=vehicle_ids)

    stats = UserMaintenanceStats(
        total_amount_of_vehicles=len(vehicle_ids),
        total_maintenance_records=maintenance_stats.get("total_maintenance_records"),
        total_maintenance_cost=maintenance_stats.get("total_maintenance_cost"),
        total_maintenance_reminders=maintenance_reminder_stats.get("total_maintenance_reminders"),
        upcoming_reminder_count=maintenance_reminder_stats.get("upcoming_reminder_count"),
        overdue_reminder_count=maintenance_reminder_stats.get("overdue_reminder_count"),
        highest_cost_maintenance_record=maintenance_stats.get("highest_cost_maintenance_record"),
        most_maintained_vehicle=maintenance_stats.get("most_maintained_vehicle")
    )

    message = "User maintenance stats fetched successfully."

    return {"stats": stats, "generated_at": datetime.utcnow(), "message": message}


def query_maintenance_records(db: Session, vehicle_ids: list) -> dict:
    maintenance_records = db.query(MaintenanceRecord).filter(MaintenanceRecord.vehicle_id.in_(vehicle_ids)).all()
    for record in maintenance_records:
        print(f"ID: {record.id}, Cost: {record.cost}, Vehicle: {record.vehicle.nickname}")

    total_maintenance_records = len(maintenance_records)
    total_maintenance_cost = sum(record.cost for record in maintenance_records if record.cost)

    valid_costs = [record.cost for record in maintenance_records if record.cost is not None]

    highest_cost_maintenance_record = float(max(valid_costs))

    vehicle_counts = Counter([record.vehicle_id for record in maintenance_records])
    # if there is a tie, as in equal amounts of maintenance records for a vehicle, index 0 will be set as val
    most_maintained_vehicle_id = vehicle_counts.most_common(1)[0][0] if vehicle_counts else None

    most_maintained_vehicle = None
    if most_maintained_vehicle_id:
        # Pycharm doesn't like the '==' comparator but works just fine at runtime
        most_maintained_vehicle_obj = db.query(Vehicle.nickname).filter(
            Vehicle.id == most_maintained_vehicle_id).first()

        if most_maintained_vehicle_obj:
            most_maintained_vehicle = most_maintained_vehicle_obj[0]

    return {
        "total_maintenance_records": total_maintenance_records,
        "total_maintenance_cost": total_maintenance_cost,
        "highest_cost_maintenance_record": highest_cost_maintenance_record,
        "most_maintained_vehicle": most_maintained_vehicle
    }


def query_maintenance_reminders(db: Session, vehicle_ids: list) -> dict:
    """
    total_maintenance_reminders=,
    upcoming_reminder_count=,
    overdue_reminder_count=,
    """
    now = datetime.utcnow()

    reminders = db.query(MaintenanceReminder).filter(MaintenanceReminder.vehicle_id.in_(vehicle_ids)).all()

    total_maintenance_reminders = len(reminders)

    upcoming_reminder_count = 0
    overdue_reminder_count = 0

    for reminder in reminders:
        is_upcoming = False
        is_overdue = False

        if reminder.last_serviced_date:
            starting_reminder_date = reminder.last_serviced_date
        elif reminder.updated_at:
            starting_reminder_date = reminder.updated_at
        else:
            starting_reminder_date = reminder.created_at

        if reminder.interval_months:
            service_due_date = starting_reminder_date + timedelta(days=(reminder.interval_months * 30))
            notify_before_date = service_due_date - timedelta(days=reminder.notify_before_days)

            if now >= notify_before_date:
                is_overdue = True
            else:
                is_upcoming = True

        if (
                reminder.last_serviced_mileage is not None and
                reminder.interval_miles and
                reminder.estimated_miles_driven_per_month
        ):
            service_mileage_due = reminder.last_serviced_mileage + reminder.interval_miles
            notify_before_mileage = service_mileage_due - reminder.notify_before_miles

            estimated_months_passed = (now - starting_reminder_date).days / 30
            estimated_miles_driven = reminder.estimated_miles_driven_per_month * estimated_months_passed

            if estimated_miles_driven + reminder.last_serviced_mileage >= notify_before_mileage:
                is_overdue = True
            else:
                is_upcoming = True

        if is_overdue:
            overdue_reminder_count += 1
        elif is_upcoming:
            upcoming_reminder_count += 1

    return {
        "total_maintenance_reminders": total_maintenance_reminders,
        "upcoming_reminder_count": upcoming_reminder_count,
        "overdue_reminder_count": overdue_reminder_count
    }
