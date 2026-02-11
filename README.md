# Python-hub

Stateless FastAPI app with Postgres storage, built for Docker Compose.

## What it does

- Landing page with two actions: Snake game login and Upload a python.
- Snake game login stores a username in Postgres.
- Upload accepts an image or text, stores it in Postgres, and reports size.

## Local run (pip, no Docker)

Use Python 3.13 or 3.12 on Windows (Pillow does not ship wheels for 3.14 yet).

1. Start Postgres and set `DATABASE_URL`.
2. Install deps and run:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://pythonhub:pythonhub@localhost:5432/pythonhub
uvicorn app.main:app --reload
```

Open http://localhost:8000

## Docker Compose (app + Postgres)

```bash
docker compose up -d
```

App: http://localhost:8000

## Admin panel

Visit http://localhost:8000/admin

Set credentials via env vars:

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_SECRET`

## Docker build

```bash
docker build -t python-hub:latest .
```

## Production (Kubernetes + ArgoCD)

This repo builds a production image with GitHub Actions and pushes it to GHCR:

- Image: `ghcr.io/<org>/phub1.0:latest`
- Immutable tag: `ghcr.io/<org>/phub1.0:<git-sha>`

Use the immutable tag in your ArgoCD manifests.

### GitHub Actions

Workflow: `.github/workflows/build-and-push.yml`

Required permissions:

- `packages: write`

Optional secrets for scanning:

- `SNYK_TOKEN`

## Image replacement safety

The app is stateless. All data is stored in Postgres (volume `postgres_data`).
Replacing the app image will not delete stored data.