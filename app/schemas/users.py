from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserUpdateResponse(BaseModel):
    old_data: UserResponse
    updated_data: UserResponse
    changes: dict
    update_message: str


class UserDeleteResponse(BaseModel):
    user_id: int
    message: str
