from typing import Optional
import uuid as uuid_pkg

from sqlalchemy import Column, event
from sqlalchemy.databases import postgres
from sqlmodel import SQLModel, Field

from app.core.models import TimestampModel, UUIDModel


prefix = "hrs"

hrs_role_type = postgres.ENUM(
    "mage",
    "assassin",
    "warrior",
    "priest",
    "tank",
    name=f"{prefix}_role",
)


@event.listens_for(SQLModel.metadata, "before_create")
def _create_enums(metadata, conn, **kw):  # noqa: indirect usage
    hrs_role_type.create(conn, checkfirst=True)


class UserBase(SQLModel):
    email: str
    nickname: str


class UserModel(TimestampModel, UUIDModel, UserBase, table=True):
    __tablename__ = f"{prefix}_users"

    hashed_password: str


class HeroBase(SQLModel):
    nickname: str = Field(max_length=255, nullable=False)
    role: Optional[str] = Field(
        sa_column=Column(
            "role",
            hrs_role_type,
            nullable=True,
        ),
    )


class HeroModel(TimestampModel, UUIDModel, HeroBase, table=True):
    __tablename__ = f"{prefix}_heroes"

    user_uuid: Optional[uuid_pkg.UUID] = Field(default=None, foreign_key=f"{prefix}_users.uuid")
