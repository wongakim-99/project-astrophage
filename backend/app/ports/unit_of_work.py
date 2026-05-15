from typing import Protocol


class UnitOfWorkPort(Protocol):
    """트랜잭션 완료와 영속 객체 갱신을 추상화하는 포트."""

    async def commit(self) -> None: ...

    async def refresh(self, entity: object) -> None: ...
