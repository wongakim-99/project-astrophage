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
