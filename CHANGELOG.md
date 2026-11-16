# Changelog

Deployers: read the entry for a version before you apply its update on Railway.

## 3.0.1-railway.2 (2026-11-16)

- README: add the Deploy on Railway button for the published template (`bisheng`). No change to any service, image or variable; nothing to redeploy.

## 3.0.1-railway.1 (2026-11-16)

First release of the template.

- Bisheng v3.0.1 (`dataelement/bisheng-backend` and `dataelement/bisheng-frontend`, pinned by digest).
- OpenFGA v1.19.0, Elasticsearch 8.19.25, Milvus v2.5.27 (embedded etcd, local storage) and RustFS 1.0.6 (S3 storage), each pinned by digest.
- Railway MySQL and Redis.
- The first account registered in the web UI becomes the super admin (no default password).
