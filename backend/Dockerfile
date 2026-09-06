# syntax=docker/dockerfile:1.7

# ---------- Base ----------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_ENV=production \
    APP_VERSION=1.0.0

WORKDIR /app

# Minimal system deps. Postgres client libs come via psycopg[binary], so no
# libpq-dev needed. curl is included for optional in-container debugging.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

# ---------- Deps layer ----------
FROM base AS deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# ---------- Final ----------
FROM base AS runtime

# Bring in installed site-packages + console scripts from deps stage.
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Strip build tooling from the runtime image. Nothing here imports pip,
# setuptools, or wheel at runtime (uvicorn/alembic are plain console
# scripts) — and each vendors its own copy of other libraries internally
# (e.g. pip/_vendor/msgpack, setuptools/_vendor/wheel) that trail the CVE
# fixes in the real top-level packages, so shipping them is pure downside.
# `pip uninstall` in the deps stage doesn't work here: the base image
# (python:3.12-slim) already bundles its own pip/setuptools/wheel via
# ensurepip, and COPY merges into that existing directory rather than
# replacing it — an uninstall upstream leaves the base image's own copies
# to reappear right back in this stage. Deleting the known paths
# explicitly, after the copy, is what actually removes them.
RUN rm -rf \
      /usr/local/lib/python3.12/site-packages/pip \
      /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
      /usr/local/lib/python3.12/site-packages/setuptools \
      /usr/local/lib/python3.12/site-packages/setuptools-*.dist-info \
      /usr/local/lib/python3.12/site-packages/wheel \
      /usr/local/lib/python3.12/site-packages/wheel-*.dist-info \
      /usr/local/lib/python3.12/site-packages/_distutils_hack \
      /usr/local/lib/python3.12/site-packages/distutils-precedence.pth \
      /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.12 /usr/local/bin/wheel

# Create an unprivileged user.
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --home /app --shell /usr/sbin/nologin app

# Application source.
COPY --chown=app:app app /app/app
COPY --chown=app:app alembic /app/alembic
COPY --chown=app:app alembic.ini /app/alembic.ini
COPY --chown=app:app docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

USER app

EXPOSE 8000

# tini gives us proper PID 1 + signal forwarding for graceful shutdown.
# The entrypoint script optionally runs migrations + seed before exec'ing CMD.
# In Kubernetes we skip the entrypoint (set command:) and run migrations as a
# separate Job instead.
ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]

# Uvicorn honours SIGTERM: the running requests get to finish, then it exits.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips=*"]
