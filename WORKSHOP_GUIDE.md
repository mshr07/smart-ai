# Trainer's marathon-class guide (7.5–8 hours including breaks)

## The company's actual requirement

"Build a customer-support ticket API in Python. Automatically classify complaints
as billing/login/technical, flag urgent cases, persist each ticket, expose health and
usage counts, run test automation on every PR, package as a container, publish a
versioned release on main, deploy to a Linux server, verify and roll back releases."

**Definition of done:** working POST and GET APIs, a reproducible AI model, automated
unit/API tests, passing CI, a built Docker image, GHCR release, running Docker Compose
deployment, successful smoke test, documented logs and rollback steps.

## Explain the key distinction

- **Python application code:** handles HTTP requests, makes model predictions,
  applies priority rules, accesses the SQLite database.
- **Python automation scripts:** validate datasets, train/evaluate models,
  run smoke tests, and in advanced labs report health/model statistics.
- **DevOps:** shared developer/operations practices for reliable delivery and support.
- **CI:** automatic checks after pushes and PRs, catching broken changes.
- **Continuous delivery:** release artifact ready to deploy after checks.
- **Continuous deployment:** automatic rollout to the runtime environment.
- **MLOps:** datasets, training, model versioning, evaluation, drift and retraining.

## Recommended agenda

| Time | Lesson | Live proof |
|---|---|---|
| 00:00–00:35 | Business problem, API/HTTP and lifecycle | Draw request and delivery flows |
| 00:35–01:15 | Terminal, environments, Git basics | Create venv and first commit |
| 01:15–02:15 | FastAPI + SQLite | POST ticket via `/docs`; GET it |
| 02:15–03:10 | AI basics and Python dataset/model scripts | Run checks, train and predict |
| 03:10–03:25 | Break | |
| 03:25–04:05 | Testing and useful failure | Deliberately fail and repair pytest |
| 04:05–04:55 | Docker and Compose | Build container and persist tickets |
| 04:55–05:10 | Break | |
| 05:10–06:10 | GitHub Actions CI, image publishing | Observe green/red jobs |
| 06:10–06:55 | Linux deployment/health/logs/rollback | Swap immutable version tags |
| 06:55–07:25 | Python operations scripting + MLOps | HTTP smoke script; quality thresholds |
| 07:25–07:50 | Group capstone and interview recap | Submit PR and demo a release |

## Sequenced demonstration

1. **Requirement and architecture** — identify customer, backend, model, database,
   repo, CI runner, registry, VM and end-user paths.
2. **Python API** — explain JSON, HTTP POST/GET, status codes, FastAPI `/docs`,
   validation and SQLite; start server with Uvicorn.
3. **AI training** — explain labeled data, `TfidfVectorizer`, logistic regression,
   training/inference, confidence and review; run validation and training scripts.
4. **Tests** — explain unit vs integration/API vs post-deploy smoke tests;
   `pytest -q`, invalid input and missing item tests.
5. **Containers** — Dockerfile base image, copy, pip install, train, port, user,
   runtime volume and image versus container.
6. **Git and CI** — show branch, PR, workflow YAML, runner, `checkout`,
   `setup-python`, `ruff`, training, pytest, Docker build, commit status.
7. **CD** — publish immutable container tagged by Git SHA to GHCR;
   show manual staging VM rollout, health and smoke. Point out that fully automatic
   deployment needs a further deploy job and secure server credentials.
8. **Operations** — inspect logs, record alerts/quality metrics; force a bad change,
   watch CI fail, then fix and redeploy; version rollback safely.

## Deliberate incident drills

- Change one API test to demand status 200 on POST (which correctly returns 201):
  CI becomes red. Correct the test and repeat.
- Add a malformed row or unsupported label to `data/tickets.csv`: dataset validation
  fails *before* training and deployment.
- Run two servers on port 8000 to demonstrate port conflicts and inspect `docker ps`.
- Point smoke tests at port 9999 to see an operational failure.
- Change only a text classification example and retrain; explain data and model
  versioning, then restore the lab dataset for predictable results.

## Where Python scripting creates practical value

| Moment | Python script | What it replaces |
|---|---|---|
| Before model training | `check_dataset.py` | Manual inspection of CSV rows |
| AI build | `train_model.py` | Manual training clicks and saving |
| API runtime | `app/main.py` | Manual triage and ticket entry |
| PR verification | `tests/test_api.py` | Repeated manual endpoint testing |
| After deployment | `smoke_test.py` | Opening several URLs and checking data by hand |
| Next stage | `monitor.py` (exercise) | Manually watching multiple deployments |
| MLOps extension | `retrain.py` (exercise) | Manual data refresh and retraining |

## Exit ticket / interview practice

1. What is the difference between Git, GitHub, CI and CD?
2. Why do we use requirements.txt, virtual environments and pinned versions?
3. What does a Dockerfile build, and what does Docker Compose start?
4. What causes a GitHub Actions workflow to execute?
5. What happens when a single test fails during CI?
6. What difference is there between an image and a container?
7. Which Python file trains the AI model, and which serves predictions?
8. What is an ML confidence score and why might it be unreliable?
9. Why do we tag releases with a commit hash instead of always using `latest`?
10. How do health checks, logs and rollback limit damage from a faulty release?

## Extension for a second marathon

Add API authentication, PostgreSQL, structured logs, OpenTelemetry and alerts;
separate model release from application release; add more labeled ticket data,
robust cross-validation, per-class metrics, model monitoring and drift alerts;
add a cloud deployment job with approvals and secrets, and optionally LLM summarization.
