from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """회원가입 요청 본문. username은 URL에 안전한 계정 식별자다."""

    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Access token 응답. refresh token은 JSON이 아니라 쿠키로만 내려간다."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
