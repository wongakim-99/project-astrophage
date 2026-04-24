from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """평문 비밀번호를 저장하기 전에 bcrypt로 해시한다."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """로그인 비밀번호가 저장된 bcrypt 해시와 일치하는지 확인한다."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str) -> str:
    """Authorization 헤더에 넣는 단기 bearer token을 생성한다."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "access"},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def create_refresh_token(subject: str) -> str:
    """httpOnly 쿠키에만 저장할 장기 refresh token을 생성한다."""
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "refresh"},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_token(token: str, token_type: str = "access") -> str:
    """JWT를 해석해 subject(user_id)를 반환한다. 실패하면 ValueError를 던진다."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise ValueError("Invalid token type")
        sub: str | None = payload.get("sub")
        if sub is None:
            raise ValueError("Missing subject")
        return sub
    except JWTError as e:
        raise ValueError("Invalid token") from e
