# SWE40006 Project
TasketCasket - Task Manager

A small Flask web app for tracking tasks. It is the application for our CI/CD pipeline project (SWE40006), so the feature set is deliberately simple and the focus is on build, test, deploy and monitor.

## Authors
Tom Goodison - 103638899@student.swin.edu.au
Pimpatra Chotteerapirom - 103504330@student.swin.edu.au
Eugene Baek - 105045569@student.swin.edu.au
Maher Basir Afzal 105523230@student.swin.edu.au


## Features
- Create, view, edit and delete tasks
- Three statuses: **pending**, **in progress**, **complete** 
- `GET /health` reports app status, database connectivity, build version and environment

### Prerequisites
| Tool | Check it works |
|---|---|
| [Git](https://git-scm.com/downloads) | `git --version` |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | `uv --version` |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | `docker --version` |


### Choose how to run it 
- **Option A: Docker Compose .** 
- **Option B: uv.** 


## Option A: Docker Compose
Req
From the `app/` folder:
 
```bash
docker compose up --build
```

The first run takes a few minutes while the images download and build. It starts PostgreSQL, builds the app image from the `Dockerfile`, applies the database migrations
and starts the app. Wait until the log shows the app is running, then open
http://localhost:5000
 
To stop it, press `Ctrl+C`, then run `docker compose down`. Your tasks are kept in a Docker volume and are still there next time. To delete the data and start fresh, run `docker compose down -v`.

## Option B: Run with uv
 
### B1. Install dependencies
 Run these from the `app/` folder

```bash
   uv sync
```

### B2. Start a database 
 
**PostgreSQL in Docker .** (first time only; afterwards docker start tasks-db):
Make sure Docker Desktop is running, then:
 
```bash
   docker run --name tasks-db -e POSTGRES_USER=app \
   -e POSTGRES_PASSWORD=change-me -e POSTGRES_DB=app \
   -p 5432:5432 -d postgres:17
```


### B3. Configure the environment
 
Copy the example file and create your own `.env`:
 
```bash
cp .env.example .env
```
 
For the Docker database above, make sure it contains:
 
```
  DATABASE_URL=postgresql://app:change-me@localhost:5432/app
```
 
 ### B4. Create the database tables
 
```bash
uv run flask --app app:create_app db upgrade -d ../migrations
```
This applies the migrations in the `migrations/` folder at the repository root. 

### B5. Run the app
 
```bash
uv run flask --app app:create_app run 
```
 
Open http://127.0.0.1:5000 in your browser.


### B6. Stop everything
 
Press `Ctrl+C` in the terminal to stop the app


## Check that it works
  
1. Click **+** in the top bar and create a task.
2. Use the buttons on the task card to start it, complete it, undo it, edit it and
   delete it.
3. Open `/health` (for example http://localhost:5000/health). You should see:
```json
   {"status": "ok", "database": "connected", "version": "dev", "environment": "local"}
```
4. Check the page footer shows the version and environment.


## Run the tests and linting
 
From the `app/` folder (this needs `uv sync`):
 
```bash
uv run pytest -v         # unit and integration tests
uv run ruff check .      # linting
```
All tests should pass and ruff should report `All checks passed!`.


## Troubleshooting
 
| Problem | Fix |
|---|---|
| Compose: `db` keeps restarting or is `unhealthy` | The saved database data was corrupted by an unclean shutdown. Run `docker compose down -v`, then `docker compose up --build`. This deletes local data. |
| `no such table: tasks` | The migrations have not been applied. Run step B4. Also check `DATABASE_URL` is the database you expect. |
| `connection refused` on port 5432 | The Docker database is not running. Start Docker Desktop, then `docker start tasks-db`. |
| Port already in use (5000, 5001 or 5432) | Stop whatever is using it, or change the port number (for Flask, `--port 5002`). |
| `uv: command not found` | Install uv (step 1) and open a new terminal. |
| `/health` shows `503` / `degraded` | The app cannot reach the database. Check the database is running and `DATABASE_URL` is correct. |


## Health check
 
`GET /health` returns:
 
```json
{"status": "ok", "database": "connected", "version": "abc1234", "environment": "staging"}
```
 
- HTTP **200** when the app can reach the database
- HTTP **503** with `"status": "degraded"` when it cannot
It is used for the load balancer health check, smoke tests after a deploy, and to
confirm which version is live.


## Docker
 
The image is defined by the `Dockerfile` in the `app/` folder:
 
```bash
cd app
docker build -t tasketcasket .
```
 
The container reads all configuration from the environment variables above and runs
the database migrations before starting Gunicorn on port 500

## CI/CD pipeline
How the code reaches the staging and production servers. 
GitHub Actions deploys them automatically.
 
### How a change is deployed
 
1. Work on a branch and open a pull request into `main`. CI runs lint, tests and a
   Docker build.
2. After a teammate approves and CI passes, merge the pull request.
3. Merging starts the **Deploy** workflow: it builds the image, pushes it to GitHub
   Container Registry, and deploys it to **staging**.
4. The Playwright end-to-end tests run against staging.
5. After a manual approval in GitHub, the same image is deployed to **production**.


### How to see the result
- Follow each run in the **Actions** tab of the GitHub repository. 
- Open the staging or production address in a browser. The page footer and `/health`show the environment (`staging` or `production`) and the build version (the git commit SHA), which confirms which build is live.

### Pipeline details
 
- **CI** (`.github/workflows/ci.yml`) runs on every pull request: lint, pytest and a
  Docker build. Merging into `main` needs a passing CI and one approving review.
- **Deploy** (`.github/workflows/deploy.yml`) builds the image, pushes it to GitHub
  Container Registry, deploys to **staging** on AWS, runs the Playwright end-to-end
  tests, then deploys to **production** after a manual approval.
- On each server, `deploy/deploy.sh` logs in to GHCR, pulls the image and restarts the stack with `docker compose`. It expects `IMAGE`, `DATABASE_URL`, `SECRET_KEY`,
  `APP_ENV`, `APP_VERSION`, `GHCR_USER` and `GHCR_TOKEN` in the environment.
The staging and production URLs and credentials are not in this repository. Staging and production use separate AWS RDS PostgreSQL databases, and their secrets are stored in GitHub Secrets.