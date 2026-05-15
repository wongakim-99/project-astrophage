from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUnitOfWork:
    """SQLAlchemy AsyncSession을 트랜잭션 포트로 노출한다."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def refresh(self, entity: object) -> None:
        await self._session.refresh(entity)
