import uuid

from pydantic import BaseModel, Field


class GalaxyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class GalaxyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class GalaxyResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    color: str
    star_count: int = 0

    model_config = {"from_attributes": True}
