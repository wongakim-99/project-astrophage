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
    """계정을 만들고 access token과 httpOnly refresh token을 발급한다."""
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
    # AuthService.register는 공개 응답 형태만 반환한다.
    # HTTP 경계인 라우터에서 쿠키 전용 refresh token을 만든다.
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
    """httpOnly refresh 쿠키를 새 access token으로 교환한다."""
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
    response.delete_cookie(REFRESH_COOKIE)
    return MessageResponse(message="Logged out")


def _set_refresh_cookie(response: Response, token: str) -> None:
    """refresh token을 JavaScript 접근 밖에 저장한다. 운영 환경에서는 secure 쿠키를 쓴다."""
    from app.core.config import settings
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.app_env == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
    )
