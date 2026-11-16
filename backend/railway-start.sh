#!/bin/bash
# Railway wrapper for the Bisheng backend image.
set -euo pipefail
cd /app
export PYTHONPATH="./"

# Writes /app/bisheng/config.yaml from the Railway variables and, on the API,
# creates the MySQL database Bisheng uses.
python /app/railway_config.py

case "${BISHENG_ROLE:-api}" in
  api)
    echo "Running database migrations..."
    alembic upgrade head
    echo "Starting Bisheng API on [::]:${PORT}"
    # Bind :: so the API answers on Railway's IPv6 private network (and IPv4).
    exec uvicorn bisheng.main:app --host :: --port "${PORT}" --no-access-log --workers "${API_WORKERS:-2}"
    ;;
  worker)
    # Same processes as the upstream "worker" mode (docker/bisheng/entrypoint.sh).
    celery -A bisheng.worker.main worker -l info -c "${WORKER_CONCURRENCY:-100}" -P threads \
      -Q knowledge_celery,ocr_celery,workflow_celery,celery -n min_worker@%h &
    python bisheng/linsight/worker.py --worker_num 1 --max_concurrency 5 &
    celery -A bisheng.worker.main beat -l info &
    # Exit (and let Railway restart the service) as soon as any of them stops.
    wait -n
    echo "A worker process exited; stopping so Railway restarts the service." >&2
    exit 1
    ;;
  *)
    echo "Unknown BISHENG_ROLE '${BISHENG_ROLE}' (use api or worker)" >&2
    exit 1
    ;;
esac
