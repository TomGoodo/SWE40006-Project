#!/usr/bin/env bash
# Runs on the server. Expects IMAGE, DATABASE_URL, SECRET_KEY, APP_ENV,
# GHCR_USER and GHCR_TOKEN in the environment (passed by the workflow).
set -euo pipefail

cd /opt/app

echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

export IMAGE DATABASE_URL SECRET_KEY APP_ENV
docker compose pull
docker compose up -d --remove-orphans
docker image prune -f

docker logout ghcr.io
