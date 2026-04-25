from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.user_repo import UserRepository
from app.repositories.view_event_repo import ViewEventRepository
from app.schemas.star import StarPublicResponse
from app.services.lifecycle import compute_lifecycle
from app.services.star_service import StarError, StarService

router = APIRouter(tags=["explore"])


@router.get("/explore", response_model=list[StarPublicResponse])
async def list_public_stars(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[StarPublicResponse]:
    """
    공개 카드 피드. is_public=true인 항성만 여기에 노출된다.

    Args:
        session: 요청 범위에서 공유하는 비동기 DB 세션.
        limit: 한 번에 반환할 공개 항성 최대 개수. 1~100 사이만 허용한다.
        offset: 페이지네이션을 위해 앞에서 건너뛸 공개 항성 개수.
    """
    service = StarService(session)
    stars = await service.list_public(limit=limit, offset=offset)

    user_repo = UserRepository(session)
    view_repo = ViewEventRepository(session)
    result = []
    for star in stars:
        user = await user_repo.get_by_id(star.user_id)
        if user is None:
            continue
        recent = await view_repo.list_recent_by_star(star.id, days=30)
        last_valid = await view_repo.get_last_valid(star.id)
        state, _ = compute_lifecycle(recent, last_valid)
        result.append(
            StarPublicResponse(
                id=star.id,
                username=user.username,
                galaxy_id=star.galaxy_id,
                title=star.title,
                slug=star.slug,
                content=star.content,
                lifecycle_state=state,
            )
        )
    return result


@router.get("/{username}/stars/{slug}", response_model=StarPublicResponse)
async def get_public_star(
    username: str,
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StarPublicResponse:
    """
    공개 username/slug 페이지. 비공개 또는 없는 항성은 의도적으로 403을 반환한다.

    Args:
        username: 공개 URL에서 받은 항성 소유자의 username.
        slug: 공개 URL에서 받은 사용자 범위의 항성 slug.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = StarService(session)
    view_repo = ViewEventRepository(session)
    try:
        star, uname = await service.get_public_star(username, slug)
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

    recent = await view_repo.list_recent_by_star(star.id, days=30)
    last_valid = await view_repo.get_last_valid(star.id)
    state, _ = compute_lifecycle(recent, last_valid)

    return StarPublicResponse(
        id=star.id,
        username=uname,
        galaxy_id=star.galaxy_id,
        title=star.title,
        slug=star.slug,
        content=star.content,
        lifecycle_state=state,
    )
