import uuid
from typing import Protocol


class UserRecord(Protocol):
    """인증 유스케이스가 영속성 모델에서 필요로 하는 필드."""

    id: uuid.UUID
    username: str
    email: str
    password_hash: str
    is_universe_public: bool


class UserRepositoryPort(Protocol):
    """사용자 영속성 기능 포트."""

    async def get_by_id(self, user_id: str | uuid.UUID) -> UserRecord | None: ...

    async def get_by_email(self, email: str) -> UserRecord | None: ...

    async def get_by_username(self, username: str) -> UserRecord | None: ...

    async def create(self, username: str, email: str, password_hash: str) -> UserRecord: ...

    async def update_universe_visibility(
        self,
        user: UserRecord,
        is_universe_public: bool,
    ) -> UserRecord: ...
