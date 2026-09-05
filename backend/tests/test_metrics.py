"""Tests for the Prometheus /metrics endpoint.

These tests exercise the endpoint and the middleware's counter/histogram/gauge
wiring end-to-end via the FastAPI TestClient. They do not require a database.
"""
from fastapi.testclient import TestClient


METRIC_NAMES = (
    "smart_education_http_requests_total",
    "smart_education_http_request_duration_seconds",
    "smart_education_http_requests_in_progress",
)


def _scrape(client: TestClient) -> str:
    resp = client.get("/metrics")
    assert resp.status_code == 200, resp.text
    # prometheus_client's ASGI app advertises the standard exposition format.
    ctype = resp.headers.get("content-type", "")
    assert "text/plain" in ctype, ctype
    return resp.text


def test_metrics_endpoint_returns_prometheus_exposition(client: TestClient) -> None:
    body = _scrape(client)
    for name in METRIC_NAMES:
        assert name in body, f"expected {name} in /metrics output"


def test_metrics_exposes_http_help_lines(client: TestClient) -> None:
    body = _scrape(client)
    # Prometheus exposition format prefixes each metric family with '# HELP'
    # and '# TYPE' lines. Verify our three custom families are present.
    for name in METRIC_NAMES:
        assert f"# HELP {name}" in body
        assert f"# TYPE {name}" in body


def test_request_counter_increments_on_normal_request(client: TestClient) -> None:
    # Baseline scrape (this scrape itself must NOT increment because /metrics
    # is on the exclusion list).
    before = _scrape(client)

    # A normal application request.
    resp = client.get("/health")
    assert resp.status_code == 200

    after = _scrape(client)

    # Locate the counter series for GET /health status=200 in both scrapes.
    needle = 'smart_education_http_requests_total{method="GET",path="/health",status="200"}'

    def _extract(body: str) -> float:
        for line in body.splitlines():
            if line.startswith(needle):
                # Format: '<labels> <value>' — take the trailing number.
                return float(line.rsplit(" ", 1)[-1])
        return 0.0

    assert _extract(after) >= _extract(before) + 1.0, (
        f"expected counter to increment; before={_extract(before)} "
        f"after={_extract(after)}"
    )


def test_scraping_metrics_does_not_pollute_counter(client: TestClient) -> None:
    # Multiple /metrics scrapes must not create a metric series for path="/metrics".
    for _ in range(3):
        client.get("/metrics")
    body = _scrape(client)
    for line in body.splitlines():
        if line.startswith("smart_education_http_requests_total{"):
            assert 'path="/metrics"' not in line, (
                "the /metrics endpoint must be excluded from the request counter"
            )


def test_health_endpoint_still_works(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_ready_endpoint_still_responds(client: TestClient) -> None:
    # Without a real DB, /ready returns 503; the point of this test is that
    # the route still exists and the metrics middleware does not break it.
    resp = client.get("/ready")
    assert resp.status_code in (200, 503)
