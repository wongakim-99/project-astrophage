import uuid
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.application.galaxy_dto import GalaxyDetails
from app.application.galaxy_use_cases import GalaxyUseCaseError
from app.core.dependencies import CurrentUser, GalaxyUseCaseDep
from app.schemas.common import MessageResponse
from app.schemas.galaxy import GalaxyCreate, GalaxyResponse, GalaxyUpdate

router = APIRouter(prefix="/galaxies", tags=["galaxies"])


@router.get("", response_model=list[GalaxyResponse])
async def list_galaxies(
    current_user: CurrentUser,
    use_cases: GalaxyUseCaseDep,
) -> list[GalaxyResponse]:
    """
    인증된 사용자의 은하만 반환한다.

    Args:
        current_user: Bearer access token에서 확인한 현재 사용자.
        use_cases: composition root가 조립한 은하 유스케이스.
    """
    galaxies = await use_cases.list_galaxies(current_user.id)
    return [_galaxy_response(g) for g in galaxies]


@router.post("", response_model=GalaxyResponse, status_code=status.HTTP_201_CREATED)
async def create_galaxy(
    body: GalaxyCreate,
    current_user: CurrentUser,
    use_cases: GalaxyUseCaseDep,
) -> GalaxyResponse:
    """
    사용자 범위 은하를 생성한다. 슬러그 충돌은 명시적 오류로 처리한다.

    Args:
        body: name, slug, 선택적 color가 담긴 은하 생성 요청 본문.
        current_user: Bearer access token에서 확인한 현재 사용자.
        use_cases: composition root가 조립한 은하 유스케이스.
    """
    try:
        galaxy = await use_cases.create_galaxy(
            user_id=current_user.id,
            name=body.name,
            slug=body.slug,
            color=body.color,
        )
    except GalaxyUseCaseError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return _galaxy_response(galaxy)


@router.patch("/{galaxy_id}", response_model=GalaxyResponse)
async def update_galaxy(
    galaxy_id: uuid.UUID,
    body: GalaxyUpdate,
    current_user: CurrentUser,
    use_cases: GalaxyUseCaseDep,
) -> GalaxyResponse:
    """
    인증된 사용자가 소유한 은하의 표시 이름과 색상을 수정한다.

    Args:
        galaxy_id: 수정할 Galaxy의 path UUID.
        body: 변경할 name과 color가 담긴 은하 수정 요청 본문. 생략된 필드는 유지한다.
        current_user: Bearer access token에서 확인한 현재 사용자.
        use_cases: composition root가 조립한 은하 유스케이스.
    """
    try:
        galaxy = await use_cases.update_galaxy(
            user_id=current_user.id,
            galaxy_id=galaxy_id,
            name=body.name,
            color=body.color,
        )
    except GalaxyUseCaseError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return _galaxy_response(galaxy)


@router.delete("/{galaxy_id}", response_model=MessageResponse)
async def delete_galaxy(
    galaxy_id: uuid.UUID,
    current_user: CurrentUser,
    use_cases: GalaxyUseCaseDep,
) -> MessageResponse:
    """
    인증된 사용자가 소유한 은하를 삭제한다.

    Args:
        galaxy_id: 삭제할 Galaxy의 path UUID.
        current_user: Bearer access token에서 확인한 현재 사용자.
        use_cases: composition root가 조립한 은하 유스케이스.
    """
    try:
        await use_cases.delete_galaxy(user_id=current_user.id, galaxy_id=galaxy_id)
    except GalaxyUseCaseError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return MessageResponse(message="Galaxy deleted")


def _galaxy_response(galaxy: GalaxyDetails) -> GalaxyResponse:
    return GalaxyResponse(**asdict(galaxy))
