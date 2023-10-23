import time
import jwt
from typing import Tuple
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import settings
from app.api.models import UserModel
from app.core.db import get_async_session
from app.core.security.exceptions import AuthPasswordError, AuthUserNotFoundError, JWTDecodeError, JWTTokenInvalidError, JWTTokenExpiredError
from app.core.security.schemas import AccessTokenResponse, JWTSubject, JWTTokenPayload

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECS = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_EXPIRE_SECS = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
PWD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.SECURITY_BCRYPT_ROUNDS,
)

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="auth/access-token")



class JWTService:

    @classmethod
    def __decode_jwt_token(cls, token: str) -> dict:
        try:
            return jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
            )
        except (jwt.DecodeError, ValidationError):
            raise JWTDecodeError("Could not validate credentials, unknown error")

    @classmethod
    def __is_token_time_valid(cls, token_data: JWTTokenPayload) -> None:
        now = int(time.time())
        if now < token_data.issued_at or now > token_data.expires_at:
            raise JWTTokenExpiredError(
                "Could not validate credentials, token expired or not yet valid"
            )

    @classmethod
    def create_jwt_token(
        cls, subject: str | int, exp_secs: int, refresh: bool
    ) -> Tuple[str, int, int]:
        """Creates jwt access or refresh token for user.

        Args:
            subject: anything unique to user, id or email or payload etc.
            exp_secs: expire time in seconds
            refresh: if True, this is refresh token
        """

        issued_at = int(time.time())
        expires_at = issued_at + exp_secs

        to_encode: dict[str, int | str | bool] = JWTTokenPayload(
            sub=JWTSubject(user_uuid=subject),
            refresh=refresh,
            issued_at=issued_at,
            expires_at=expires_at,
        ).dict()
        encoded_jwt = jwt.encode(
            to_encode,
            key=settings.SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )
        return encoded_jwt, expires_at, issued_at

    @classmethod
    def generate_access_token_response(cls, subject: str | int) -> AccessTokenResponse:
        """Generate tokens and return AccessTokenResponse"""
        access_token, expires_at, issued_at = cls.create_jwt_token(
            subject, ACCESS_TOKEN_EXPIRE_SECS, refresh=False
        )
        refresh_token, refresh_expires_at, refresh_issued_at = cls.create_jwt_token(
            subject, REFRESH_TOKEN_EXPIRE_SECS, refresh=True
        )
        return AccessTokenResponse(
            token_type="Bearer",
            access_token=access_token,
            expires_at=expires_at,
            issued_at=issued_at,
            refresh_token=refresh_token,
            refresh_token_expires_at=refresh_expires_at,
            refresh_token_issued_at=refresh_issued_at,
        )

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies plain and hashed password matches

        Applies passlib context based on bcrypt algorithm on plain passoword.
        It takes about 0.3s for default 12 rounds of SECURITY_BCRYPT_DEFAULT_ROUNDS.
        """
        return PWD_CONTEXT.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Creates hash from password

        Applies passlib context based on bcrypt algorithm on plain passoword.
        It takes about 0.3s for default 12 rounds of SECURITY_BCRYPT_DEFAULT_ROUNDS.
        """
        return PWD_CONTEXT.hash(password)

    @classmethod
    def decode_token(cls, token: str, refresh: bool = False) -> JWTTokenPayload:
        payload = cls.__decode_jwt_token(token=token)
        token_data: JWTTokenPayload = JWTTokenPayload(**payload)

        if refresh and not token_data.refresh:
            raise JWTTokenInvalidError("Could not validate credentials, cannot use access token")

        cls.__is_token_time_valid(token_data=token_data)
        return token_data


class AuthenticationService:
    __db_async_session: AsyncSession = None
    __user: UserModel = None
    __token_data: JWTTokenPayload

    # TODO cache?
    async def get_current_user(self) -> UserModel:
        if not self.__user:
            result = await self.__db_async_session.execute(
                select(UserModel).where(UserModel.uuid == self.__token_data.sub.user_uuid)
            )
            user: UserModel = result.scalars().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )
            self.__user = user
        return self.__user

    def __init__(
        self,
        token: str = Depends(reusable_oauth2),
        # TODO Usar AsyncDatabaseContext
        db_async_session: AsyncSession = Depends(get_async_session),
    ):
        self.__db_async_session = db_async_session
        self.__token_data = JWTService.decode_token(token=token)

    @property
    def user_uuid(self):
        return self.__token_data.sub.user_uuid

    @classmethod
    async def login_access_token(
        cls,
        form_data: OAuth2PasswordRequestForm,
        db_async_session: AsyncSession,
    ) -> AccessTokenResponse:
        """OAuth2 compatible token, get an access token for future requests using username and password"""

        result = await db_async_session.execute(select(UserModel).where(UserModel.nickname == form_data.username))
        user: UserModel = result.scalars().first()

        if user is None:
            raise AuthUserNotFoundError("Incorrect nickname or password")

        if not JWTService.verify_password(form_data.password, user.hashed_password):
            raise AuthPasswordError("Incorrect password format")

        return JWTService.generate_access_token_response(str(user.uuid))

    @classmethod
    async def refresh_access_token(
        cls,
        input_token: str,
        db_async_session: AsyncSession,
    ) -> AccessTokenResponse:
        token_data: JWTTokenPayload = JWTService.decode_token(token=input_token, refresh=True)

        result = await db_async_session.execute(
            select(UserModel).where(UserModel.uuid == token_data.sub.user_uuid)
        )
        user: UserModel = result.scalars().first()

        if user is None:
            raise AuthUserNotFoundError("User not found")

        return JWTService.generate_access_token_response(str(user.uuid))
