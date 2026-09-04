#!/bin/sh
# Backend container entrypoint.
#
# Runs alembic migrations, optionally seeds the database, then hands off to
# the CMD (uvicorn). Used for the local docker-compose environment. In
# Kubernetes, migrations should run as an initContainer or a Job instead of
# on every pod start — see k8s/README when we get there.

set -e

: "${RUN_MIGRATIONS:=1}"
: "${RUN_SEED:=1}"

if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "[entrypoint] running alembic upgrade head"
  alembic upgrade head
fi

if [ "$RUN_SEED" = "1" ]; then
  echo "[entrypoint] running seed"
  python -m app.seed
fi

echo "[entrypoint] handing off to: $*"
exec "$@"
