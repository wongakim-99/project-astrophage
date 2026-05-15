from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query, status

from app.application.star_dto import StarPublicDetails
from app.application.star_use_cases import StarUseCaseError
from app.core.dependencies import StarUseCaseDep
from app.schemas.star import StarPublicResponse

router = APIRouter(tags=["explore"])


@router.get("/explore", response_model=list[StarPublicResponse])
async def list_public_stars(
    use_cases: StarUseCaseDep,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[StarPublicResponse]:
    """
    공개 카드 피드. is_public=true인 항성만 여기에 노출된다.
    star+username은 JOIN 1회, 생애주기 이벤트는 배치 2회로 총 쿼리 3회.

    Args:
        use_cases: composition root가 조립한 항성 유스케이스.
        limit: 한 번에 반환할 공개 항성 최대 개수. 1~100 사이만 허용한다.
        offset: 페이지네이션을 위해 앞에서 건너뛸 공개 항성 개수.
    """
    stars = await use_cases.list_public_stars(limit=limit, offset=offset)
    return [_public_star_response(star) for star in stars]


@router.get("/{username}/stars/{slug}", response_model=StarPublicResponse)
async def get_public_star(
    username: str,
    slug: str,
    use_cases: StarUseCaseDep,
) -> StarPublicResponse:
    """
    공개 username/slug 페이지. 비공개 또는 없는 항성은 의도적으로 403을 반환한다.

    Args:
        username: 공개 URL에서 받은 항성 소유자의 username.
        slug: 공개 URL에서 받은 사용자 범위의 항성 slug.
        use_cases: composition root가 조립한 항성 유스케이스.
    """
    try:
        return _public_star_response(await use_cases.get_public_star(username, slug))
    except StarUseCaseError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


def _public_star_response(star: StarPublicDetails) -> StarPublicResponse:
    return StarPublicResponse(**asdict(star))
