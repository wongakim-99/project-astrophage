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
    service = GalaxyService(session)
    galaxies = await service.list_galaxies(current_user.id)
    return [GalaxyResponse(**g) for g in galaxies]


@router.post("", response_model=GalaxyResponse, status_code=status.HTTP_201_CREATED)
async def create_galaxy(
    body: GalaxyCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GalaxyResponse:
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
    service = GalaxyService(session)
    try:
        await service.delete_galaxy(user_id=current_user.id, galaxy_id=galaxy_id)
    except GalaxyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return MessageResponse(message="Galaxy deleted")
