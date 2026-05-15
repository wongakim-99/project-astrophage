from dataclasses import dataclass


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
