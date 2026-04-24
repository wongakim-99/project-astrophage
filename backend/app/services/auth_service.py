from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, UserResponse


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def register(self, username: str, email: str, password: str) -> tuple[UserResponse, TokenResponse]:
        if await self._repo.get_by_email(email):
            raise AuthError("Email already registered")
        if await self._repo.get_by_username(username):
            raise AuthError("Username already taken")

        user = await self._repo.create(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )

        tokens = TokenResponse(
            access_token=create_access_token(str(user.id)),
        )
        user_response = UserResponse(id=str(user.id), username=user.username, email=user.email)
        return user_response, tokens

    async def login(self, email: str, password: str) -> tuple[UserResponse, TokenResponse, str]:
        """Returns (user, access_token_response, refresh_token)."""
        user = await self._repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Invalid email or password")

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        tokens = TokenResponse(access_token=access_token)
        user_response = UserResponse(id=str(user.id), username=user.username, email=user.email)
        return user_response, tokens, refresh_token

    async def refresh(self, user_id: str) -> TokenResponse:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise AuthError("User not found")
        return TokenResponse(access_token=create_access_token(str(user.id)))
