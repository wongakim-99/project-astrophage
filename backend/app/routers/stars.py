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
    """
    인증된 사용자가 소유한 특정 은하의 항성 목록을 반환한다.

    Args:
        galaxy_id: 항성 목록을 가져올 Galaxy의 path UUID.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
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
    """
    의미적으로 가까운 이웃을 미리 본다. 이 POST는 의도적으로 임베딩을 호출한다.

    Args:
        galaxy_id: 유사 항성을 검색할 Galaxy UUID.
        title: 저장 전 미리보기에 사용할 임시 항성 제목.
        content: 저장 전 미리보기에 사용할 임시 항성 본문.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
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
    """
    기본 비공개 항성을 만들고 최초 고정 좌표를 배정한다.

    Args:
        body: title, slug, content, galaxy_id가 담긴 항성 생성 요청 본문.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
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
    """
    항성의 제목, 본문, 소속 은하를 수정한다. 좌표는 자동으로 다시 배치하지 않는다.

    Args:
        star_id: 수정할 Star의 path UUID.
        body: 변경할 title, content, galaxy_id가 담긴 항성 수정 요청 본문.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
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
    """
    인증된 사용자가 소유한 항성을 삭제한다.

    Args:
        star_id: 삭제할 Star의 path UUID.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
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
    """
    체류/편집 에너지를 기록하고, 유효하면 1-hop Nova 전파를 실행한다.

    Args:
        star_id: 이벤트를 기록할 Star의 path UUID.
        body: duration_seconds와 is_edit가 담긴 체류/편집 이벤트 요청 본문.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
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
    """
    공개 explore와 username/slug URL에 쓰는 소유자 전용 공개 토글.

    Args:
        star_id: 공개 여부를 변경할 Star의 path UUID.
        body: is_public 값이 담긴 공개 상태 변경 요청 본문.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = StarService(session)
    try:
        return await service.set_visibility(current_user.id, star_id, body.is_public)
    except StarError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
