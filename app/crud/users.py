from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Type, List

from app.models import User
from app.schemas.users import UserCreate, UserLogin, UserUpdate, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token


def crud_register_new_user(db: Session, user: UserCreate) -> User:
    db_user_username = db.query(User).filter(User.username == user.username).first()
    if db_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )

    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def crud_authenticate_user(db: Session, username: str, password: str) -> Type[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    return user


def crud_login_user(db: Session, user_login: UserLogin) -> dict:
    authenticated_user = crud_authenticate_user(
        db=db,
        username=user_login.username,
        password=user_login.password
    )
    access_token = create_access_token(user_id=authenticated_user.id)

    return {"access_token": access_token, "token_type": "bearer"}


def crud_login_user_oauth(db: Session, form_data: OAuth2PasswordRequestForm) -> dict:
    authenticated_user = crud_authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    access_token = create_access_token(user_id=authenticated_user.id)

    return {"access_token": access_token, "token_type": "bearer"}


def crud_fetch_user_by_username(db: Session, username: str) -> Type[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Username: '{username}' not found."
        )

    return user


def crud_fetch_user_by_id(db: Session, user_id: int) -> Type[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User_id: '{user_id}' not found."
        )

    return user


def crud_fetch_all_users(db: Session) -> List[Type[User]]:
    users = db.query(User).all()
    return users


# TODO: crud_delete_user
def crud_update_user(db: Session, user_id: int, user_update: UserUpdate) -> dict:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{user_id} not found."
        )

    old_data = UserResponse(id=db_user.id, username=db_user.username, email=db_user.email)

    changes = {"Username": False, "Email": False, "Password": False}

    if user_update.username:
        if user_update.username == db_user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{user_update.username}' is already your username."
            )

        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{user_update.username}' is already taken."
            )

        db_user.username = user_update.username
        changes["Username"] = True

    if user_update.email:
        if user_update.email == db_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{user_update.email}' is already your email."
            )

        existing_email = db.query(User).filter(User.email == user_update.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{user_update.email}' is already taken."
            )

        db_user.email = user_update.email
        changes["Email"] = True

    if user_update.password:
        if verify_password(user_update.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password."
            )

        db_user.password_hash = hash_password(user_update.password)
        changes["Password"] = True

    db.commit()
    db.refresh(db_user)

    updated_data = UserResponse(id=db_user.id, username=db_user.username, email=db_user.email)

    updated_vals = [key for key, val in changes.items() if val]
    update_message = (
        f"{updated_vals[0]} successfully updated."
        if len(updated_vals) == 1
        else "Credentials successfully updated."
    )

    return {"old_data": old_data, "updated_data": updated_data, "changes": changes, "update_message": update_message}


def crud_delete_user(db: Session, user_id: int) -> dict:
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User: {user_id} not found."
        )

    db.delete(db_user)
    db.commit()

    return {"user_id": user_id, "message": f"User: {user_id} successfully deleted."}
