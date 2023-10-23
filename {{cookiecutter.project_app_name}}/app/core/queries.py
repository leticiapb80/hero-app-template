from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

DatabaseModel = TypeVar("DatabaseModel", bound=SQLModel)


class BaseQueryset(ABC, Generic[DatabaseModel]):
    #: Database Model class
    __db_model_class: SQLModel = None
    #: Database object (select, delete), SqlAlchemy statement (from sqlalchemy.sql.expression)
    __queryset = None
    #: Database async session
    __async_session: AsyncSession = None

    def __init__(self, async_session: AsyncSession):
        self.__db_model_class = self._get_db_model_class()
        self.__async_session = async_session

    @abstractmethod
    def _get_db_model_class(self) -> DatabaseModel:
        raise NotImplementedError
