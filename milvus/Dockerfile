# Milvus standalone (Bisheng's vector store) with embedded etcd and local
# storage, so it needs one service and one volume (/var/lib/milvus).
FROM milvusdb/milvus:v2.5.27@sha256:ea3b924dfb2129fa2daca569eab657b4fcebc4baaed5706cf30d51e19d99b0c9

COPY embedEtcd.yaml /milvus/configs/embedEtcd.yaml
COPY user.yaml /milvus/configs/user.yaml

ENV ETCD_USE_EMBED=true \
    ETCD_DATA_DIR=/var/lib/milvus/etcd \
    ETCD_CONFIG_PATH=/milvus/configs/embedEtcd.yaml \
    COMMON_STORAGETYPE=local \
    PORT=9091

CMD ["milvus", "run", "standalone"]
