import uuid
from dataclasses import dataclass
from datetime import datetime

from app.domain.star.lifecycle import LifecycleState


@dataclass(frozen=True)
class SimilarStar:
    id: uuid.UUID
    title: str
    similarity: float


@dataclass(frozen=True)
class StarDetails:
    id: uuid.UUID
    user_id: uuid.UUID
    galaxy_id: uuid.UUID
    title: str
    slug: str
    content: str
    pos_x: float
    pos_y: float
    is_public: bool
    lifecycle_state: LifecycleState
    energy_score: float
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class StarPublicDetails:
    id: uuid.UUID
    username: str
    galaxy_id: uuid.UUID
    title: str
    slug: str
    content: str
    lifecycle_state: LifecycleState
    created_at: datetime
    updated_at: datetime
