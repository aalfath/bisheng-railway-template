# RustFS: S3-compatible object storage for Bisheng's uploaded files
# (MinIO no longer publishes images). Data lives on the /data volume.
FROM rustfs/rustfs:1.0.6@sha256:ee717072290bec9b11abfc0365f8310b00df1cd9b3639943edae47bdef05044a

# Railway volumes are root-owned; the image's default user can't write them.
USER root
ENV RUSTFS_ADDRESS=[::]:9000 \
    RUSTFS_VOLUMES=/data \
    RUSTFS_CONSOLE_ENABLE=false \
    PORT=9000
