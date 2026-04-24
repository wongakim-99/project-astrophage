from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, explore, galaxies, stars

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
# explore routes are last — /{username}/stars/{slug} must not shadow fixed paths
app.include_router(explore.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
