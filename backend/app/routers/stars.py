import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies import CurrentUser
from app.schemas.common import MessageResponse
from app.schemas.star import (
    SimilarStarPreview,
    StarCreate,
    StarResponse,
    StarUpdate,
    ViewEventCreate,
    VisibilityUpdate,
)
from app.services.star_service import StarError, StarService

router = APIRouter(prefix="/stars", tags=["stars"])


@router.get("/galaxy/{galaxy_id}", response_model=list[StarResponse])
async def list_stars_in_galaxy(
    galaxy_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[StarResponse]:
    service = StarService(session)
    try:
        return await service.get_stars_in_galaxy(current_user.id, galaxy_id)
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/preview-similar", response_model=list[SimilarStarPreview])
async def preview_similar(
    galaxy_id: uuid.UUID,
    title: str,
    content: str,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[SimilarStarPreview]:
    """의미적으로 가까운 이웃을 미리 본다. 이 POST는 의도적으로 임베딩을 호출한다."""
    service = StarService(session)
    try:
        return await service.preview_similar(current_user.id, galaxy_id, title, content)
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("", response_model=StarResponse, status_code=status.HTTP_201_CREATED)
async def create_star(
    body: StarCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StarResponse:
    """기본 비공개 항성을 만들고 최초 고정 좌표를 배정한다."""
    service = StarService(session)
    try:
        return await service.create_star(
            user_id=current_user.id,
            galaxy_id=body.galaxy_id,
            title=body.title,
            slug=body.slug,
            content=body.content,
        )
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.put("/{star_id}", response_model=StarResponse)
async def update_star(
    star_id: uuid.UUID,
    body: StarUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StarResponse:
    service = StarService(session)
    try:
        return await service.update_star(
            user_id=current_user.id,
            star_id=star_id,
            title=body.title,
            content=body.content,
            galaxy_id=body.galaxy_id,
        )
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{star_id}", response_model=MessageResponse)
async def delete_star(
    star_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageResponse:
    service = StarService(session)
    try:
        await service.delete_star(current_user.id, star_id)
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return MessageResponse(message="Star deleted")


@router.post("/{star_id}/view", response_model=StarResponse)
async def record_view(
    star_id: uuid.UUID,
    body: ViewEventCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StarResponse:
    """체류/편집 에너지를 기록하고, 유효하면 1-hop Nova 전파를 실행한다."""
    service = StarService(session)
    try:
        return await service.record_view(
            user_id=current_user.id,
            star_id=star_id,
            duration_seconds=body.duration_seconds,
            is_edit=body.is_edit,
        )
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{star_id}/visibility", response_model=StarResponse)
async def update_visibility(
    star_id: uuid.UUID,
    body: VisibilityUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StarResponse:
    """공개 explore와 username/slug URL에 쓰는 소유자 전용 공개 토글."""
    service = StarService(session)
    try:
        return await service.set_visibility(current_user.id, star_id, body.is_public)
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
