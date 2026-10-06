# ACEest Fitness & Gym DevOps Project

DevOps assignment repository for ACEest Fitness & Gym. Contains Flask web service, unit test cases using pytest, Dockerfile, and automated CI CD setup with GitHub Actions and Jenkins.

## Overview

The original baseline was a desktop application written in tkinter. Since desktop GUIs cannot run inside headless CI runners or basic linux docker containers, the core business logic (client management, calorie calculation, weekly adherance) has been ported into a modular Flask REST API.

## Project Structure

- `app.py`: Flask application with endpoints for clients, programs, calorie calculations and progress tracking
- `requirements.txt`: runtime dependencies (Flask, gunicorn)
- `requirements-dev.txt`: runtime + test/lint dependencies (pytest, pytest-cov, flake8)
- `tests/test_app.py`: Unit tests using pytest framework
- `Dockerfile`: multi-stage Docker build (`test` and `runtime` targets)
- `.github/workflows/main.yml`: Github actions workflow file
- `Jenkinsfile`: Jenkins pipeline configuration

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/programs` | List programs with workout, diet and calorie factor |
| POST | `/calculate-calories` | `{"weight": 70, "program": "Fat Loss (FL)"}` -> daily calories |
| POST | `/clients` | Create or update a client `{"name", "age", "weight", "program"}` |
| GET | `/clients/<name>` | Fetch a client |
| POST | `/progress` | Log weekly adherence `{"client_name", "week", "adherence": 0-100}` |

## How to run locally

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
# on windows use: venv\Scripts\activate
```

2. Install the dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Run the app:
```bash
python app.py
```
App will be running at `http://127.0.0.1:5000/`. The SQLite file path can be changed with the `ACEEST_DB` environment variable.

## Running Tests Manually

To run the unit test suite:
```bash
pytest tests/ -v
```

With coverage report:
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

To run lint check:
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

## Docker Build and Run

The Dockerfile has two targets built on a shared `python:3.11-slim` base:

- `test`: adds pytest/flake8 and the `tests/` folder, default command runs the suite
- `runtime` (default): only Flask + gunicorn and `app.py`, runs as a non-root user with a `HEALTHCHECK`

To build and run the tests inside the container:
```bash
docker build --target test -t aceest-app:test .
docker run --rm aceest-app:test
```

To build and run the application container:
```bash
docker build -t aceest-app .
docker run -p 5000:5000 aceest-app
```

## CI/CD Pipeline Logic

1. GitHub Actions (`.github/workflows/main.yml`):
Triggers on every push and every pull request, on any branch.
- Stage 1 (build-and-lint): Installs dependencies, compiles `app.py`, runs flake8 for syntax verification and runs pytest with coverage on the runner.
- Stage 2 (docker-build-test): Builds the `test` image and runs the pytest suite inside the container, then builds the `runtime` image and smoke tests it by hitting the health endpoint.

2. Jenkins Pipeline (`Jenkinsfile`):
Configured as a Pipeline job pointing at this GitHub repository (Pipeline script from SCM, triggered by poll SCM or a GitHub webhook). Each build checks out the latest code into a clean workspace, creates a fresh venv, lints and runs unit tests, builds both Docker targets tagged with the build number, and runs the tests in-container as a secondary validation layer. The workspace and test image are cleaned up after every build.

Both pipelines run the same checks so a change that passes GitHub Actions should also pass the Jenkins BUILD and vice versa.

## Branching Strategy

Work is done on short-lived branches and merged into `main`:
- `feature/*` for new functionality
- `fix/*` for bug fixes
- `test/*` for test changes
- `infra/*` / `chore/*` for Docker, CI and repo config
- `docs/*` for documentation
