from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """backend/.env 또는 프로세스 환경변수에서 읽어오는 런타임 설정."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    openai_api_key: str
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """FastAPI CORS 미들웨어는 리스트를 기대하지만 .env에는 CSV 문자열로 저장한다."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()  # type: ignore[call-arg]
