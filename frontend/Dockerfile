# Bisheng web UI (nginx). Serves the platform and workspace apps and proxies
# /api to the Bisheng API and file links to RustFS over Railway's private network.
FROM dataelement/bisheng-frontend:v3.0.1@sha256:4985058f0097b4796daf9dc5081068ed04e880b4c4f0fad3384c220f7d62863a

COPY default.conf.template /etc/nginx/bisheng.conf.template
COPY railway-start.sh /railway-start.sh

ENV PORT=3001
ENTRYPOINT ["sh", "/railway-start.sh"]
