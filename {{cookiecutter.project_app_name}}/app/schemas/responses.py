from pydantic import BaseModel, EmailStr

from app.core.models import UUIDModel
from app.api.models import UserBase, HeroBase


class BaseResponse(BaseModel):
    # may define additional fields or config shared across responses
    class Config:
        orm_mode = True


class UserResponse(UserBase, UUIDModel):
    email: EmailStr


class HeroResponse(HeroBase, UUIDModel):
    ...
