# OpenFGA (Bisheng's permission engine). The official image is distroless, so a
# static busybox shell is added to run "migrate" before "run" in one service.
FROM busybox:1.37.0-musl@sha256:f6a95d611e0a8780fabdb2aec43e31275b2720dfefa3e41b16835bfc42454478 AS busybox

FROM openfga/openfga:v1.19.0@sha256:78d1fa601d42340ecb131305d80d3767d0f254f9b1bc3646f9a557e11b24c63a
COPY --from=busybox /bin/busybox /busybox/busybox
COPY railway-start.sh /railway-start.sh

ENV OPENFGA_DATASTORE_ENGINE=mysql \
    OPENFGA_HTTP_ADDR=[::]:8080 \
    OPENFGA_GRPC_ADDR=[::]:8081 \
    OPENFGA_PLAYGROUND_ENABLED=false \
    OPENFGA_LOG_FORMAT=json \
    OPENFGA_CHECK_QUERY_CACHE_ENABLED=true \
    OPENFGA_CHECK_QUERY_CACHE_TTL=30s \
    OPENFGA_CHECK_ITERATOR_CACHE_ENABLED=true \
    OPENFGA_CHECK_ITERATOR_CACHE_TTL=30s \
    OPENFGA_CACHE_CONTROLLER_ENABLED=true \
    OPENFGA_CACHE_CONTROLLER_TTL=10s \
    OPENFGA_DATASTORE_MAX_OPEN_CONNS=40 \
    OPENFGA_DATASTORE_MAX_IDLE_CONNS=20 \
    OPENFGA_RESOLVE_NODE_LIMIT=25 \
    OPENFGA_LIST_OBJECTS_MAX_RESULTS=1000 \
    PORT=8080

ENTRYPOINT ["/busybox/busybox", "sh", "/railway-start.sh"]
