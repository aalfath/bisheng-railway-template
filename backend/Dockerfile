# Bisheng API and worker (one image, two Railway services).
# BISHENG_ROLE=api (default) runs migrations and the API on $PORT;
# BISHENG_ROLE=worker runs the Celery workers, Celery beat and the LinSight worker.
FROM dataelement/bisheng-backend:v3.0.1@sha256:7462f5efa9e596388763b91195ba57ffb7693a22b0798dccb533c27501f15023

COPY railway_config.py /app/railway_config.py
COPY railway-start.sh /app/railway-start.sh

ENV BISHENG_ROLE=api \
    PORT=7860 \
    TZ=UTC

WORKDIR /app
ENTRYPOINT ["bash", "/app/railway-start.sh"]
