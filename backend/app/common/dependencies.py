from typing import Annotated, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.application.dto import AuthenticatedUser
from app.api.auth.application.ports.user_repository import UserRepositoryPort
from app.api.auth.application.use_cases import AuthUseCases
from app.api.auth.infrastructure.user_repository import UserRepository
from app.api.galaxy.application.ports.galaxy_repository import GalaxyRepositoryPort
from app.api.galaxy.application.use_cases import GalaxyUseCases
from app.api.galaxy.infrastructure.galaxy_repository import GalaxyRepository
from app.api.star.application.ports.star_repository import StarRepositoryPort
from app.api.star.application.ports.view_event_repository import ViewEventRepositoryPort
from app.api.star.application.use_cases import StarUseCases
from app.api.star.infrastructure.openai_embedding_provider import OpenAIEmbeddingProvider
from app.api.star.infrastructure.star_repository import StarRepository
from app.api.star.infrastructure.view_event_repository import ViewEventRepository
from app.common.infrastructure.persistence.database import get_session as get_session
from app.common.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from app.common.security.tokens import decode_token

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
        user_repo=cast(UserRepositoryPort, UserRepository(session)),
        star_repo=cast(StarRepositoryPort, StarRepository(session)),
    )


def get_galaxy_use_cases(session: Annotated[AsyncSession, Depends(get_session)]) -> GalaxyUseCases:
    """은하 유스케이스에 필요한 persistence adapter를 조립한다."""
    return GalaxyUseCases(
        unit_of_work=SqlAlchemyUnitOfWork(session),
        galaxy_repo=cast(GalaxyRepositoryPort, GalaxyRepository(session)),
    )


def get_star_use_cases(session: Annotated[AsyncSession, Depends(get_session)]) -> StarUseCases:
    """항성 유스케이스에 필요한 persistence/external adapter를 조립한다."""
    return StarUseCases(
        unit_of_work=SqlAlchemyUnitOfWork(session),
        star_repo=cast(StarRepositoryPort, StarRepository(session)),
        galaxy_repo=cast(GalaxyRepositoryPort, GalaxyRepository(session)),
        user_repo=cast(UserRepositoryPort, UserRepository(session)),
        view_event_repo=cast(ViewEventRepositoryPort, ViewEventRepository(session)),
        embedding_provider=OpenAIEmbeddingProvider(),
    )


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
AuthUseCaseDep = Annotated[AuthUseCases, Depends(get_auth_use_cases)]
GalaxyUseCaseDep = Annotated[GalaxyUseCases, Depends(get_galaxy_use_cases)]
StarUseCaseDep = Annotated[StarUseCases, Depends(get_star_use_cases)]
