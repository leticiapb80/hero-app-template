from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from sqlmodel import Field

from app.api.models import HeroBase, UserBase
from app.core.models import UUIDModel
from app.core.security.services import JWTService


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class UserUpdatePasswordRequest(BaseRequest):
    password: str

    @validator("password")
    def set_password(cls, value):
        return JWTService.get_password_hash(value)


class UserCreateRequest(UserBase, UserUpdatePasswordRequest):
    email: EmailStr


class HeroRequest(HeroBase, UUIDModel):
    ...


class HeroCreateRequest(HeroBase):
    ...


class HeroPatchRequest(HeroBase):
    nickname: Optional[str] = Field(max_length=255)
