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

# 유효 조회에서 Nova 에너지를 받을 같은 은하 내 이웃 항성 수.
NOVA_K = 5


class StarError(Exception):
    """라우터가 HTTP 오류로 변환할 항성 도메인 예외."""

    pass


class StarService:
    """항성의 소유권, 임베딩, 배치, 생애주기, 공개 여부 규칙을 담당한다."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: 항성/은하/이벤트 조회와 commit에 사용할 요청 범위 비동기 DB 세션.
        """
        self._session = session
        self._repo = StarRepository(session)
        self._galaxy_repo = GalaxyRepository(session)
        self._view_repo = ViewEventRepository(session)

    async def get_stars_in_galaxy(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> list[StarResponse]:
        """
        사용자 본인의 항성만 나열한다. 공개 피드 규칙은 이 경로에 섞지 않는다.

        Args:
            user_id: 목록 조회를 요청한 사용자 UUID.
            galaxy_id: 항성 목록을 가져올 Galaxy UUID.
        """
        await self._assert_galaxy_owned(user_id, galaxy_id)
        stars = await self._repo.list_by_galaxy(galaxy_id)
        return [await self._to_response(s) for s in stars]

    async def get_public_star(self, username: str, slug: str) -> tuple[Star, str]:
        """
        공개 username/slug 경로에서 노출 가능한 항성만 찾아 (star, username)을 반환한다.

        Args:
            username: 공개 URL에 포함된 항성 소유자 username.
            slug: 공개 URL에 포함된 사용자 범위 Star slug.
        """
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
        """
        항성을 저장하기 전에 생성 모달용 유사 항성 미리보기를 계산한다.

        Args:
            user_id: 미리보기를 요청한 사용자 UUID.
            galaxy_id: 유사 항성을 검색할 Galaxy UUID.
            title: 임베딩 기준 텍스트에 포함할 임시 항성 제목.
            content: 임베딩 기준 텍스트에 포함할 임시 항성 본문.
        """
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
        """
        소유 은하 안에 기본 비공개 항성을 만들고 최초 고정 좌표를 배정한다.

        Args:
            user_id: 새 항성을 소유할 사용자 UUID.
            galaxy_id: 새 항성이 배치될 Galaxy UUID.
            title: 화면과 공개 목록에 표시할 항성 제목.
            slug: 사용자 범위에서 유일해야 하는 URL용 항성 식별자.
            content: 항성 본문 텍스트. title과 함께 임베딩 입력으로 사용된다.
        """
        await self._assert_galaxy_owned(user_id, galaxy_id)

        if await self._repo.get_by_user_and_slug(user_id, slug):
            raise StarError(f"Slug '{slug}' already in use")

        # 임베딩은 명시적인 생성/수정 흐름에서만 만든다. GET 엔드포인트는
        # 지연과 API 비용을 피하기 위해 저장된 벡터를 재사용해야 한다.
        text = f"{title}\n{content}"
        vec = await embed_svc.embed_text(text)

        existing = await self._repo.list_by_galaxy(galaxy_id)
        # 새 항성은 유사한 기존 항성 근처에 배치하되, 기존 좌표는 움직이지 않는다.
        # 사용자가 익힌 우주 지도를 보존하기 위한 규칙이다.
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
        """
        항성의 제목, 본문, 소속 은하를 수정한다. 의미 콘텐츠가 바뀌면 임베딩만 갱신한다.

        Args:
            user_id: 수정을 요청한 사용자 UUID.
            star_id: 수정할 Star UUID.
            title: 새 항성 제목. None이면 기존 값을 유지한다.
            content: 새 항성 본문. None이면 기존 값을 유지한다.
            galaxy_id: 이동할 대상 Galaxy UUID. None이면 기존 은하에 둔다.
        """
        star = await self._get_owned(user_id, star_id)

        if galaxy_id is not None:
            await self._assert_galaxy_owned(user_id, galaxy_id)

        new_embedding: list[float] | None = None
        if title is not None or content is not None:
            new_title = title or star.title
            new_content = content if content is not None else star.content
            # 의미 콘텐츠가 바뀔 때만 다시 임베딩한다. 임베딩이 바뀌어도 좌표는 고정한다.
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
        """
        소유권을 확인한 뒤 항성을 삭제한다.

        Args:
            user_id: 삭제를 요청한 사용자 UUID.
            star_id: 삭제할 Star UUID.
        """
        star = await self._get_owned(user_id, star_id)
        await self._repo.delete(star)
        await self._session.commit()

    async def set_visibility(
        self, user_id: uuid.UUID, star_id: uuid.UUID, is_public: bool
    ) -> StarResponse:
        """
        소유자의 명시적 액션으로만 항성을 공개/비공개 전환한다.

        Args:
            user_id: 공개 상태 변경을 요청한 사용자 UUID.
            star_id: 공개 여부를 변경할 Star UUID.
            is_public: True이면 공개 URL과 explore 피드에 노출하고, False이면 숨긴다.
        """
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
        """
        체류/편집 이벤트를 저장하고 유효 이벤트이면 유사 항성에 Nova 에너지를 전파한다.

        Args:
            user_id: 이벤트를 발생시킨 사용자 UUID.
            star_id: 이벤트가 기록될 Star UUID.
            duration_seconds: 사용자가 항성에 머문 시간(초). 편집 이벤트도 요청 본문 값을 보존한다.
            is_edit: 편집으로 발생한 이벤트인지 여부. 편집은 항상 유효 에너지로 처리한다.
        """
        star = await self._get_owned(user_id, star_id)
        # 편집은 항상 유효 에너지이며 2배로 계산한다. 단순 조회는 30초 체류 기준을 만족해야 한다.
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
        """
        공개 explore 피드에 노출할 항성 목록을 가져온다.

        Args:
            limit: 한 번에 가져올 공개 항성 최대 개수.
            offset: 페이지네이션을 위해 건너뛸 공개 항성 개수.
        """
        return await self._repo.list_public(limit=limit, offset=offset)

    async def _propagate_nova(self, source_star: Star, base_energy: float) -> None:
        """
        같은 은하 안의 유사 항성에 1-hop Nova 에너지를 적용한다.

        Args:
            source_star: 직접 조회 또는 편집 이벤트가 발생한 원본 Star.
            base_energy: 원본 이벤트의 에너지 값. Nova 전파 비율을 곱하는 기준값이다.
        """
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
        """
        저장된 항성 필드에 실시간 생애주기 상태를 붙인다.

        Args:
            star: 응답 스키마로 변환할 Star 모델 인스턴스.
        """
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
        """
        인증 라우트에서 항성을 가져오며 개인 소유권을 검증한다.

        Args:
            user_id: 소유권을 확인할 사용자 UUID.
            star_id: 소유 여부를 확인할 Star UUID.
        """
        star = await self._repo.get_by_id(star_id)
        if star is None or star.user_id != user_id:
            raise StarError("Star not found")
        return star

    async def _assert_galaxy_owned(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> None:
        """
        다른 사용자의 은하에 항성을 생성하거나 이동하지 못하게 막는다.

        Args:
            user_id: 소유권을 확인할 사용자 UUID.
            galaxy_id: 소유 여부를 확인할 Galaxy UUID.
        """
        galaxy = await self._galaxy_repo.get_by_id(galaxy_id)
        if galaxy is None or galaxy.user_id != user_id:
            raise StarError("Galaxy not found")
