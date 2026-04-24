import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.star import Star
from app.models.view_event import VALID_DWELL_SECONDS
from app.repositories.galaxy_repo import GalaxyRepository
from app.repositories.star_repo import StarRepository
from app.repositories.user_repo import UserRepository
from app.repositories.view_event_repo import ViewEventRepository
from app.schemas.star import SimilarStarPreview, StarResponse
from app.services import embedding as embed_svc
from app.services.lifecycle import NOVA_ENERGY_RATIO, compute_lifecycle
from app.services.umap_service import place_new_star

NOVA_K = 5  # number of similar stars to propagate Nova energy to


class StarError(Exception):
    pass


class StarService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = StarRepository(session)
        self._galaxy_repo = GalaxyRepository(session)
        self._view_repo = ViewEventRepository(session)

    async def get_stars_in_galaxy(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> list[StarResponse]:
        await self._assert_galaxy_owned(user_id, galaxy_id)
        stars = await self._repo.list_by_galaxy(galaxy_id)
        return [await self._to_response(s) for s in stars]

    async def get_public_star(self, username: str, slug: str) -> tuple[Star, str]:
        """Returns (star, username)."""
        user_repo = UserRepository(self._session)
        user = await user_repo.get_by_username(username)
        if user is None:
            raise StarError("User not found")

        star = await self._repo.get_public_by_username_slug(username, slug)
        if star is None:
            raise StarError("Star not found or not public")
        return star, username

    async def preview_similar(
        self, user_id: uuid.UUID, galaxy_id: uuid.UUID, title: str, content: str
    ) -> list[SimilarStarPreview]:
        await self._assert_galaxy_owned(user_id, galaxy_id)
        text = f"{title}\n{content}"
        vec = await embed_svc.embed_text(text)
        similar = await self._repo.find_similar_in_galaxy(galaxy_id, vec, k=5)
        return [
            SimilarStarPreview(id=s.id, title=s.title, similarity=round(sim, 3))
            for s, sim in similar
            if sim > 0.5
        ]

    async def create_star(
        self,
        user_id: uuid.UUID,
        galaxy_id: uuid.UUID,
        title: str,
        slug: str,
        content: str,
    ) -> StarResponse:
        await self._assert_galaxy_owned(user_id, galaxy_id)

        if await self._repo.get_by_user_and_slug(user_id, slug):
            raise StarError(f"Slug '{slug}' already in use")

        text = f"{title}\n{content}"
        vec = await embed_svc.embed_text(text)

        existing = await self._repo.list_by_galaxy(galaxy_id)
        pos_x, pos_y = place_new_star(existing, vec)

        star = await self._repo.create(
            user_id=user_id,
            galaxy_id=galaxy_id,
            title=title,
            slug=slug,
            content=content,
            embedding=vec,
            pos_x=pos_x,
            pos_y=pos_y,
        )
        await self._session.commit()
        return await self._to_response(star)

    async def update_star(
        self,
        user_id: uuid.UUID,
        star_id: uuid.UUID,
        title: str | None,
        content: str | None,
        galaxy_id: uuid.UUID | None,
    ) -> StarResponse:
        star = await self._get_owned(user_id, star_id)

        if galaxy_id is not None:
            await self._assert_galaxy_owned(user_id, galaxy_id)

        new_embedding: list[float] | None = None
        if title is not None or content is not None:
            new_title = title or star.title
            new_content = content if content is not None else star.content
            new_embedding = await embed_svc.embed_text(f"{new_title}\n{new_content}")

        star = await self._repo.update(
            star,
            title=title,
            content=content,
            embedding=new_embedding,
            galaxy_id=galaxy_id,
        )
        await self._session.commit()
        return await self._to_response(star)

    async def delete_star(self, user_id: uuid.UUID, star_id: uuid.UUID) -> None:
        star = await self._get_owned(user_id, star_id)
        await self._repo.delete(star)
        await self._session.commit()

    async def set_visibility(
        self, user_id: uuid.UUID, star_id: uuid.UUID, is_public: bool
    ) -> StarResponse:
        star = await self._get_owned(user_id, star_id)
        star = await self._repo.update_visibility(star, is_public)
        await self._session.commit()
        return await self._to_response(star)

    async def record_view(
        self,
        user_id: uuid.UUID,
        star_id: uuid.UUID,
        duration_seconds: int,
        is_edit: bool,
    ) -> StarResponse:
        star = await self._get_owned(user_id, star_id)
        is_valid = is_edit or duration_seconds >= VALID_DWELL_SECONDS

        base_energy = 2.0 if is_edit else 1.0
        await self._view_repo.create(
            star_id=star_id,
            user_id=user_id,
            duration_seconds=duration_seconds,
            is_valid=is_valid,
            is_edit=is_edit,
            energy_value=base_energy,
        )

        if is_valid:
            await self._propagate_nova(star, base_energy)

        await self._session.commit()
        return await self._to_response(star)

    async def list_public(self, limit: int, offset: int) -> list[Star]:
        return await self._repo.list_public(limit=limit, offset=offset)

    async def _propagate_nova(self, source_star: Star, base_energy: float) -> None:
        nova_energy = base_energy * NOVA_ENERGY_RATIO
        similar = await self._repo.find_similar_in_galaxy(
            source_star.galaxy_id,
            source_star.embedding,
            exclude_id=source_star.id,
            k=NOVA_K,
        )
        for target_star, _ in similar:
            await self._view_repo.create(
                star_id=target_star.id,
                user_id=source_star.user_id,
                duration_seconds=0,
                is_valid=True,
                is_edit=False,
                energy_value=nova_energy,
            )

    async def _to_response(self, star: Star) -> StarResponse:
        recent_events = await self._view_repo.list_recent_by_star(star.id, days=30)
        last_valid = await self._view_repo.get_last_valid(star.id)
        state, energy = compute_lifecycle(recent_events, last_valid)
        return StarResponse(
            id=star.id,
            user_id=star.user_id,
            galaxy_id=star.galaxy_id,
            title=star.title,
            slug=star.slug,
            content=star.content,
            pos_x=star.pos_x,
            pos_y=star.pos_y,
            is_public=star.is_public,
            lifecycle_state=state,
            energy_score=energy,
        )

    async def _get_owned(self, user_id: uuid.UUID, star_id: uuid.UUID) -> Star:
        star = await self._repo.get_by_id(star_id)
        if star is None or star.user_id != user_id:
            raise StarError("Star not found")
        return star

    async def _assert_galaxy_owned(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> None:
        galaxy = await self._galaxy_repo.get_by_id(galaxy_id)
        if galaxy is None or galaxy.user_id != user_id:
            raise StarError("Galaxy not found")
