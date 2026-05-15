from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.ports.star_repository import StarRepositoryPort
from app.ports.user_repository import UserRepositoryPort
from app.schemas.auth import TokenResponse, UserResponse


class AuthUseCaseError(Exception):
    """라우터가 HTTP 상태 코드로 변환할 인증 유스케이스 예외."""

    pass


class AuthUseCases:
    """인증과 사용자 설정 변경 유스케이스의 흐름을 조율한다."""

    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepositoryPort,
        star_repo: StarRepositoryPort,
    ) -> None:
        """
        Args:
            session: 사용자와 항성 공개 상태 변경에 사용할 요청 범위 비동기 DB 세션.
        """
        self._session = session
        self._user_repo = user_repo
        self._star_repo = star_repo

    async def register(self, username: str, email: str, password: str) -> tuple[TokenResponse, str]:
        """
        username/email 중복을 검사하고 access token과 refresh token을 발급한다.

        Args:
            username: 새 계정의 고유 username. 공개 URL 식별자로도 사용된다.
            email: 새 계정의 고유 이메일.
            password: 클라이언트가 보낸 평문 비밀번호. 저장 전 해시한다.
        """
        if await self._user_repo.get_by_email(email):
            raise AuthUseCaseError("Email already registered")
        if await self._user_repo.get_by_username(username):
            raise AuthUseCaseError("Username already taken")

        user = await self._user_repo.create(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )

        tokens = TokenResponse(access_token=create_access_token(str(user.id)))
        refresh_token = create_refresh_token(str(user.id))
        return tokens, refresh_token

    async def login(self, email: str, password: str) -> tuple[TokenResponse, str]:
        """
        이메일/비밀번호를 검증하고 access token과 refresh token을 반환한다.

        Args:
            email: 로그인할 사용자 이메일.
            password: 검증할 평문 비밀번호.
        """
        user = await self._user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthUseCaseError("Invalid email or password")

        return (
            TokenResponse(access_token=create_access_token(str(user.id))),
            create_refresh_token(str(user.id)),
        )

    async def refresh(self, user_id: str) -> TokenResponse:
        """
        refresh token subject로 받은 사용자 ID를 새 access token으로 교환한다.

        Args:
            user_id: refresh token에서 decode한 사용자 UUID 문자열.
        """
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise AuthUseCaseError("User not found")
        return TokenResponse(access_token=create_access_token(str(user.id)))

    async def update_universe_visibility(
        self, current_user: User, is_universe_public: bool
    ) -> UserResponse:
        """
        우주 탐색 노출 여부를 저장한다. 공개 전환 시 기존 항성을 모두 공개한다.

        Args:
            current_user: 인증 의존성이 반환한 현재 사용자 ORM 인스턴스.
            is_universe_public: 변경할 공개 우주 설정값.
        """
        current_user.is_universe_public = is_universe_public
        if is_universe_public:
            await self._star_repo.set_all_public_for_user(current_user.id, is_public=True)
        await self._session.commit()
        await self._session.refresh(current_user)
        return UserResponse(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            is_universe_public=current_user.is_universe_public,
        )
