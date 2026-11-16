#!/bin/sh
# Render the nginx config from Railway variables, then start nginx.
set -eu
: "${API_HOST:?API_HOST must be the Bisheng API host:port (private network)}"
case "$API_HOST" in :*) echo "API_HOST has no host part (${API_HOST}); is the API service deployed?" >&2; exit 1;; esac
: "${S3_ENDPOINT:?S3_ENDPOINT must be the RustFS host:port (private network)}"
sed -e "s#__PORT__#${PORT}#g" \
    -e "s#__API_HOST__#${API_HOST}#g" \
    -e "s#__S3_ENDPOINT__#${S3_ENDPOINT}#g" \
    /etc/nginx/bisheng.conf.template > /etc/nginx/conf.d/default.conf
# nginx resolves upstream names at start; wait until the API's private name resolves.
host="${API_HOST%:*}"
i=0
until getent hosts "$host" >/dev/null 2>&1; do
  i=$((i+1)); [ "$i" -gt 60 ] && { echo "cannot resolve $host" >&2; exit 1; }
  echo "waiting for $host to resolve..."; sleep 5
done
exec nginx -g 'daemon off;'
