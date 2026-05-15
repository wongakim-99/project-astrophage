import uuid

from pydantic import BaseModel, Field


class GalaxyCreate(BaseModel):
    """클라이언트가 보내는 은하 데이터. color가 없으면 팔레트에서 자동 배정한다."""

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class GalaxyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class GalaxyResponse(BaseModel):
    """인증된 개인 우주 UI에서 사용하는 은하 응답 형태."""

    id: uuid.UUID
    name: str
    slug: str
    color: str
    star_count: int = 0

    model_config = {"from_attributes": True}
