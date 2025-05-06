import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.models import Base
from app.crud import vehicles, maintenance
from app.schemas.vehicles import VehicleCreate
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from test_crud_vehicles import get_new_user


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


def get_registered_car(db, current_user, user_id: int = 1):
    if user_id == 1:
        vehicle_data = VehicleCreate(
            vehicle_type="Sedan",
            make="Toyota",
            model="Corolla",
            color="Blue",
            year=2020,
            mileage=25000,
            vin="asdf853dasdf51g",
            license_plate="XYZ123",
            registration_state="OH",
            fuel_type="Gasoline",
            transmission_type="Automatic",
            is_active=True,
            nickname="DailyDriver"
        )

    else:
        vehicle_data = VehicleCreate(
            vehicle_type="Sedan",
            make="Toyota",
            model="Prius",
            color="Blue",
            year=2020,
            mileage=25000,
            vin="uydfjasdn45sd2215",
            license_plate="XYZ999",
            registration_state="OH",
            fuel_type="Gasoline",
            transmission_type="Automatic",
            is_active=True,
            nickname="Little Betty"
        )

    return vehicles.crud_register_new_vehicle(db=db, current_user=current_user, vehicle_create=vehicle_data)


def test_create_maintenance_record(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    new_record = maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    for field, value in maintenance_create.__dict__.items():
        assert getattr(new_record, field) == value
    """
    maintenance_provider: Optional[str] = Field(None, example="Valvoline")
    maintenance_type: str = Field(None, example="Oil Change")
    description: Optional[str] = Field(None, example="Changed to synthetic oil.")
    mileage: int = Field(None, example="133150")
    cost: float = Field(None, example="89.56")
    serviced_at: Optional[datetime] = Field(None, example="2024-04-10T10:00:00")
    vehicle_id: int
    """


def test_create_maintenance_record_no_vehicle_with_vehicle_id(db):
    created_user = get_new_user(db=db, user_id=1)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=1
    )

    with pytest.raises(HTTPException) as exc_info:
        maintenance.crud_create_maintenance_record(
            db=db,
            current_user=created_user,
            maintenance_create=maintenance_create
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Vehicle ID 1 not found or not owned by you."


def test_create_maintenance_record_maintenance_mileage_less_than_vehicle_mileage(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=1,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    with pytest.raises(HTTPException) as exc_info:
        maintenance.crud_create_maintenance_record(
            db=db,
            current_user=created_user,
            maintenance_create=maintenance_create
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        f"Maintenance mileage({maintenance_create.mileage}) "
        f"cannot be less than current vehicle mileage({new_vehicle.mileage})"
    )


def test_base_maintenance_records_query(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    fetched_user = maintenance.base_maintenance_records_query(db=db, current_user=created_user)

    only_record = fetched_user.all()[0]

    assert len(fetched_user.all()) == 1
    for field, value in maintenance_create.__dict__.items():
        assert getattr(only_record, field) == value


def test_fetch_all_vehicle_maintenance_records(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    all_records = maintenance.crud_fetch_all_vehicle_maintenance_records(db=db, current_user=created_user)

    results = all_records["maintenance"]

    assert len(results) == 1
    for field, value in maintenance_create.__dict__.items():
        assert getattr(results[0], field) == value


def test_fetch_all_vehicle_maintenance_records_filtered(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    filtered_response = maintenance.crud_fetch_all_vehicle_maintenance_records_filtered(
        db=db,
        current_user=created_user,
        vehicle_id=maintenance_create.vehicle_id,
        maintenance_provider=maintenance_create.maintenance_provider,
        maintenance_type=maintenance_create.maintenance_type,
        description=maintenance_create.description,
        mileage=maintenance_create.mileage,
        cost=maintenance_create.cost,
        serviced_at=maintenance_create.serviced_at
    )

    results = filtered_response["maintenance"]

    assert len(results) == 1
    for field, value in maintenance_create.__dict__.items():
        assert getattr(results[0], field) == value


def test_fetch_all_vehicle_maintenance_records_filtered_no_filters(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    with pytest.raises(HTTPException) as exc_info:
        maintenance.crud_fetch_all_vehicle_maintenance_records_filtered(
            db=db,
            current_user=created_user,
            vehicle_id=None,
            maintenance_provider=None,
            maintenance_type=None,
            description=None,
            mileage=None,
            cost=None,
            serviced_at=None
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "At least one filter parameter must be provided."


def test_update_maintenance_record(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    maintenance_update = MaintenanceUpdate(
        maintenance_provider="Take 5",
        maintenance_type="Tire rotation",
        description="Rotated all 4 tires",
        mileage=35000,
        cost=216.54,
        serviced_at="2024-04-10T10:00:00",
    )

    update_request = maintenance.crud_update_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_record_id=1,
        update_data=maintenance_update
    )

    old_data = update_request["old_data"]
    updated_data = update_request["updated_data"]
    changes = update_request["changes"]
    update_message = update_request["update_message"]

    for field, value in maintenance_create.__dict__.items():
        if field == "vehicle_id":
            assert value == old_data.vehicle.id
        else:
            assert getattr(old_data, field) == value

    # elifs check that existing data passed remain the same and run without error
    for field, value in maintenance_update.__dict__.items():
        if field == "vehicle_id":
            assert value == updated_data.vehicle.id
        elif field == "mileage":
            assert value == old_data.mileage
        elif field == "serviced_at":
            assert value == old_data.serviced_at
        else:
            assert getattr(updated_data, field) == value

    changes_dict = {
        "maintenance_provider": True,
        "maintenance_type": True,
        "description": True,
        "mileage": False,
        "cost": True,
        "serviced_at": False,
        "vehicle": False
    }
    assert changes == changes_dict
    assert update_message == f"Maintenance Record ID 1 updated successfully."


def test_update_maintenance_record_no_record(db):
    created_user = get_new_user(db=db, user_id=1)
    get_registered_car(db=db, current_user=created_user)

    maintenance_update = MaintenanceUpdate(
        maintenance_provider="Take 5",
        maintenance_type="Tire rotation",
        description="Rotated all 4 tires",
        mileage=35000,
        cost=216.54,
        serviced_at="2024-04-10T10:00:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        maintenance.crud_update_maintenance_record(
            db=db,
            current_user=created_user,
            maintenance_record_id=1,
            update_data=maintenance_update
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Maintenance record not found."


def test_update_maintenance_record_user_id_not_found(db):
    created_user = get_new_user(db=db, user_id=1)
    second_user = get_new_user(db=db, user_id=2)
    new_vehicle = get_registered_car(db=db, current_user=second_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=second_user,
        maintenance_create=maintenance_create
    )

    maintenance_update = MaintenanceUpdate(
        maintenance_provider="Take 5",
        maintenance_type="Tire rotation",
        description="Rotated all 4 tires",
        mileage=35000,
        cost=216.54,
        serviced_at="2024-04-10T10:00:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        maintenance.crud_update_maintenance_record(
            db=db,
            current_user=created_user,
            maintenance_record_id=1,
            update_data=maintenance_update
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to update this record."


def test_update_maintenance_record_no_updates_passed(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    maintenance_update = MaintenanceUpdate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
    )

    update_request = maintenance.crud_update_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_record_id=1,
        update_data=maintenance_update
    )

    old_data = update_request["old_data"]
    updated_data = update_request["updated_data"]
    changes = update_request["changes"]
    update_message = update_request["update_message"]

    assert old_data == updated_data
    for key, value in changes.items():
        assert value is False
    assert update_message == "No updates were made to Maintenance Record ID 1."


def test_delete_maintenance_record(db):
    created_user = get_new_user(db=db, user_id=1)
    new_vehicle = get_registered_car(db=db, current_user=created_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    new_record = maintenance.crud_create_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_create=maintenance_create
    )

    delete_request = maintenance.crud_delete_maintenance_record(
        db=db,
        current_user=created_user,
        maintenance_record_id=new_record.id
    )

    record_check = maintenance.crud_fetch_all_vehicle_maintenance_records(db=db,current_user=created_user)

    assert record_check["maintenance"] == []
    assert delete_request["id"] == new_record.id
    assert delete_request["message"] == f"Maintenance Record ID: {new_record.id} deleted successfully."


def test_delete_maintenance_record_no_maintenance_record_found(db):
    created_user = get_new_user(db=db, user_id=1)
    get_registered_car(db=db, current_user=created_user)

    with pytest.raises(HTTPException) as exc_info:
        maintenance.crud_delete_maintenance_record(db=db, current_user=created_user, maintenance_record_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Maintenance record not found."


def test_delete_maintenance_record_user_does_not_own_record(db):
    created_user = get_new_user(db=db, user_id=1)
    second_user = get_new_user(db=db, user_id=2)
    new_vehicle = get_registered_car(db=db, current_user=second_user)

    maintenance_create = MaintenanceCreate(
        maintenance_provider="Valvoline",
        maintenance_type="Oil Change",
        description="Synthetic Oil Change",
        mileage=35000,
        cost=89.65,
        serviced_at="2024-04-10T10:00:00",
        vehicle_id=new_vehicle.id
    )

    maintenance.crud_create_maintenance_record(
        db=db,
        current_user=second_user,
        maintenance_create=maintenance_create
    )

    with pytest.raises(HTTPException) as exc_info:
        maintenance.crud_delete_maintenance_record(db=db, current_user=created_user, maintenance_record_id=1)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to delete this record."
