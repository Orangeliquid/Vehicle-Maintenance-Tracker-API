from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.users import UserCreate, UserResponse, UserLogin, UserLoginResponse,UserUpdate, UserUpdateResponse
from app.schemas.users import UserDeleteResponse
from app.crud.users import crud_register_new_user, crud_login_user, crud_login_user_oauth, crud_fetch_user_by_username
from app.crud.users import crud_fetch_user_by_id, crud_fetch_all_users, crud_update_user, crud_delete_user

router = APIRouter()


@router.post(path="/users/", response_model=UserResponse)
def register_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_register_new_user(db=db, user=user)


@router.post(path="/sessions/", response_model=UserLoginResponse)
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    return crud_login_user(db=db, user_login=user_login)


@router.post("/token/", response_model=UserLoginResponse)
def login_user_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return crud_login_user_oauth(db=db, form_data=form_data)


@router.get("/users/{username}/", response_model=UserResponse)
def fetch_user_by_username(username: str, db: Session = Depends(get_db)):
    return crud_fetch_user_by_username(db=db, username=username)


@router.get("/users/{user_id}/", response_model=UserResponse)
def fetch_user_by_user_id(user_id: int, db: Session = Depends(get_db)):
    return crud_fetch_user_by_id(db=db, user_id=user_id)


@router.get("/users/", response_model=List[UserResponse])
def fetch_all_users(db: Session = Depends(get_db)):
    return crud_fetch_all_users(db=db)


@router.put("/users/{user_id}/", response_model=UserUpdateResponse)
def modify_user_information(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    return crud_update_user(db=db, user_id=user_id, user_update=user_update)


@router.delete("/users/{user_id}/", response_model=UserDeleteResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud_delete_user(db=db, user_id=user_id)
