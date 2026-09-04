# Kubernetes manifests

Manifests for deploying Smart Education Portal to GKE Standard (cluster
`prod-gke` in `me-central1`, project `smart-education-assignment`).

Nothing here is applied automatically. See Phase 13 for the full deploy
runbook.

## Files

| File | Purpose |
|---|---|
| `namespace.yaml` | Creates the `smart-education` namespace. |
| `configmap.yaml` | Non-secret env vars for the backend. |
| `secret.yaml` | Placeholder DB credentials. **Replace before applying.** Prefer Google Secret Manager + External Secrets in production. |
| `backend-serviceaccount.yaml` | KSA `app-service-account`. Workload Identity annotation is commented; uncomment and bind to a GSA to remove the need for key files. |
| `backend-deployment.yaml` | 3-replica FastAPI backend. Non-root, read-only rootfs, resource limits, liveness/readiness/startup probes, `RollingUpdate maxUnavailable: 0`. |
| `backend-service.yaml` | ClusterIP + `cloud.google.com/neg` annotation for container-native LB. |
| `frontend-deployment.yaml` | 2-replica nginx serving the built SPA. Non-root, resource limits, probes. |
| `frontend-service.yaml` | ClusterIP + NEG annotation. |
| `backend-hpa.yaml` | HPA 2–5 replicas, CPU target 70% (needs metrics-server). |
| `frontend-hpa.yaml` | HPA 2–4 replicas, CPU target 70%. |
| `ingress.yaml` | GKE Ingress: `/api`, `/health`, `/ready`, `/docs`, `/openapi.json` → backend; `/` → frontend. TLS blocks commented; enable Google-managed certificate for production. |
| `network-policy.yaml` | Default-deny plus explicit allows (frontend→backend, backend→DNS/DB). **Test before enforcing in prod.** |
| `migration-job.yaml` | One-shot Job that runs `alembic upgrade head` + seed. |

## Suggested apply order

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml            # after replacing placeholder values
kubectl apply -f k8s/backend-serviceaccount.yaml
kubectl apply -f k8s/migration-job.yaml
kubectl -n smart-education wait --for=condition=complete job/backend-migrate --timeout=180s
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/backend-hpa.yaml
kubectl apply -f k8s/frontend-hpa.yaml
kubectl apply -f k8s/ingress.yaml
# NetworkPolicy last, after verifying pods are healthy:
kubectl apply -f k8s/network-policy.yaml
```

## Database

The manifests assume an in-cluster Postgres named `postgres` at
`postgres:5432`. That deployment is not included here — for production,
prefer Cloud SQL Postgres reached over Private IP with Workload Identity
so no password ships in a Secret.

## Rollback

```bash
kubectl -n smart-education rollout undo deployment/backend
kubectl -n smart-education rollout status deployment/backend
```
