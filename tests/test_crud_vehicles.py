import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models import Base, User, Vehicle
from app.crud import users, vehicles
from app.schemas.users import UserCreate
from app.schemas.vehicles import VehicleCreate, VehicleUpdate


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


def get_new_user(db, user_id: int):
    if user_id == 1:
        user_data = UserCreate(
            username="testuser",
            email="testuser1@test.com",
            password="pass12345"
        )

        created_user = users.crud_register_new_user(db=db, user=user_data)
        return created_user

    else:
        user_data = UserCreate(
            username="testuser2",
            email="testuser2@test.com",
            password="pass12345"
        )

        created_user = users.crud_register_new_user(db=db, user=user_data)
        return created_user


def test_register_new_vehicle(db):

    created_user = get_new_user(db=db, user_id=1)

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

    new_vehicle = vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data)

    assert new_vehicle.id == 1
    assert new_vehicle.user_id == created_user.id
    assert new_vehicle.vehicle_type == vehicle_data.vehicle_type
    assert new_vehicle.make == vehicle_data.make
    assert new_vehicle.model == vehicle_data.model
    assert new_vehicle.color == vehicle_data.color
    assert new_vehicle.year == vehicle_data.year
    assert new_vehicle.mileage == vehicle_data.mileage
    assert new_vehicle.vin == vehicle_data.vin
    assert new_vehicle.license_plate == vehicle_data.license_plate
    assert new_vehicle.registration_state == vehicle_data.registration_state
    assert new_vehicle.fuel_type == vehicle_data.fuel_type
    assert new_vehicle.transmission_type == vehicle_data.transmission_type
    assert new_vehicle.is_active == vehicle_data.is_active
    assert new_vehicle.nickname == vehicle_data.nickname


def test_register_new_vehicle_vin_already_registered(db):
    created_user = get_new_user(db=db, user_id=1)

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

    vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data)

    created_user_2 = get_new_user(db=db, user_id=2)

    vehicle_data_2 = VehicleCreate(
        vehicle_type="Sedan",
        make="Toyota",
        model="Corolla",
        color="Blue",
        year=2021,
        mileage=2500,
        vin="asdf853dasdf51g",
        license_plate="XYZ165",
        registration_state="OH",
        fuel_type="Gasoline",
        transmission_type="Automatic",
        is_active=True,
        nickname="DailyDirt"
    )

    with pytest.raises(HTTPException) as exc_info:
        vehicles.crud_register_new_vehicle(db=db, current_user=created_user_2, vehicle_create=vehicle_data_2)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"{vehicle_data_2.vin} already registered."


def test_register_new_vehicle_nickname_exists_on_user_other_car(db):
    created_user = get_new_user(db=db, user_id=1)

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

    vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data)

    vehicle_data_2 = VehicleCreate(
        vehicle_type="Sedan",
        make="Toyota",
        model="Prius",
        color="Blue",
        year=2020,
        mileage=25000,
        vin="asdf853das658iol",
        license_plate="XYZ894",
        registration_state="OH",
        fuel_type="Electric",
        transmission_type="Automatic",
        is_active=True,
        nickname="DailyDriver"
    )

    with pytest.raises(HTTPException) as exc_info:
        vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data_2)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"'{vehicle_data_2.nickname}' is already being used by you."


def test_fetch_all_user_vehicles(db):
    created_user = get_new_user(db=db, user_id=1)
    check = vehicles.crud_fetch_user_vehicles(db=db, current_user=created_user)

    assert type(check) == dict
    assert check["vehicles"] == []


def test_filter_user_vehicles(db):
    created_user = get_new_user(db=db, user_id=1)

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

    vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data)

    filtered_car = vehicles.crud_filter_user_vehicles(
        db=db,
        current_user=created_user,
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

    filtered_vehicle_data = filtered_car["vehicles"][0]

    for field, value in vehicle_data.__dict__.items():
        assert getattr(filtered_vehicle_data, field) == value


def test_filter_user_vehicles_no_filters_passed(db):
    created_user = get_new_user(db=db, user_id=1)

    with pytest.raises(HTTPException) as exc_info:
        vehicles.crud_filter_user_vehicles(
            db=db,
            current_user=created_user,
            vehicle_type=None,
            make=None,
            model=None,
            color=None,
            year=None,
            mileage=None,
            vin=None,
            license_plate=None,
            registration_state=None,
            fuel_type=None,
            transmission_type=None,
            is_active=None,
            nickname=None
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "At least one filter parameter must be provided."


def test_update_vehicle(db):
    created_user = get_new_user(db=db, user_id=1)

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

    vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data)

    update_data = VehicleUpdate(
        make="Toyota",
        color="Orange",
        mileage=30000,
        license_plate="XYZ321",
        nickname="Baby Orange"
    )

    update_request = vehicles.crud_update_vehicle(
        db=db,
        current_user=created_user,
        vehicle_id=1,
        update_data=update_data
    )

    updated_data_old = update_request["old_data"]
    updated_data_new = update_request["updated_data"]
    updated_data_changes = update_request["changes"]

    assert updated_data_old.color != update_data.color
    assert updated_data_old.mileage != update_data.mileage
    assert updated_data_old.license_plate != update_data.license_plate
    assert updated_data_old.nickname != update_data.nickname
    assert updated_data_new.color == update_data.color
    assert updated_data_new.mileage == update_data.mileage
    assert updated_data_new.license_plate == update_data.license_plate
    assert updated_data_new.nickname == update_data.nickname
    assert updated_data_changes["color"]
    assert updated_data_changes["mileage"]
    assert updated_data_changes["license_plate"]
    assert updated_data_changes["nickname"]
    assert update_request["update_message"] == "Vehicle ID 1 updated successfully."


def test_update_vehicle_no_vehicle_id(db):
    created_user = get_new_user(db=db, user_id=1)

    update_data = VehicleUpdate(
        make="Toyota",
        color="Orange",
        mileage=30000,
        license_plate="XYZ321",
        nickname="Baby Orange"
    )

    with pytest.raises(HTTPException) as exc_info:
        update_request = vehicles.crud_update_vehicle(
            db=db,
            current_user=created_user,
            vehicle_id=1,
            update_data=update_data
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Vehicle ID 1 not found or not owned by you."


def test_update_vehicle_no_updates(db):
    created_user = get_new_user(db=db, user_id=1)

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

    vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data)

    update_data = VehicleUpdate()

    update_request = vehicles.crud_update_vehicle(
        db=db,
        current_user=created_user,
        vehicle_id=1,
        update_data=update_data
    )

    assert update_request["old_data"] == update_request["updated_data"]
    for key, val in update_request["changes"].items():
        assert not val
    assert update_request["update_message"] == f"No updates were made to vehicle ID 1."


def test_delete_vehicle(db):
    created_user = get_new_user(db=db, user_id=1)

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

    vehicles.crud_register_new_vehicle(db=db, current_user=created_user, vehicle_create=vehicle_data)

    deleted_response = vehicles.crud_delete_vehicle(db=db, current_user=created_user, vehicle_id=1)

    assert deleted_response["vehicle_id"] == 1
    assert deleted_response["message"] == "Vehicle ID: 1 deleted successfully."


def test_delete_vehicle_no_existing_vehicle_id(db):
    created_user = get_new_user(db=db, user_id=1)

    with pytest.raises(HTTPException) as exc_info:
        vehicles.crud_delete_vehicle(db=db, current_user=created_user, vehicle_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Vehicle ID 1 not found or not owned by you."
