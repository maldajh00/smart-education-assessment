import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

from app.api.routes import api_router
from app.api.routes.health import router as health_router
from app.api.routes.ready import router as ready_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.service_name)
logger = logging.getLogger(__name__)


# Prometheus metrics.
#
# Labels are intentionally low-cardinality:
#   - method: bounded to the small set of HTTP verbs actually used.
#   - path:   the matched FastAPI *route template* (e.g. "/api/courses/{id}"),
#             NOT the raw request URL, so IDs and query strings do not
#             explode the cardinality.
#   - status: string form of the HTTP status code.
#
# High-cardinality labels (request id, client IP, user id, query params)
# are deliberately excluded.
REQUEST_COUNT = Counter(
    "smart_education_http_requests_total",
    "Total HTTP requests processed, labeled by method, route template, and status.",
    ["method", "path", "status"],
)
REQUEST_DURATION = Histogram(
    "smart_education_http_request_duration_seconds",
    "HTTP request duration in seconds, labeled by method and route template.",
    ["method", "path"],
)
REQUESTS_IN_PROGRESS = Gauge(
    "smart_education_http_requests_in_progress",
    "In-flight HTTP requests currently being processed.",
)

# Paths that must NOT contribute to the request metrics themselves,
# otherwise every Prometheus scrape would increment the counters.
_METRICS_EXCLUDED_PATHS = {"/metrics"}


def _route_template(request: Request, fallback: str) -> str:
    """Return the matched FastAPI route template, or a safe fallback.

    Using the template (e.g. "/api/courses/{id}") instead of the raw
    request path keeps the `path` label cardinality bounded.
    Unmatched paths (404s on unknown URLs) collapse to "unmatched" so
    scanners cannot inflate the label set.
    """
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    if template:
        return template
    if fallback in _METRICS_EXCLUDED_PATHS:
        return fallback
    return "unmatched"


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
    raw_path = request.url.path
    record_metrics = raw_path not in _METRICS_EXCLUDED_PATHS

    if record_metrics:
        REQUESTS_IN_PROGRESS.inc()

    status_code = 500
    try:
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration = time.perf_counter() - start
            logger.exception(
                "request failed",
                extra={
                    "method": request.method,
                    "path": raw_path,
                    "duration_ms": int(duration * 1000),
                    "client": request.client.host if request.client else None,
                },
            )
            if record_metrics:
                template = _route_template(request, raw_path)
                REQUEST_COUNT.labels(
                    method=request.method, path=template, status="500"
                ).inc()
                REQUEST_DURATION.labels(
                    method=request.method, path=template
                ).observe(duration)
            raise
    finally:
        if record_metrics:
            REQUESTS_IN_PROGRESS.dec()

    duration = time.perf_counter() - start
    template = _route_template(request, raw_path)

    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": raw_path,
            "status_code": status_code,
            "duration_ms": int(duration * 1000),
            "client": request.client.host if request.client else None,
        },
    )
    response.headers["x-request-id"] = request_id

    if record_metrics:
        REQUEST_COUNT.labels(
            method=request.method, path=template, status=str(status_code)
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method, path=template
        ).observe(duration)

    return response


app.include_router(health_router)
app.include_router(ready_router)
app.include_router(api_router)

# Prometheus scrape endpoint. Same port as the app so GKE Managed Service
# for Prometheus scrapes it via the pod's existing named "http" port under
# the cluster NetworkPolicy — /metrics is NOT exposed through the public
# Ingress.
app.mount("/metrics", make_asgi_app())
