from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.openai_embedding_provider import OpenAIEmbeddingProvider
from app.adapters.persistence.galaxy_repository import GalaxyRepository
from app.adapters.persistence.star_repository import StarRepository
from app.adapters.persistence.unit_of_work import SqlAlchemyUnitOfWork
from app.adapters.persistence.user_repository import UserRepository
from app.adapters.persistence.view_event_repository import ViewEventRepository
from app.application.auth_dto import AuthenticatedUser
from app.application.auth_use_cases import AuthUseCases
from app.application.galaxy_use_cases import GalaxyUseCases
from app.application.star_use_cases import StarUseCases
from app.core.database import get_session as get_session
from app.core.security import decode_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthenticatedUser:
    """Bearer access token을 인증된 사용자 행으로 해석한다."""
    token = credentials.credentials
    try:
        user_id = decode_token(token, token_type="access")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return AuthenticatedUser(
        id=user.id,
        username=user.username,
        email=user.email,
        is_universe_public=user.is_universe_public,
    )


def get_auth_use_cases(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthUseCases:
    """인증 유스케이스에 필요한 persistence adapter를 조립한다."""
    return AuthUseCases(
        unit_of_work=SqlAlchemyUnitOfWork(session),
        user_repo=UserRepository(session),
        star_repo=StarRepository(session),
    )


def get_galaxy_use_cases(session: Annotated[AsyncSession, Depends(get_session)]) -> GalaxyUseCases:
    """은하 유스케이스에 필요한 persistence adapter를 조립한다."""
    return GalaxyUseCases(
        unit_of_work=SqlAlchemyUnitOfWork(session),
        galaxy_repo=GalaxyRepository(session),
    )


def get_star_use_cases(session: Annotated[AsyncSession, Depends(get_session)]) -> StarUseCases:
    """항성 유스케이스에 필요한 persistence/external adapter를 조립한다."""
    return StarUseCases(
        unit_of_work=SqlAlchemyUnitOfWork(session),
        star_repo=StarRepository(session),
        galaxy_repo=GalaxyRepository(session),
        user_repo=UserRepository(session),
        view_event_repo=ViewEventRepository(session),
        embedding_provider=OpenAIEmbeddingProvider(),
    )


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
AuthUseCaseDep = Annotated[AuthUseCases, Depends(get_auth_use_cases)]
GalaxyUseCaseDep = Annotated[GalaxyUseCases, Depends(get_galaxy_use_cases)]
StarUseCaseDep = Annotated[StarUseCases, Depends(get_star_use_cases)]
