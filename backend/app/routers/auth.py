from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_token
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthError, AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    """
    계정을 만들고 access token과 httpOnly refresh token을 발급한다.

    Args:
        body: username, email, password가 담긴 회원가입 요청 본문.
        response: refresh token 쿠키를 설정할 FastAPI 응답 객체.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = AuthService(session)
    try:
        _, tokens, refresh = await _register_with_refresh(service, body)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    _set_refresh_cookie(response, refresh)
    return tokens


async def _register_with_refresh(
    service: AuthService, body: RegisterRequest
) -> tuple[UserResponse, TokenResponse, str]:
    """
    AuthService.register 응답에 라우터 전용 refresh token을 붙인다.

    Args:
        service: 회원가입 비즈니스 규칙을 실행할 인증 서비스.
        body: username, email, password가 담긴 회원가입 요청 본문.
    """
    user, tokens = await service.register(
        username=body.username, email=body.email, password=body.password
    )
    from app.core.security import create_refresh_token
    refresh = create_refresh_token(user.id)
    return user, tokens, refresh


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    """
    이메일/비밀번호를 검증하고 access token과 httpOnly refresh token을 발급한다.

    Args:
        body: email과 password가 담긴 로그인 요청 본문.
        response: refresh token 쿠키를 설정할 FastAPI 응답 객체.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    service = AuthService(session)
    try:
        _, tokens, refresh = await service.login(email=body.email, password=body.password)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    _set_refresh_cookie(response, refresh)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
) -> TokenResponse:
    """
    httpOnly refresh 쿠키를 새 access token으로 교환한다.

    Args:
        refresh_token: REFRESH_COOKIE 이름으로 전달된 httpOnly refresh token 쿠키 값.
        session: 요청 범위에서 공유하는 비동기 DB 세션.
    """
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        user_id = decode_token(refresh_token, token_type="refresh")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from e

    service = AuthService(session)
    try:
        return await service.refresh(user_id)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response) -> MessageResponse:
    """
    refresh token 쿠키를 삭제해 브라우저 세션을 로그아웃 상태로 만든다.

    Args:
        response: refresh token 쿠키 삭제 헤더를 실을 FastAPI 응답 객체.
    """
    response.delete_cookie(REFRESH_COOKIE)
    return MessageResponse(message="Logged out")


def _set_refresh_cookie(response: Response, token: str) -> None:
    """
    refresh token을 JavaScript 접근 밖에 저장한다. 운영 환경에서는 secure 쿠키를 쓴다.

    Args:
        response: 쿠키 설정 헤더를 실을 FastAPI 응답 객체.
        token: 클라이언트에 httpOnly 쿠키로 내려줄 refresh token 문자열.
    """
    from app.core.config import settings
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.app_env == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
    )
