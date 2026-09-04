# Smart Education Portal

A production-oriented educational web application built to demonstrate a
Google Kubernetes Engine (GKE) Standard architecture end to end:
React frontend, FastAPI backend, PostgreSQL, Docker, Kubernetes,
Artifact Registry, HPA, Ingress, and CI.

> **Status:** Phase 1 complete — project skeleton only.
> Implementation will be added phase by phase.

## Planned architecture

```
Internet
   |
   v
Google Cloud Load Balancer
   |
   v
Kubernetes Ingress  ---- /api ----> Backend Service --> FastAPI pods --> PostgreSQL
   |
    ---- / --------> Frontend Service --> React (nginx) pods
```

## Repository layout

See the top-level directories:

- `frontend/` — React + TypeScript + Vite SPA (served by nginx in prod).
- `backend/`  — FastAPI + SQLAlchemy + Alembic REST API.
- `database/init/` — Optional SQL bootstrap scripts for local Postgres.
- `k8s/` — Kubernetes manifests for GKE Standard.
- `.github/workflows/` — CI pipeline (build + test, no auto-deploy).
- `docker-compose.yml` — Full local dev stack (frontend + backend + postgres).

## Phases

1. Project structure (this phase)
2. FastAPI backend
3. PostgreSQL integration
4. Seed data
5. React frontend
6. Frontend ↔ Backend integration
7. Dockerfiles
8. Docker Compose
9. Local end-to-end run
10. Kubernetes manifests
11. Manifest validation
12. Artifact Registry image naming
13. GKE deployment documentation

Detailed instructions for local dev, migrations, testing, Docker builds,
and GKE deployment will be filled in as later phases are completed.
