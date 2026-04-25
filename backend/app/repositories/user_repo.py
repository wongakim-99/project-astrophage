import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """사용자 DB 접근 전용 클래스. 비즈니스 규칙은 AuthService에 둔다."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: 현재 요청 또는 작업에서 공유하는 비동기 DB 세션.
        """
        self._session = session

    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None:
        """
        Args:
            user_id: 조회할 User의 기본키 UUID. 토큰 subject에서 온 문자열 UUID도 허용한다.
        """
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Args:
            email: 회원가입 중복 확인과 로그인에 사용하는 사용자 이메일.
        """
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Args:
            username: 공개 URL 소유자 식별과 회원가입 중복 확인에 사용하는 username.
        """
        result = await self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, username: str, email: str, password_hash: str) -> User:
        """
        Args:
            username: 새 계정의 고유 username.
            email: 새 계정의 고유 이메일.
            password_hash: 평문 비밀번호가 아니라 보안 계층에서 해시한 비밀번호 문자열.
        """
        user = User(username=username, email=email, password_hash=password_hash)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user
