import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.models import Base, MaintenanceReminder
from app.crud import vehicles, maintenance, reminder
from app.schemas.reminder import MaintenanceReminderCreate, MaintenanceReminderUpdate
from test_crud_vehicles import get_new_user
from test_crud_maintenance import get_registered_car


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        Base.metadata.drop_all(bind=engine)
        db.close()


def test_create_maintenance_reminder(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder_response = reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    assert len(db.query(MaintenanceReminder).all()) == 1

    for field, value in reminder_create.__dict__.items():
        assert getattr(reminder_response, field) == value


def test_create_maintenance_reminder_no_vehicle_found(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=2
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_create_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder=reminder_create
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Vehicle ID {reminder_create.vehicle_id} not found or not owned by you."


def test_create_maintenance_reminder_mileage_less_than_vehicle_mileage(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=1,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_create_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder=reminder_create
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        f"Last serviced mileage({reminder_create.last_serviced_mileage}) "
        f"cannot be greater than current vehicle mileage({new_vehicle.mileage})"
    )


def test_create_maintenance_reminder_last_serviced_date_in_future(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date="2030-10-10T10:00:00",
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_create_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder=reminder_create
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Last serviced date cannot be in the future."


def test_fetch_all_maintenance_reminders(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    all_response = reminder.crud_fetch_all_maintenance_reminders(
        db=db,
        current_user=created_user
    )

    for field, value in reminder_create.__dict__.items():
        assert getattr(all_response["reminders"][0], field) == value


def test_fetch_all_maintenance_reminders_filtered(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    response = reminder.crud_fetch_all_maintenance_reminders_filtered(
        db=db,
        current_user=created_user,
        vehicle_id=new_vehicle.id,
        maintenance_type=reminder_create.maintenance_type,
        details=reminder_create.details,
        interval_miles=reminder_create.interval_miles,
        interval_months=reminder_create.interval_months,
        last_serviced_mileage=reminder_create.last_serviced_mileage,
        last_serviced_date=reminder_create.last_serviced_date,
        notify_before_miles=reminder_create.notify_before_miles,
        notify_before_days=reminder_create.notify_before_days,
        estimated_miles_driven_per_month=reminder_create.estimated_miles_driven_per_month,
        is_active=reminder_create.is_active,
        vehicle_make=new_vehicle.make,
        vehicle_model=new_vehicle.model,
        vehicle_year=new_vehicle.year,
        vehicle_vin=new_vehicle.vin,
        vehicle_nickname=None
    )

    only_reminder = response["reminders"][0]

    for field, value in reminder_create.__dict__.items():
        assert getattr(only_reminder, field) == value

    assert only_reminder.vehicle.make == new_vehicle.make
    assert only_reminder.vehicle.model == new_vehicle.model
    assert only_reminder.vehicle.year == new_vehicle.year
    assert only_reminder.vehicle.vin == new_vehicle.vin
    assert only_reminder.vehicle.nickname == new_vehicle.nickname


def test_fetch_all_maintenance_reminders_filtered_no_params_passed(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_fetch_all_maintenance_reminders_filtered(
            db=db,
            current_user=created_user,
            vehicle_id=None,
            maintenance_type=None,
            details=None,
            interval_miles=None,
            interval_months=None,
            last_serviced_mileage=None,
            last_serviced_date=None,
            notify_before_miles=None,
            notify_before_days=None,
            estimated_miles_driven_per_month=None,
            is_active=None,
            vehicle_make=None,
            vehicle_model=None,
            vehicle_year=None,
            vehicle_vin=None,
            vehicle_nickname=None
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "At least one filter parameter must be provided."


def test_update_maintenance_reminder(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder_create_response = reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    reminder_update = MaintenanceReminderUpdate(
        maintenance_type="Oil Change",
        details="Synthetic oil changed",
        interval_miles=7500,
        interval_months=10,
        last_serviced_mileage=24000,
        last_serviced_date="2025-04-10T10:00:00",
        notify_before_miles=350,
        notify_before_days=15,
        estimated_miles_driven_per_month=900,
        is_active=True
        )

    update_request = reminder.crud_update_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder_id=1,
        update_data=reminder_update
    )

    old_data = update_request["old_data"]
    updated_data = update_request["updated_data"]
    changes = update_request["changes"]
    update_message = update_request["update_message"]

    for field, value in reminder_create.__dict__.items():
        if field == "vehicle_id":
            assert value == old_data.vehicle.id
        else:
            assert getattr(old_data, field) == value

    for field, value in reminder_update.__dict__.items():
        assert getattr(updated_data, field) == value

    changes_dict = {
        "maintenance_type": True,
        "details": True,
        "interval_miles": True,
        "interval_months": True,
        "last_serviced_mileage": True,
        "last_serviced_date": True,
        "notify_before_miles": True,
        "notify_before_days": True,
        "estimated_miles_driven_per_month": True,
        "is_active": False,
        "vehicle": False
    }

    assert changes == changes_dict
    assert update_message == f"Maintenance Record ID {reminder_create_response.id} updated successfully."


def test_update_maintenance_reminder_no_maintenance_record_id(db):
    created_user = get_new_user(db=db, user_id=1)
    get_registered_car(db=db, current_user=created_user)

    reminder_update = MaintenanceReminderUpdate(
        maintenance_type="Oil Change",
        details="Synthetic oil changed",
        interval_miles=7500,
        interval_months=10,
        last_serviced_mileage=24000,
        last_serviced_date="2025-04-10T10:00:00",
        notify_before_miles=350,
        notify_before_days=15,
        estimated_miles_driven_per_month=900,
        is_active=True
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_update_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder_id=1,
            update_data=reminder_update
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Reminder: 1 not found"


def test_update_maintenance_reminder_invalid_intervals(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=None,
        interval_months=12,
        last_serviced_mileage=None,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    reminder_update = MaintenanceReminderUpdate(
        maintenance_type="Oil Change",
        details="Synthetic oil changed",
        interval_miles=None,
        interval_months=None,
        last_serviced_mileage=None,
        last_serviced_date=None,
        notify_before_miles=350,
        notify_before_days=15,
        estimated_miles_driven_per_month=900,
        is_active=True
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_update_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder_id=1,
            update_data=reminder_update
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Reminder must include either a complete mileage-based or time-based configuration."


def test_maintenance_reminder_update_vehicle_is_not_users(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    secondary_user = get_new_user(db=db, user_id=2)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    reminder_update = MaintenanceReminderUpdate(
        maintenance_type="Oil Change",
        details="Synthetic oil changed",
        interval_miles=7500,
        interval_months=10,
        last_serviced_mileage=24000,
        last_serviced_date="2025-04-10T10:00:00",
        notify_before_miles=350,
        notify_before_days=15,
        estimated_miles_driven_per_month=900,
        is_active=True
    )

    with pytest.raises(HTTPException) as exc_info:
        update_request = reminder.crud_update_maintenance_reminder(
            db=db,
            current_user=secondary_user,
            maintenance_reminder_id=1,
            update_data=reminder_update
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to update this record."


def test_maintenance_reminder_update_last_serviced_mileage_greater_than_vehicle_mileage(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    reminder_update = MaintenanceReminderUpdate(
        maintenance_type="Oil Change",
        details="Synthetic oil changed",
        interval_miles=7500,
        interval_months=10,
        last_serviced_mileage=26000,
        last_serviced_date="2025-04-10T10:00:00",
        notify_before_miles=350,
        notify_before_days=15,
        estimated_miles_driven_per_month=900,
        is_active=True
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_update_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder_id=1,
            update_data=reminder_update
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
                    f"Last serviced mileage ({reminder_update.last_serviced_mileage}) "
                    f"cannot be greater than current vehicle mileage ({new_vehicle.mileage})."
                )


def test_maintenance_reminder_update_last_service_date_in_future(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    reminder_update = MaintenanceReminderUpdate(
        maintenance_type="Oil Change",
        details="Synthetic oil changed",
        interval_miles=7500,
        interval_months=10,
        last_serviced_mileage=25000,
        last_serviced_date="2026-04-10T10:00:00",
        notify_before_miles=350,
        notify_before_days=15,
        estimated_miles_driven_per_month=900,
        is_active=True
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_update_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder_id=1,
            update_data=reminder_update
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Last serviced date cannot be in the future."


def test_maintenance_reminder_update_no_new_update_values(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    reminder_update = MaintenanceReminderUpdate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
    )

    reminder_update_response = reminder.crud_update_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder_id=1,
            update_data=reminder_update
        )

    old_data = reminder_update_response["old_data"]
    updated_data = reminder_update_response["updated_data"]
    changes = reminder_update_response["changes"]
    update_message = reminder_update_response["update_message"]

    assert old_data == updated_data
    for key, value in changes.items():
        assert value is False
    assert update_message == "No updates were made to Maintenance Reminder ID 1."


def test_delete_maintenance_reminder(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder_create_response = reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    delete_response = reminder.crud_delete_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder_id=1
    )

    assert delete_response["id"] == reminder_create_response.id
    assert delete_response["message"] == "Maintenance Record ID: 1 deleted successfully."


def test_delete_maintenance_reminder_not_found(db):
    created_user = get_new_user(db=db, user_id=1)

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_delete_maintenance_reminder(
            db=db,
            current_user=created_user,
            maintenance_reminder_id=1
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Maintenance Reminder not found."


def test_delete_maintenance_not_owned_by_user(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    secondary_user = get_new_user(db=db, user_id=2)

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need all tires rotated.",
        interval_miles=8000,
        interval_months=12,
        last_serviced_mileage=new_vehicle.mileage,
        last_serviced_date=new_vehicle.created_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    with pytest.raises(HTTPException) as exc_info:
        reminder.crud_delete_maintenance_reminder(
            db=db,
            current_user=secondary_user,
            maintenance_reminder_id=1
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You do not have permission to delete reminder for Vehicle ID 1."
