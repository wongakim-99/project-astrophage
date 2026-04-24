import uuid
from enum import StrEnum

from pydantic import BaseModel, Field


class LifecycleState(StrEnum):
    MAIN_SEQUENCE = "main_sequence"   # Active: energy >= 3 in 30 days
    YELLOW_DWARF = "yellow_dwarf"     # Normal: energy 1-2 in 30 days
    RED_GIANT = "red_giant"           # Fading: 60-90 days no valid view
    WHITE_DWARF = "white_dwarf"       # Forgotten: 90-180 days no valid view
    DARK_MATTER = "dark_matter"       # Lost: 180+ days no valid view


class StarCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[a-z0-9-]+$")
    content: str = Field(default="")
    galaxy_id: uuid.UUID


class StarUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
    galaxy_id: uuid.UUID | None = None


class StarResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    galaxy_id: uuid.UUID
    title: str
    slug: str
    content: str
    pos_x: float
    pos_y: float
    is_public: bool
    lifecycle_state: LifecycleState = LifecycleState.YELLOW_DWARF
    energy_score: float = 0.0

    model_config = {"from_attributes": True}


class StarPublicResponse(BaseModel):
    """Returned to unauthenticated users — no user_id exposed."""
    id: uuid.UUID
    username: str
    galaxy_id: uuid.UUID
    title: str
    slug: str
    content: str
    lifecycle_state: LifecycleState

    model_config = {"from_attributes": True}


class SimilarStarPreview(BaseModel):
    id: uuid.UUID
    title: str
    similarity: float


class ViewEventCreate(BaseModel):
    duration_seconds: int = Field(ge=0)
    is_edit: bool = False


class VisibilityUpdate(BaseModel):
    is_public: bool
