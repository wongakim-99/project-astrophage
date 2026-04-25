import uuid
from enum import StrEnum

from pydantic import BaseModel, Field


class LifecycleState(StrEnum):
    """최근 에너지와 비활성 기간에서 계산되는 UI용 생애주기 라벨."""

    MAIN_SEQUENCE = "main_sequence"   # 활성: 최근 30일 에너지 3 이상
    YELLOW_DWARF = "yellow_dwarf"     # 보통: 최근 30일 에너지 1~2
    RED_GIANT = "red_giant"           # 희미해짐: 60~90일간 유효 조회 없음
    WHITE_DWARF = "white_dwarf"       # 잊힘: 90~180일간 유효 조회 없음
    DARK_MATTER = "dark_matter"       # 유실: 180일 이상 유효 조회 없음


class StarCreate(BaseModel):
    """생성 요청 본문. 임베딩과 좌표는 서버가 계산한다."""

    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[a-z0-9-]+$")
    content: str = Field(default="")
    galaxy_id: uuid.UUID


class StarUpdate(BaseModel):
    """수정 요청 본문. 생략된 필드는 기존 값을 유지한다."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
    galaxy_id: uuid.UUID | None = None


class StarResponse(BaseModel):
    """인증 응답용 항성 형태. 개인 소유권 메타데이터를 포함한다."""

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
    """비로그인 사용자에게 반환하는 형태. user_id는 노출하지 않는다."""
    id: uuid.UUID
    username: str
    galaxy_id: uuid.UUID
    title: str
    slug: str
    content: str
    lifecycle_state: LifecycleState

    model_config = {"from_attributes": True}


class SimilarStarPreview(BaseModel):
    """생성 모달에서 의미적으로 가까운 기존 항성을 보여주는 힌트."""

    id: uuid.UUID
    title: str
    similarity: float


class ViewEventCreate(BaseModel):
    """프론트엔드가 체류 시간을 측정한 뒤 제출하는 체류/편집 이벤트."""

    duration_seconds: int = Field(ge=0)
    is_edit: bool = False


class VisibilityUpdate(BaseModel):
    is_public: bool
