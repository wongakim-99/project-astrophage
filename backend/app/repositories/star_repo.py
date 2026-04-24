import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.star import Star


class StarRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, star_id: uuid.UUID) -> Star | None:
        result = await self._session.execute(select(Star).where(Star.id == star_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_slug(self, user_id: uuid.UUID, slug: str) -> Star | None:
        result = await self._session.execute(
            select(Star).where(Star.user_id == user_id, Star.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_public_by_username_slug(self, username: str, slug: str) -> Star | None:
        from app.models.user import User

        result = await self._session.execute(
            select(Star)
            .join(User, Star.user_id == User.id)
            .where(User.username == username, Star.slug == slug, Star.is_public == True)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def list_by_galaxy(self, galaxy_id: uuid.UUID) -> list[Star]:
        result = await self._session.execute(
            select(Star).where(Star.galaxy_id == galaxy_id).order_by(Star.created_at)
        )
        return list(result.scalars().all())

    async def list_by_user(self, user_id: uuid.UUID) -> list[Star]:
        result = await self._session.execute(
            select(Star).where(Star.user_id == user_id).order_by(Star.created_at)
        )
        return list(result.scalars().all())

    async def list_public(self, limit: int = 50, offset: int = 0) -> list[Star]:
        result = await self._session.execute(
            select(Star)
            .where(Star.is_public == True)  # noqa: E712
            .order_by(Star.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def find_similar_in_galaxy(
        self,
        galaxy_id: uuid.UUID,
        embedding: list[float],
        exclude_id: uuid.UUID | None = None,
        k: int = 5,
    ) -> list[tuple[Star, float]]:
        """Return top-k stars in the galaxy ordered by cosine similarity (highest first)."""
        query = (
            select(Star, Star.embedding.cosine_distance(embedding).label("distance"))
            .where(Star.galaxy_id == galaxy_id)
        )
        if exclude_id is not None:
            query = query.where(Star.id != exclude_id)
        query = query.order_by(text("distance")).limit(k)

        result = await self._session.execute(query)
        rows = result.all()
        return [(row[0], 1.0 - row[1]) for row in rows]  # convert distance to similarity

    async def create(
        self,
        user_id: uuid.UUID,
        galaxy_id: uuid.UUID,
        title: str,
        slug: str,
        content: str,
        embedding: list[float],
        pos_x: float,
        pos_y: float,
    ) -> Star:
        star = Star(
            user_id=user_id,
            galaxy_id=galaxy_id,
            title=title,
            slug=slug,
            content=content,
            embedding=embedding,
            pos_x=pos_x,
            pos_y=pos_y,
        )
        self._session.add(star)
        await self._session.flush()
        await self._session.refresh(star)
        return star

    async def update(
        self,
        star: Star,
        title: str | None = None,
        content: str | None = None,
        embedding: list[float] | None = None,
        galaxy_id: uuid.UUID | None = None,
    ) -> Star:
        if title is not None:
            star.title = title
        if content is not None:
            star.content = content
        if embedding is not None:
            star.embedding = embedding
        if galaxy_id is not None:
            star.galaxy_id = galaxy_id
        await self._session.flush()
        await self._session.refresh(star)
        return star

    async def update_visibility(self, star: Star, is_public: bool) -> Star:
        star.is_public = is_public
        await self._session.flush()
        await self._session.refresh(star)
        return star

    async def delete(self, star: Star) -> None:
        await self._session.delete(star)
        await self._session.flush()
