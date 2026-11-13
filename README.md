# SmartDesk AI — end-to-end Python, AI, DevOps and CI/CD classroom project

One application demonstrates software development, training a small text classifier,
REST APIs, database persistence, automated Python scripts, automated tests, Docker,
GitHub Actions CI, container image delivery, and Linux deployment operations.

This is a teaching demo based on a **tiny synthetic dataset**, not a production-ready
AI or security-hardened ticketing system. Do not send real customer or confidential data.

## Prerequisites

- Python 3.12 and pip, Git, Docker Desktop (or Docker Engine + Compose), a GitHub account.
- Terminal commands below assume macOS / Linux / Git Bash. On Windows use a virtual
  environment activation command suitable for PowerShell.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m scripts.check_dataset
python -m scripts.train_model
python -m pytest -q
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API documentation.
In a *second terminal*:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/tickets \
  -H 'Content-Type: application/json' \
  -d '{"text":"I was charged twice for my subscription, urgent refund"}'
python -m scripts.smoke_test
```

The `/tickets` POST returns an ID, category, priority, confidence, and needs_review.
Fetch it with GET `/tickets/{ticket_id}`. The `/metrics` endpoint shows counts.
Priority is a **rule**, while category is predicted by the **ML classifier**.

## Docker run

Stop the local Uvicorn process (Ctrl+C), then:

```bash
docker compose up --build -d
docker compose ps
python -m scripts.smoke_test
docker compose logs -f api
# Ctrl+C leaves the application running
docker compose down
```

The named Docker volume retains SQLite data when containers are recreated. Deleting
volumes with `docker compose down -v` will erase the demo database.

## Git + CI/CD workflow

```bash
git init
git add .
git commit -m "Build SmartDesk AI MVP"
git branch -M main
# Create an empty GitHub repo first, and substitute your URL:
git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
git push -u origin main
```

The GitHub Actions workflow in `.github/workflows/ci-cd.yml` automatically validates
training data, trains/evaluates the classifier, lints Python, tests APIs, and builds a
Docker image. On a successful push to `main`, a second job publishes an image
versioned with the commit SHA to GitHub Container Registry (GHCR). Repository package
visibility and permissions may need configuration. Pull requests run validation
but do not publish images.

**Important terminology:** Publishing a tested container image is *continuous delivery*;
production *continuous deployment* additionally updates the running environment.
The server rollout below is deliberately manual so students can observe the steps.

## Linux server exercise (optional VM)

After the public image has been published and Docker installed on a Linux server:

```bash
# Copy compose.prod.yaml onto the Linux server.
export IMAGE_REF=ghcr.io/YOUR-USER/YOUR-REPO:YOUR-COMMIT-SHA
docker compose -f compose.prod.yaml pull
docker compose -f compose.prod.yaml up -d
docker compose -f compose.prod.yaml ps
BASE_URL=http://127.0.0.1:8000 python -m scripts.smoke_test
```

For private images, authenticate to GHCR with a suitable token/permission first.
When using remote servers, run `scripts/smoke_test.py` from a machine that can access
the service; for a public service configure TLS, authentication, firewall and a proxy.

**Rollback demonstration:** Set `IMAGE_REF` to the previously published SHA, run
`docker compose -f compose.prod.yaml up -d` again, and repeat the smoke test. Do not
roll back database schema changes blindly; plan migrations and backups separately.

## Operations and responsible deployment

- Keep secrets in a secret manager or CI platform secrets; never commit `.env` tokens.
- Limit API exposure: the demo is unauthenticated and intended for a local lab.
- Monitor `docker compose logs -f api` plus `/health`, `/metrics`, and test errors.
- Treat low-confidence classifications as human-review cases; monitor model quality.
- Use real labeled data, versioned artifacts, a robust database, authentication,
  monitoring/alerting, pinned dependencies, security scans, and release approvals
  before considering a production implementation.

See `WORKSHOP_GUIDE.md` for full-day instructor timings, learning outcomes and labs.
