# GitHub → GCP setup guide

End-to-end steps to go from a fresh GitHub repo to images in Artifact
Registry and (optionally) a deployed workload in GKE — with **no service
account JSON key files** anywhere.

All commands here are for **you to run** — I never touch your GCP
environment automatically.

Contents:

1. [What I need from you](#0-what-i-need-from-you)
2. [Push the code to GitHub](#1-push-the-code-to-github)
3. [Configure Workload Identity Federation](#2-configure-workload-identity-federation-in-gcp)
4. [Add secrets to the GitHub repo](#3-add-secrets-to-the-github-repo)
5. [Trigger the workflows](#4-trigger-the-workflows)
6. [(Later) Deploy to GKE](#5-later-deploy-to-gke)

---

## 0. What I need from you

Please gather:

- [ ] Your **GitHub username** (or org name) and the **repo name** you want, e.g. `mohannad34/smart-education-portal`.
- [ ] Your **GCP project number** (not the ID). Get it with:
  ```bash
  gcloud projects describe smart-education-assignment --format='value(projectNumber)'
  ```
- [ ] Confirmation you have **Owner** or a mix of (`iam.workloadIdentityPoolAdmin`, `iam.serviceAccountAdmin`, `resourcemanager.projectIamAdmin`, `artifactregistry.admin`) on `smart-education-assignment`.
- [ ] Docker Desktop running (already there).
- [ ] `gcloud` CLI installed and `gcloud auth login` completed. Check:
  ```bash
  gcloud config get-value project    # should print: smart-education-assignment
  ```
- [ ] `git` installed. Check: `git --version`.

---

## 1. Push the code to GitHub

Run these once from `D:\Smart Education\Project\smart-education-portal`:

```bash
git init -b main
git add .
git commit -m "initial: FastAPI + React + PostgreSQL + K8s manifests"

# Create the empty repo on GitHub first (Web UI or `gh repo create`).
git remote add origin git@github.com:<YOUR_GITHUB_USER>/smart-education-portal.git
git push -u origin main
```

The **CI workflow** (`.github/workflows/ci.yaml`) will run automatically on
this first push: backend tests, frontend build, Docker builds — no push
yet. Watch it under the *Actions* tab.

---

## 2. Configure Workload Identity Federation in GCP

Set once, then GitHub Actions can auth to GCP with an OIDC token — no JSON
key files ever leave GCP.

Substitute your values:

```bash
export PROJECT_ID="smart-education-assignment"
export PROJECT_NUMBER="<YOUR_PROJECT_NUMBER>"      # from step 0
export GITHUB_OWNER="<YOUR_GITHUB_USER_OR_ORG>"
export GITHUB_REPO="smart-education-portal"

export POOL_ID="github-pool"
export PROVIDER_ID="github-provider"
export GSA_NAME="github-actions-deployer"
export GSA_EMAIL="${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```

Enable the required services (safe if already enabled):

```bash
gcloud services enable \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  artifactregistry.googleapis.com \
  container.googleapis.com \
  --project "$PROJECT_ID"
```

Create the Workload Identity **Pool** and **Provider**:

```bash
gcloud iam workload-identity-pools create "$POOL_ID" \
  --project "$PROJECT_ID" \
  --location "global" \
  --display-name "GitHub Actions pool"

gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
  --project "$PROJECT_ID" \
  --location "global" \
  --workload-identity-pool "$POOL_ID" \
  --display-name "GitHub OIDC" \
  --issuer-uri "https://token.actions.githubusercontent.com" \
  --attribute-mapping "google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition "assertion.repository_owner == '${GITHUB_OWNER}'"
```

Create the Google Service Account the workflows will impersonate, and grant
it the minimum roles needed:

```bash
gcloud iam service-accounts create "$GSA_NAME" \
  --project "$PROJECT_ID" \
  --display-name "GitHub Actions deployer"

# Push images to Artifact Registry
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${GSA_EMAIL}" \
  --role "roles/artifactregistry.writer"

# Deploy to GKE (only needed for the deploy-k8s workflow)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${GSA_EMAIL}" \
  --role "roles/container.developer"
```

Let the pool impersonate the GSA, but only for **this** GitHub repo:

```bash
gcloud iam service-accounts add-iam-policy-binding "$GSA_EMAIL" \
  --project "$PROJECT_ID" \
  --role "roles/iam.workloadIdentityUser" \
  --member "principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_OWNER}/${GITHUB_REPO}"
```

Grab the two values you'll paste into GitHub secrets:

```bash
echo "GCP_WORKLOAD_IDENTITY_PROVIDER = projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
echo "GCP_SERVICE_ACCOUNT            = ${GSA_EMAIL}"
```

---

## 3. Add secrets to the GitHub repo

In GitHub → **Settings → Secrets and variables → Actions → New repository secret**, add:

| Name | Value |
|---|---|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | The `projects/…/providers/github-provider` string printed above. |
| `GCP_SERVICE_ACCOUNT` | `github-actions-deployer@smart-education-assignment.iam.gserviceaccount.com` |

That's all — no JSON files, no long-lived keys.

---

## 4. Trigger the workflows

### Push images automatically
Any push to `main` triggers `.github/workflows/deploy-images.yaml` and pushes:

```
me-central1-docker.pkg.dev/smart-education-assignment/prod-gke-repo/smart-education-backend:1.0.0
me-central1-docker.pkg.dev/smart-education-assignment/prod-gke-repo/smart-education-backend:sha-<7chars>
me-central1-docker.pkg.dev/smart-education-assignment/prod-gke-repo/smart-education-frontend:1.0.0
me-central1-docker.pkg.dev/smart-education-assignment/prod-gke-repo/smart-education-frontend:sha-<7chars>
```

### Manual push with a custom tag
Actions tab → *Build & push images to Artifact Registry* → *Run workflow* →
set the optional `tag` input (e.g. `staging`).

Confirm the images are there:

```bash
gcloud artifacts docker images list \
  me-central1-docker.pkg.dev/smart-education-assignment/prod-gke-repo \
  --include-tags
```

---

## 5. (Later) Deploy to GKE

The apply is a **separate manual workflow** so nothing touches the cluster
until you explicitly ask. In GitHub:

Actions tab → *Apply Kubernetes manifests to GKE* → *Run workflow* →
- `image_tag`: e.g. `1.0.0` or `sha-abc1234` (must already exist in Artifact Registry)
- `apply_network_policy`: leave `false` the first time; enable only after
  verifying pods stay healthy under the policy.

Before your first run, replace the placeholder Secret:

```bash
kubectl create secret generic backend-secret \
  --namespace smart-education \
  --from-literal=DATABASE_USER='smart_education' \
  --from-literal=DATABASE_PASSWORD='<a real strong password>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

Or better: bind the KSA to a GSA with Cloud SQL access via Workload
Identity and drop the password entirely.

---

## Troubleshooting

- **`Permission denied` when pushing to Artifact Registry**
  → the GSA is missing `roles/artifactregistry.writer` on the project.
- **`Unable to acquire impersonation credentials`**
  → the WIF binding at step 2 hasn't been applied for this exact
  `${GITHUB_OWNER}/${GITHUB_REPO}` pair. Recheck the `principalSet://…` string.
- **CI passes locally but fails in GitHub with DB errors**
  → CI has no Postgres. DB-tagged tests should auto-skip. If they don't,
  the `requires_db` fixture is being bypassed — check `backend/tests/conftest.py`.
- **`kubectl` says `couldn't get current server API group list`**
  → `get-credentials` didn't run. Check the deploy-k8s workflow logs for
  the `gcloud container clusters get-credentials` step.
