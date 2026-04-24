from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, explore, galaxies, stars

# FastAPI 앱 진입점. 도메인 로직은 서비스 클래스에 두고, 여기서는
# 전역 미들웨어와 라우터 등록만 담당한다.
app = FastAPI(
    title="Project Astrophage API",
    version="0.1.0",
    docs_url="/docs" if settings.app_env != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(galaxies.router)
app.include_router(stars.router)
# /{username}/stars/{slug}가 고정 경로를 가리지 않도록 explore 라우터는 마지막에 등록한다.
app.include_router(explore.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
