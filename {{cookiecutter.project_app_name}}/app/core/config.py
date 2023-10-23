"""
File with environment variables and general configuration logic.
`SECRET_KEY`, `ENVIRONMENT` etc. map to env variables with the same names.

Pydantic priority ordering:

1. (Most important, will overwrite everything) - environment variables
2. `.env` file in root folder of project
3. Default values

For project name, version, description we use pyproject.toml
For the rest, we use file `.env` (gitignored), see `.env.example`

`DEFAULT_SQLALCHEMY_DATABASE_URI` and `TEST_SQLALCHEMY_DATABASE_URI`:
Both are ment to be validated at the runtime, do not change unless you know
what are you doing. All the two validators do is to build full URI (TCP protocol)
to databases to avoid typo bugs.

See https://pydantic-docs.helpmanual.io/usage/settings/

Note, complex types like lists are read as json-encoded strings.
"""

# import tomllib
import os
from pathlib import Path
from typing import Literal, List
from dotenv import load_dotenv

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator


dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv(dotenv_path=Path(dir_path, "../..", ".env"))


class Settings(BaseSettings):
    # CORE SETTINGS
    SECRET_KEY: str
    ENVIRONMENT: Literal["DEV", "PYTEST", "STG", "PRD"] = "DEV"
    SECURITY_BCRYPT_ROUNDS: int = 12
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 40320  # 28 days
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]

    API_V1_PREFIX: str
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str
    DEBUG: bool

    # POSTGRESQL DATABASE
    DATABASE_HOSTNAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: str
    DATABASE_DB: str
    SQLALCHEMY_DATABASE_URI: str = ""
    DB_EXCLUDE_TABLES: List[str] = [""]

    # POSTGRESQL TEST DATABASE
    TEST_DATABASE_HOSTNAME: str = "postgres"
    TEST_DATABASE_USER: str = "postgres"
    TEST_DATABASE_PASSWORD: str = "postgres"
    TEST_DATABASE_PORT: str = "5432"
    TEST_DATABASE_DB: str = "postgres"
    TEST_SQLALCHEMY_DATABASE_URI: str = ""

    # FIRST SUPERUSER
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # Exaple: SQLALCHEMY_DATABASE_URI="postgresql+asyncpg://hero:heroPass123@0.0.0.0:5432/heroes_db"
    @validator("SQLALCHEMY_DATABASE_URI")
    @classmethod
    def _assemble_default_db_connection(cls, v: str, values: dict[str, str]) -> str:
        print(f"Values init: {values}")
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values["DATABASE_USER"],
            password=values["DATABASE_PASSWORD"],
            host=values["DATABASE_HOSTNAME"],
            port=values["DATABASE_PORT"],
            path=f"/{values['DATABASE_DB']}",
        )

    @validator("TEST_SQLALCHEMY_DATABASE_URI")
    @classmethod
    def _assemble_test_db_connection(cls, v: str, values: dict[str, str]) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values["TEST_DATABASE_USER"],
            password=values["TEST_DATABASE_PASSWORD"],
            host=values["TEST_DATABASE_HOSTNAME"],
            port=values["TEST_DATABASE_PORT"],
            path=f"/{values['TEST_DATABASE_DB']}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True

settings: Settings = Settings()  # type: ignore
