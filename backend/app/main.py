import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.api.routes.health import router as health_router
from app.api.routes.ready import router as ready_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.service_name)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("service starting (env=%s version=%s)", settings.app_env, settings.app_version)
    yield
    logger.info("service stopping")


app = FastAPI(
    title="Smart Education Portal API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def access_log(request: Request, call_next):
    start = time.perf_counter()
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "client": request.client.host if request.client else None,
            },
        )
        raise
    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "client": request.client.host if request.client else None,
        },
    )
    response.headers["x-request-id"] = request_id
    return response


app.include_router(health_router)
app.include_router(ready_router)
app.include_router(api_router)
