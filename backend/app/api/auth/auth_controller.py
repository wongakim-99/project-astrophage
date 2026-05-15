from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.api.auth.application.dto import AccessToken, UserProfile
from app.api.auth.application.use_cases import AuthUseCaseError
from app.api.auth.dto.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserSettingsUpdate,
)
from app.common.dependencies import AuthUseCaseDep, CurrentUser
from app.common.dto.common import MessageResponse
from app.common.security.tokens import decode_token

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    response: Response,
    use_cases: AuthUseCaseDep,
) -> TokenResponse:
    """
    계정을 만들고 access token과 httpOnly refresh token을 발급한다.

    Args:
        body: username, email, password가 담긴 회원가입 요청 본문.
        response: refresh token 쿠키를 설정할 FastAPI 응답 객체.
        use_cases: composition root가 조립한 인증 유스케이스.
    """
    try:
        token_pair = await use_cases.register(
            username=body.username,
            email=body.email,
            password=body.password,
        )
    except AuthUseCaseError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    _set_refresh_cookie(response, token_pair.refresh_token)
    return _token_response(AccessToken(access_token=token_pair.access_token))


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    use_cases: AuthUseCaseDep,
) -> TokenResponse:
    """
    이메일/비밀번호를 검증하고 access token과 httpOnly refresh token을 발급한다.

    Args:
        body: email과 password가 담긴 로그인 요청 본문.
        response: refresh token 쿠키를 설정할 FastAPI 응답 객체.
        use_cases: composition root가 조립한 인증 유스케이스.
    """
    try:
        token_pair = await use_cases.login(email=body.email, password=body.password)
    except AuthUseCaseError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    _set_refresh_cookie(response, token_pair.refresh_token)
    return _token_response(AccessToken(access_token=token_pair.access_token))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    use_cases: AuthUseCaseDep,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
) -> TokenResponse:
    """
    httpOnly refresh 쿠키를 새 access token으로 교환한다.

    Args:
        refresh_token: REFRESH_COOKIE 이름으로 전달된 httpOnly refresh token 쿠키 값.
        use_cases: composition root가 조립한 인증 유스케이스.
    """
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        user_id = decode_token(refresh_token, token_type="refresh")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from e

    try:
        return _token_response(await use_cases.refresh(user_id))
    except AuthUseCaseError as e:
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


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """현재 로그인한 사용자의 공개 설정을 포함한 프로필을 반환한다."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        is_universe_public=current_user.is_universe_public,
    )


@router.patch("/me/settings", response_model=UserResponse)
async def update_me_settings(
    body: UserSettingsUpdate,
    current_user: CurrentUser,
    use_cases: AuthUseCaseDep,
) -> UserResponse:
    """우주 탐색 노출 여부를 사용자 단위로 저장한다. 공개로 전환 시 기존 항성 전부 공개."""
    return _user_response(await use_cases.update_universe_visibility(
        user_id=current_user.id,
        is_universe_public=body.is_universe_public,
    ))


def _token_response(token: AccessToken) -> TokenResponse:
    return TokenResponse(access_token=token.access_token)


def _user_response(user: UserProfile) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_universe_public=user.is_universe_public,
    )


def _set_refresh_cookie(response: Response, token: str) -> None:
    """
    refresh token을 JavaScript 접근 밖에 저장한다. 운영 환경에서는 secure 쿠키를 쓴다.

    Args:
        response: 쿠키 설정 헤더를 실을 FastAPI 응답 객체.
        token: 클라이언트에 httpOnly 쿠키로 내려줄 refresh token 문자열.
    """
    from app.common.config import settings
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.app_env == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
    )
