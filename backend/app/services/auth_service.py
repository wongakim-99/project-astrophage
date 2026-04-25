from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, UserResponse


class AuthError(Exception):
    """라우터가 HTTP 상태 코드로 변환할 인증 도메인 예외."""

    pass


class AuthService:
    """인증 비즈니스 규칙과 토큰 발급을 담당한다."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: 사용자 조회와 생성에 사용할 요청 범위 비동기 DB 세션.
        """
        self._repo = UserRepository(session)

    async def register(self, username: str, email: str, password: str) -> tuple[UserResponse, TokenResponse]:
        """
        username/email 중복을 검사하고 새 계정과 access token을 만든다.

        Args:
            username: 새 계정의 고유 username. 공개 URL 식별자로도 사용된다.
            email: 새 계정의 고유 이메일.
            password: 클라이언트가 보낸 평문 비밀번호. 저장 전 해시한다.
        """
        if await self._repo.get_by_email(email):
            raise AuthError("Email already registered")
        if await self._repo.get_by_username(username):
            raise AuthError("Username already taken")

        user = await self._repo.create(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )

        tokens = TokenResponse(
            access_token=create_access_token(str(user.id)),
        )
        user_response = UserResponse(id=str(user.id), username=user.username, email=user.email)
        return user_response, tokens

    async def login(self, email: str, password: str) -> tuple[UserResponse, TokenResponse, str]:
        """
        이메일/비밀번호를 검증하고 (user, access_token_response, refresh_token)을 반환한다.

        Args:
            email: 로그인할 사용자 이메일.
            password: 검증할 평문 비밀번호.
        """
        user = await self._repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Invalid email or password")

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        tokens = TokenResponse(access_token=access_token)
        user_response = UserResponse(id=str(user.id), username=user.username, email=user.email)
        return user_response, tokens, refresh_token

    async def refresh(self, user_id: str) -> TokenResponse:
        """
        refresh token subject로 받은 사용자 ID를 새 access token으로 교환한다.

        Args:
            user_id: refresh token에서 decode한 사용자 UUID 문자열.
        """
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise AuthError("User not found")
        return TokenResponse(access_token=create_access_token(str(user.id)))
