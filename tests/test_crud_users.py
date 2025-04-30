import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models import Base, User
from app.crud import users
from app.schemas.users import UserCreate, UserUpdate, UserLogin
from app.utils.security import verify_password

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


def test_create_user(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    created_user = users.crud_register_new_user(db=db, user=user_data)

    assert created_user.username == user_data.username
    assert created_user.email == user_data.email
    assert created_user.password_hash != user_data.password


def test_create_user_with_existing_username(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    duplicate_user_data = UserCreate(
        username="testuser",
        email="newuser@example.com",
        password="pass1234"
    )

    with pytest.raises(HTTPException) as exc_info:
        users.crud_register_new_user(db=db, user=duplicate_user_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Username already registered."


def test_create_user_with_existing_email(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    duplicate_user_data = UserCreate(
        username="testuser2",
        email="testuser1@test.com",
        password="pass1234"
    )

    with pytest.raises(HTTPException) as exc_info:
        users.crud_register_new_user(db=db, user=duplicate_user_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered."


def test_authenticate_user(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    created_user = users.crud_register_new_user(db=db, user=user_data)

    authenticated_user = users.crud_authenticate_user(db=db, username=user_data.username, password=user_data.password)

    assert authenticated_user.id == 1
    assert authenticated_user.username == created_user.username
    assert authenticated_user.email == created_user.email
    assert authenticated_user.password_hash == created_user.password_hash
    assert authenticated_user.password_hash != user_data.password


def test_authenticate_user_wrong_password(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    with pytest.raises(HTTPException) as exc_info:
        users.crud_authenticate_user(db=db, username=user_data.username, password="newpassword")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials."


def test_authenticate_user_does_not_exist(db):
    with pytest.raises(HTTPException) as exc_info:
        users.crud_authenticate_user(db=db, username="testuser", password="newpassword")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials."


def test_login_user(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    user_login = UserLogin(
        username=user_data.username,
        password=user_data.password
    )

    logged_in_user = users.crud_login_user(db=db, user_login=user_login)

    assert logged_in_user["token_type"] == "bearer"
    assert type(logged_in_user) == dict
    assert type(logged_in_user["access_token"]) == str
    assert len(logged_in_user["access_token"]) > 0
    assert "access_token" in logged_in_user


def test_login_user_oauth(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    form_data = OAuth2PasswordRequestForm(
        username="testuser",
        password="pass12345",
        scope="",
        client_id=None,
        client_secret=None
    )

    logged_in_user = users.crud_login_user_oauth(db=db, form_data=form_data)

    assert logged_in_user["token_type"] == "bearer"
    assert type(logged_in_user) == dict
    assert type(logged_in_user["access_token"]) == str
    assert len(logged_in_user["access_token"]) > 0
    assert "access_token" in logged_in_user


def test_fetch_user_by_username(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    created_user = users.crud_register_new_user(db=db, user=user_data)

    found_user = users.crud_fetch_user_by_username(db=db, username=created_user.username)

    assert found_user.username == user_data.username
    assert found_user.email == user_data.email
    assert found_user.password_hash == created_user.password_hash
    assert found_user.password_hash != user_data.password
    assert found_user.id == 1


def test_fetch_user_by_username_no_user(db):
    username = "testuser"
    with pytest.raises(HTTPException) as exc_info:
        users.crud_fetch_user_by_username(db=db, username=username)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Username: '{username}' not found."


def test_fetch_user_by_id(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    created_user = users.crud_register_new_user(db=db, user=user_data)

    found_user = users.crud_fetch_user_by_id(db=db, user_id=created_user.id)

    assert found_user.username == user_data.username
    assert found_user.email == user_data.email
    assert found_user.password_hash == created_user.password_hash
    assert found_user.password_hash != user_data.password
    assert found_user.id == 1


def test_fetch_user_by_id_no_user(db):
    user_id = 1
    with pytest.raises(HTTPException) as exc_info:
        users.crud_fetch_user_by_id(db=db, user_id=user_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"User_id: '{user_id}' not found."


def test_fetch_all_users(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    all_users = users.crud_fetch_all_users(db=db)

    assert len(all_users) == 1
    assert type(all_users) == list
    assert all_users[0].username == user_data.username
    assert all_users[0].email == user_data.email
    assert all_users[0].password_hash != user_data.password
    assert all_users[0].id == 1


def test_update_user(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    update_request = UserUpdate(
        username="testuser1",
        email="testuser1@test.com",
        password="pass54321"
    )

    update = users.crud_update_user(db=db, user_id=1, user_update=update_request)

    updated_user = db.query(User).filter(User.id == 1).first()

    assert type(update) == dict
    assert update["old_data"].username == user_data.username
    assert update["old_data"].email == user_data.email
    assert update["old_data"].id == 1
    assert update["old_data"].username != update_request.username
    assert update["old_data"].email != update_request.email
    assert update["updated_data"].username == update_request.username
    assert update["updated_data"].email == update_request.email
    assert update["updated_data"].id == 1
    assert update["changes"] == {"Username": True, "Email": True, "Password": True}
    assert update["update_message"] == "Credentials successfully updated."
    assert not verify_password(user_data.password, updated_user.password_hash)
    assert verify_password(update_request.password, updated_user.password_hash)


def test_update_user_no_user(db):
    update_request = UserUpdate(
        username="testuser1",
        email="testuser1@test.com",
        password="pass54321"
    )

    user_id = 1

    with pytest.raises(HTTPException) as exc_info:
        users.crud_update_user(db=db, user_id=user_id, user_update=update_request)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"{user_id} not found."


def test_update_user_username_same_as_existing(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    update_request = UserUpdate(
        username="testuser",
        email="testuser1@test.com",
        password="pass54321"
    )

    with pytest.raises(HTTPException) as exc_info:
        users.crud_update_user(db=db, user_id=1, user_update=update_request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"'{update_request.username}' is already your username."


def test_update_user_username_already_taken(db):
    user_data_1 = UserCreate(
        username="testuser",
        email="testuser@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data_1)

    user_data_2 = UserCreate(
        username="testuser1",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data_2)

    update_request = UserUpdate(
        username="testuser1",
        email="testuser1@test.com",
        password="pass54321"
    )

    with pytest.raises(HTTPException) as exc_info:
        users.crud_update_user(db=db, user_id=1, user_update=update_request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"'{update_request.username}' is already taken."


def test_update_user_email_same_as_existing(db):
    user_data = UserCreate(
        username="testuser",
        email="testuser@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data)

    update_request = UserUpdate(
        username="testuser1",
        email="testuser@test.com",
        password="pass54321"
    )

    with pytest.raises(HTTPException) as exc_info:
        users.crud_update_user(db=db, user_id=1, user_update=update_request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"'{update_request.email}' is already your email."


def test_update_user_email_already_taken(db):
    user_data_1 = UserCreate(
        username="testuser",
        email="testuser@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data_1)

    user_data_2 = UserCreate(
        username="testuser1",
        email="testuser1@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data_2)

    update_request = UserUpdate(
        username="testuser2",
        email="testuser1@test.com",
        password="pass54321"
    )

    with pytest.raises(HTTPException) as exc_info:
        users.crud_update_user(db=db, user_id=1, user_update=update_request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"'{update_request.email}' is already taken."


def test_update_user_password_is_same_as_existing(db):
    user_data_1 = UserCreate(
        username="testuser",
        email="testuser@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data_1)

    update_request = UserUpdate(
        username="testuser2",
        email="testuser1@test.com",
        password="pass12345"
    )

    with pytest.raises(HTTPException) as exc_info:
        users.crud_update_user(db=db, user_id=1, user_update=update_request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "New password must be different from current password."


def test_update_user_delete_user(db):
    user_data_1 = UserCreate(
        username="testuser",
        email="testuser@test.com",
        password="pass12345"
    )

    users.crud_register_new_user(db=db, user=user_data_1)

    deleted_response = users.crud_delete_user(db=db, user_id=1)

    all_users = db.query(User).all()

    assert deleted_response["user_id"] == 1
    assert deleted_response["message"] == f"User: 1 successfully deleted."
    assert all_users == []


def test_update_user_delete_user_does_not_exist(db):
    with pytest.raises(HTTPException) as exc_info:
        users.crud_delete_user(db=db, user_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"User: 1 not found."
