import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.models import Base
from app.crud import reminder, maintenance, statistics
from app.schemas.reminder import MaintenanceReminderCreate, MaintenanceReminderUpdate
from app.schemas.maintenance import MaintenanceCreate
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


def test_crud_fetch_user_statistics(db):
    created_user = get_new_user(db=db, user_id=1)
    vehicle_one = get_registered_car(db=db, current_user=created_user, vehicle_number=1)
    vehicle_two = get_registered_car(db=db, current_user=created_user, vehicle_number=2)

    # add maintenance record for vehicle one
    maintenance_create_one = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=25000,
        cost=89.65,
        serviced_at="2025-05-05T10:00:00",
        vehicle_id=vehicle_one.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create_one
    )

    # add maintenance record for vehicle two
    maintenance_create_two = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Tire roation",
        description="Rotated all four tires.",
        mileage=25000,
        cost=200.45,
        serviced_at="2024-05-05T10:00:00",
        vehicle_id=vehicle_two.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create_two
    )

    # create reminder for vehicle_one
    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Oil Change",
        details="Need a new synthetic oil change",
        interval_miles=8000,
        interval_months=8,
        last_serviced_mileage=maintenance_create_one.mileage,
        last_serviced_date=maintenance_create_one.serviced_at,
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

    # create reminder for vehicle_two
    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Tire Rotation",
        details="Need to have all four tires rotated",
        interval_miles=6000,
        interval_months=12,
        last_serviced_mileage=maintenance_create_two.mileage,
        last_serviced_date=maintenance_create_two.serviced_at,
        notify_before_miles=500,
        notify_before_days=30,
        estimated_miles_driven_per_month=1000,
        is_active=True,
        vehicle_id=2
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    statistics_response = statistics.crud_fetch_user_maintenance_statistics(db=db, current_user=created_user)

    stats = statistics_response["stats"]
    date_generated = statistics_response["generated_at"]

    assert stats.total_amount_of_vehicles == 2
    assert stats.total_maintenance_records == 2
    assert stats.total_maintenance_cost == maintenance_create_one.cost + maintenance_create_two.cost
    assert stats.total_maintenance_reminders == 2
    assert stats.upcoming_reminder_count == 1
    assert stats.overdue_reminder_count == 1
    assert stats.highest_cost_maintenance_record == maintenance_create_two.cost
    assert stats.most_maintained_vehicle == vehicle_one.nickname
    assert date_generated <= datetime.utcnow()
    assert statistics_response["message"] == "User maintenance stats fetched successfully."
    """
        total_maintenance_reminders=maintenance_reminder_stats.get("total_maintenance_reminders"),
        upcoming_reminder_count=maintenance_reminder_stats.get("upcoming_reminder_count"),
        overdue_reminder_count=maintenance_reminder_stats.get("overdue_reminder_count"),
        highest_cost_maintenance_record=maintenance_stats.get("highest_cost_maintenance_record"),
        most_maintained_vehicle=maintenance_stats.get("most_maintained_vehicle")
    """


def test_crud_fetch_user_statistics_with_reminder_update_no_last_serviced_date(db):
    created_user = get_new_user(db=db, user_id=1)
    vehicle_one = get_registered_car(db=db, current_user=created_user, vehicle_number=1)

    maintenance_create_one = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=25000,
        cost=89.65,
        serviced_at="2025-01-05T10:00:00",
        vehicle_id=vehicle_one.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create_one
    )

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Oil Change",
        details="Need a new synthetic oil change",
        interval_miles=8000,
        interval_months=8,
        last_serviced_mileage=maintenance_create_one.mileage,
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
        notify_before_miles=350,
        notify_before_days=15,
        estimated_miles_driven_per_month=900,
        is_active=True
    )

    reminder.crud_update_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder_id=1,
        update_data=reminder_update
    )

    statistics_response = statistics.crud_fetch_user_maintenance_statistics(db=db, current_user=created_user)

    stats = statistics_response["stats"]
    date_generated = statistics_response["generated_at"]

    assert stats.total_amount_of_vehicles == 1
    assert stats.total_maintenance_records == 1
    assert stats.total_maintenance_cost == maintenance_create_one.cost
    assert stats.total_maintenance_reminders == 1
    assert stats.upcoming_reminder_count == 1
    assert stats.overdue_reminder_count == 0
    assert stats.highest_cost_maintenance_record == maintenance_create_one.cost
    assert stats.most_maintained_vehicle == vehicle_one.nickname
    assert date_generated <= datetime.utcnow()
    assert statistics_response["message"] == "User maintenance stats fetched successfully."


def test_crud_fetch_user_statistics_with_reminder_created_at(db):
    created_user = get_new_user(db=db, user_id=1)
    vehicle_one = get_registered_car(db=db, current_user=created_user, vehicle_number=1)

    maintenance_create_one = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=25000,
        cost=89.65,
        serviced_at="2025-01-05T10:00:00",
        vehicle_id=vehicle_one.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create_one
    )

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Oil Change",
        details="Need a new synthetic oil change",
        interval_miles=1000,
        interval_months=8,
        last_serviced_mileage=maintenance_create_one.mileage,
        notify_before_miles=1000,
        notify_before_days=50,
        estimated_miles_driven_per_month=5000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    statistics_response = statistics.crud_fetch_user_maintenance_statistics(db=db, current_user=created_user)

    stats = statistics_response["stats"]
    date_generated = statistics_response["generated_at"]

    assert stats.total_amount_of_vehicles == 1
    assert stats.total_maintenance_records == 1
    assert stats.total_maintenance_cost == maintenance_create_one.cost
    assert stats.total_maintenance_reminders == 1
    assert stats.upcoming_reminder_count == 0
    assert stats.overdue_reminder_count == 1
    assert stats.highest_cost_maintenance_record == maintenance_create_one.cost
    assert stats.most_maintained_vehicle == vehicle_one.nickname
    assert date_generated <= datetime.utcnow()
    assert statistics_response["message"] == "User maintenance stats fetched successfully."


def test_crud_fetch_user_statistics_with_estimated_miles_driven_higher_than_notify_threshold(db):
    created_user = get_new_user(db=db, user_id=1)
    vehicle_one = get_registered_car(db=db, current_user=created_user, vehicle_number=1)

    maintenance_create_one = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=25000,
        cost=89.65,
        serviced_at="2025-01-05T10:00:00",
        vehicle_id=vehicle_one.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create_one
    )

    reminder_create = MaintenanceReminderCreate(
        maintenance_type="Oil Change",
        details="Need a new synthetic oil change",
        interval_miles=3000,
        last_serviced_mileage=maintenance_create_one.mileage,
        last_serviced_date=maintenance_create_one.serviced_at,
        notify_before_miles=500,
        estimated_miles_driven_per_month=3000,
        is_active=True,
        vehicle_id=1
    )

    reminder.crud_create_maintenance_reminder(
        db=db,
        current_user=created_user,
        maintenance_reminder=reminder_create
    )

    statistics_response = statistics.crud_fetch_user_maintenance_statistics(db=db, current_user=created_user)

    stats = statistics_response["stats"]
    date_generated = statistics_response["generated_at"]

    assert stats.total_amount_of_vehicles == 1
    assert stats.total_maintenance_records == 1
    assert stats.total_maintenance_cost == maintenance_create_one.cost
    assert stats.total_maintenance_reminders == 1
    assert stats.upcoming_reminder_count == 0
    assert stats.overdue_reminder_count == 1
    assert stats.highest_cost_maintenance_record == maintenance_create_one.cost
    assert stats.most_maintained_vehicle == vehicle_one.nickname
    assert date_generated <= datetime.utcnow()
    assert statistics_response["message"] == "User maintenance stats fetched successfully."
