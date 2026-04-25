import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.star import Star


class StarRepository:
    """항성 DB 접근 클래스. pgvector 유사도 쿼리도 여기에서 처리한다."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: 현재 요청 또는 작업에서 공유하는 비동기 DB 세션.
        """
        self._session = session

    async def get_by_id(self, star_id: uuid.UUID) -> Star | None:
        """
        Args:
            star_id: 조회할 Star의 기본키 UUID.
        """
        result = await self._session.execute(select(Star).where(Star.id == star_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_slug(self, user_id: uuid.UUID, slug: str) -> Star | None:
        """
        Args:
            user_id: Star를 소유한 사용자 UUID. 사용자별 slug 유일성 범위를 정한다.
            slug: 사용자의 공개 URL과 개인 영역에서 Star를 식별하는 URL용 문자열.
        """
        result = await self._session.execute(
            select(Star).where(Star.user_id == user_id, Star.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_public_by_username_slug(self, username: str, slug: str) -> Star | None:
        """
        공개 항성만 조회한다. 비공개 항성은 공개 URL로 노출되면 안 된다.

        Args:
            username: 공개 URL 경로에서 받은 소유자 username.
            slug: 공개 URL 경로에서 받은 Star slug.
        """
        from app.models.user import User

        result = await self._session.execute(
            select(Star)
            .join(User, Star.user_id == User.id)
            .where(User.username == username, Star.slug == slug, Star.is_public == True)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def list_by_galaxy(self, galaxy_id: uuid.UUID) -> list[Star]:
        """
        Args:
            galaxy_id: 항성 목록을 가져올 Galaxy UUID.
        """
        result = await self._session.execute(
            select(Star).where(Star.galaxy_id == galaxy_id).order_by(Star.created_at)
        )
        return list(result.scalars().all())

    async def list_by_user(self, user_id: uuid.UUID) -> list[Star]:
        """
        Args:
            user_id: 항성 목록을 가져올 소유자 UUID.
        """
        result = await self._session.execute(
            select(Star).where(Star.user_id == user_id).order_by(Star.created_at)
        )
        return list(result.scalars().all())

    async def list_public(self, limit: int = 50, offset: int = 0) -> list[Star]:
        """
        공개 explore 피드용 목록. 화면 표시용 필드는 호출자가 별도로 붙인다.

        Args:
            limit: 한 번에 가져올 공개 Star 최대 개수.
            offset: 페이지네이션을 위해 건너뛸 공개 Star 개수.
        """
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
        """
        같은 은하 안에서 코사인 유사도가 높은 상위 k개 항성을 반환한다.

        Args:
            galaxy_id: 유사 항성을 찾을 Galaxy UUID.
            embedding: 비교 기준이 되는 1536차원 임베딩 벡터.
            exclude_id: 결과에서 제외할 Star UUID. 자기 자신을 제외할 때 사용한다.
            k: 반환할 최대 유사 Star 개수.
        """
        query = (
            select(Star, Star.embedding.cosine_distance(embedding).label("distance"))
            .where(Star.galaxy_id == galaxy_id)
        )
        if exclude_id is not None:
            query = query.where(Star.id != exclude_id)
        query = query.order_by(text("distance")).limit(k)

        result = await self._session.execute(query)
        rows = result.all()
        # pgvector는 cosine distance를 반환하므로 service에서 쓰는 similarity로 변환한다.
        return [(row[0], 1.0 - row[1]) for row in rows]

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
        """
        Args:
            user_id: 새 Star를 소유할 사용자 UUID.
            galaxy_id: 새 Star가 배치될 Galaxy UUID.
            title: 화면과 공개 URL 목록에 표시할 Star 제목.
            slug: 사용자별로 유일해야 하는 URL용 Star 식별자.
            content: Star 본문 텍스트.
            embedding: title과 content로 생성한 1536차원 임베딩 벡터.
            pos_x: Galaxy 맵에서 사용할 고정 x 좌표.
            pos_y: Galaxy 맵에서 사용할 고정 y 좌표.
        """
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
        """
        고정 좌표는 건드리지 않고 수정 가능한 콘텐츠 필드만 갱신한다.

        Args:
            star: 수정할 영속 상태의 Star 모델 인스턴스.
            title: 새 Star 제목. None이면 기존 값을 유지한다.
            content: 새 Star 본문. None이면 기존 값을 유지한다.
            embedding: 콘텐츠 변경 후 재계산한 임베딩 벡터. None이면 기존 값을 유지한다.
            galaxy_id: Star를 이동할 대상 Galaxy UUID. None이면 기존 Galaxy에 둔다.
        """
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
        """
        Args:
            star: 공개 여부를 변경할 영속 상태의 Star 모델 인스턴스.
            is_public: True이면 공개 URL과 explore 피드에 노출하고, False이면 숨긴다.
        """
        star.is_public = is_public
        await self._session.flush()
        await self._session.refresh(star)
        return star

    async def delete(self, star: Star) -> None:
        """
        Args:
            star: 삭제할 영속 상태의 Star 모델 인스턴스.
        """
        await self._session.delete(star)
        await self._session.flush()
