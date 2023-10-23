from abc import ABC

from fastapi import Query, Request, FastAPI

from app.core.config import Settings, settings
from app.core.db import AsyncDatabaseContext


class BaseAppService(ABC):
    __app: FastAPI
    __request: Request

    def __init__(
        self,
        app: FastAPI = Query(default=None, include_in_schema=False),
        request: Request | None = None,
    ):
        self.__app = request.app if request else app
        self.__request = request

    @property
    def app(self) -> FastAPI:
        return self.__app

    @property
    def request(self) -> Request:
        return self.__request

    @property
    def settings(self) -> Settings:
        return self.app.state.settings


class BaseDatabaseService(ABC):
    __async_db_context: AsyncDatabaseContext

    def __init__(self):
        self.__async_db_context = AsyncDatabaseContext.with_config(settings=settings)

    @property
    def async_db_context(self) -> AsyncDatabaseContext:
        return self.__async_db_context
