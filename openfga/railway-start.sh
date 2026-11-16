# Runs under busybox sh. Applies OpenFGA's MySQL migrations, then serves.
set -eu
: "${OPENFGA_DATASTORE_URI:?OPENFGA_DATASTORE_URI is required}"
i=0
until /openfga migrate; do
  i=$((i+1))
  if [ "$i" -gt 60 ]; then echo "openfga migrate kept failing" >&2; exit 1; fi
  echo "openfga migrate failed (MySQL starting?), retrying in 5 s" >&2
  /busybox/busybox sleep 5
done
exec /openfga run
