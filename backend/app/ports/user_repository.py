import uuid
from typing import Protocol

from app.models.user import User


class UserRepositoryPort(Protocol):
    """사용자 영속성 기능 포트."""

    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def get_by_username(self, username: str) -> User | None: ...

    async def create(self, username: str, email: str, password_hash: str) -> User: ...
