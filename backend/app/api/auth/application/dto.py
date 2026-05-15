from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    username: str
    email: str
    is_universe_public: bool


@dataclass(frozen=True)
class AccessToken:
    access_token: str


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class UserProfile:
    id: str
    username: str
    email: str
    is_universe_public: bool
