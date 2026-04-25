import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies import CurrentUser
from app.schemas.common import MessageResponse
from app.schemas.galaxy import GalaxyCreate, GalaxyResponse, GalaxyUpdate
from app.services.galaxy_service import GalaxyError, GalaxyService

router = APIRouter(prefix="/galaxies", tags=["galaxies"])


@router.get("", response_model=list[GalaxyResponse])
async def list_galaxies(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[GalaxyResponse]:
    """
    인증된 사용자의 은하만 반환한다.

    Args:
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = GalaxyService(session)
    galaxies = await service.list_galaxies(current_user.id)
    return [GalaxyResponse(**g) for g in galaxies]


@router.post("", response_model=GalaxyResponse, status_code=status.HTTP_201_CREATED)
async def create_galaxy(
    body: GalaxyCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GalaxyResponse:
    """
    사용자 범위 은하를 생성한다. 슬러그 충돌은 명시적 오류로 처리한다.

    Args:
        body: name, slug, 선택적 color가 담긴 은하 생성 요청 본문.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = GalaxyService(session)
    try:
        galaxy = await service.create_galaxy(
            user_id=current_user.id,
            name=body.name,
            slug=body.slug,
            color=body.color,
        )
    except GalaxyError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return GalaxyResponse(id=galaxy.id, name=galaxy.name, slug=galaxy.slug, color=galaxy.color)


@router.patch("/{galaxy_id}", response_model=GalaxyResponse)
async def update_galaxy(
    galaxy_id: uuid.UUID,
    body: GalaxyUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GalaxyResponse:
    """
    인증된 사용자가 소유한 은하의 표시 이름과 색상을 수정한다.

    Args:
        galaxy_id: 수정할 Galaxy의 path UUID.
        body: 변경할 name과 color가 담긴 은하 수정 요청 본문. 생략된 필드는 유지한다.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = GalaxyService(session)
    try:
        galaxy = await service.update_galaxy(
            user_id=current_user.id,
            galaxy_id=galaxy_id,
            name=body.name,
            color=body.color,
        )
    except GalaxyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return GalaxyResponse(id=galaxy.id, name=galaxy.name, slug=galaxy.slug, color=galaxy.color)


@router.delete("/{galaxy_id}", response_model=MessageResponse)
async def delete_galaxy(
    galaxy_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageResponse:
    """
    인증된 사용자가 소유한 은하를 삭제한다.

    Args:
        galaxy_id: 삭제할 Galaxy의 path UUID.
        current_user: Bearer access token에서 확인한 현재 사용자.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = GalaxyService(session)
    try:
        await service.delete_galaxy(user_id=current_user.id, galaxy_id=galaxy_id)
    except GalaxyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return MessageResponse(message="Galaxy deleted")
