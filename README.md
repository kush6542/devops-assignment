# ACEest Fitness & Gym DevOps Project

DevOps assignment repository for ACEest Fitness & Gym. Contains Flask web service, unit test cases using pytest, Dockerfile, and automated CI CD setup with GitHub Actions and Jenkins.

## Overview

The original baseline was a desktop application written in tkinter. Since desktop GUIs cannot run inside headless CI runners or basic linux docker containers, the core business logic (client management, calorie calculation, weekly adherance) has been ported into a modular Flask REST API.

## Project Structure

- `app.py`: Flask application with endpoints for clients, programs, calorie calculations and progress tracking
- `requirements.txt`: Python package requirements
- `tests/test_app.py`: Unit tests using pytest framework
- `Dockerfile`: Docker config to build container image
- `.github/workflows/main.yml`: Github actions workflow file
- `Jenkinsfile`: Jenkins pipeline configuration

## How to run locally

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
# on windows use: venv\Scripts\activate
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
python app.py
```
App will be running at `http://127.0.0.1:5000/`.

## Running Tests Manually

To run the unit test suite:
```bash
pytest tests/ -v
```

To run lint check:
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

## Docker Build and Run

To build the docker image:
```bash
docker build -t aceest-app .
```

To run the tests inside the container:
```bash
docker run --rm aceest-app pytest tests/ -v
```

To run the application container:
```bash
docker run -p 5000:5000 aceest-app
```

## CI/CD Pipeline Logic

1. GitHub Actions:
Triggers on push or PR to main/master branch.
- Stage 1 (build-and-lint): Installs requirements, runs flake8 for syntax verification and runs pytest.
- Stage 2 (docker-build-test): Builds the docker image and executes `pytest tests/ -v` inside the newly built container to verify environmental consistency.

2. Jenkins Pipeline:
The `Jenkinsfile` pulls code from git, installs packages, runs linter checks, builds docker image with build tag, and executes tests in-container as a secondary validation layer.
