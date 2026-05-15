import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class GalaxyDetails:
    id: uuid.UUID
    name: str
    slug: str
    color: str
    star_count: int = 0
