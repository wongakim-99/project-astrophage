import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.database import request_query_log
from app.routers import auth, explore, galaxies, stars

logger = logging.getLogger("uvicorn.error")

_CYAN = "\033[96m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_DIM = "\033[2m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


_NextCall = Callable[[Request], Awaitable[Response]]


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: _NextCall) -> Response:
        method = request.method
        path = request.url.path
        start = time.perf_counter()

        token = request_query_log.set([])
        try:
            response = await call_next(request)
        finally:
            queries = request_query_log.get([]) or []
            request_query_log.reset(token)

        total_ms = (time.perf_counter() - start) * 1000
        status: int = response.status_code
        status_color = _GREEN if status < 400 else (_YELLOW if status < 500 else _RED)

        lines: list[str] = []
        lines.append(f"{_DIM}{'─' * 72}{_RESET}")
        lines.append(f"{_CYAN}{_BOLD}▶  {method} {path}{_RESET}")
        for i, (sql, ms) in enumerate(queries):
            connector = "└" if i == len(queries) - 1 else "│"
            ms_color = _GREEN if ms < 200 else (_YELLOW if ms < 600 else _RED)
            label = "TX  " if sql == "COMMIT" else "DB  "
            lines.append(
                f"   {_DIM}{connector}{_RESET}  {label}"
                f"{ms_color}{ms:5.0f}ms{_RESET}  {_DIM}{sql}{_RESET}"
            )
        lines.append(
            f"{status_color}{_BOLD}◀  {status}{_RESET}"
            f"  {_BOLD}{total_ms:.0f}ms total{_RESET}"
        )
        logger.info("\n" + "\n".join(lines))

        return response


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

if settings.app_env == "development":
    app.add_middleware(TimingMiddleware)

app.include_router(auth.router)
app.include_router(galaxies.router)
app.include_router(stars.router)
# /{username}/stars/{slug}가 고정 경로를 가리지 않도록 explore 라우터는 마지막에 등록한다.
app.include_router(explore.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
