"""Build Bisheng's config.yaml from Railway variables.

Bisheng expects the passwords inside database_url and redis_url to be
Fernet-encrypted with the key in bisheng/core/config/settings.py, so this
script encrypts them at start-up. Nothing secret is printed.
"""
import json
import os
import re
import sys
import time
from urllib.parse import quote, unquote, urlparse

import yaml
from cryptography.fernet import Fernet

ROLE = os.environ.get("BISHENG_ROLE", "api")


def need(name):
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"railway_config: required variable {name} is empty")
    return value


def fernet_key():
    src = open("/app/bisheng/core/config/settings.py", encoding="utf-8").read()
    match = re.search(r'^secret_key = "([^"]+)"', src, re.M)
    if not match:
        sys.exit("railway_config: could not find Bisheng's Fernet key")
    return match.group(1).encode()


FERNET = Fernet(fernet_key())


def enc(password):
    return FERNET.encrypt(password.encode()).decode()


# --- MySQL -----------------------------------------------------------------
mysql = urlparse(need("MYSQL_URL"))
db_name = os.environ.get("BISHENG_DB_NAME", "bisheng")
mysql_user = unquote(mysql.username or "root")
mysql_pass = unquote(mysql.password or "")
mysql_host = mysql.hostname
mysql_port = mysql.port or 3306

if ROLE == "api":
    import pymysql

    deadline = time.time() + 600
    while True:
        try:
            conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user,
                                   password=mysql_pass, connect_timeout=10)
            with conn.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conn.close()
            print(f"railway_config: MySQL database '{db_name}' is ready")
            break
        except Exception as exc:  # MySQL may still be starting
            if time.time() > deadline:
                sys.exit(f"railway_config: MySQL not reachable: {exc}")
            print(f"railway_config: waiting for MySQL ({exc.__class__.__name__})")
            time.sleep(5)

if ROLE == "worker":
    # Start the workers only once the API has migrated the database to the
    # current Alembic head (on a fresh deploy both start at the same time).
    import pymysql
    from alembic.config import Config as AlembicConfig
    from alembic.script import ScriptDirectory

    heads = set(ScriptDirectory.from_config(AlembicConfig("/app/alembic.ini")).get_heads())
    deadline = time.time() + 1200
    while True:
        current = set()
        try:
            conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user,
                                   password=mysql_pass, database=db_name, connect_timeout=10)
            with conn.cursor() as cur:
                cur.execute("SELECT version_num FROM alembic_version")
                current = {row[0] for row in cur.fetchall()}
            conn.close()
        except Exception:
            pass
        if heads and heads <= current:
            print("railway_config: database is at the Alembic head")
            break
        if time.time() > deadline:
            print("railway_config: database not at the Alembic head after 20 min; starting anyway")
            break
        print("railway_config: waiting for the API to finish database migrations")
        time.sleep(10)

database_url = (
    f"mysql+pymysql://{quote(mysql_user, safe='')}:{enc(mysql_pass)}"
    f"@{mysql_host}:{mysql_port}/{db_name}?charset=utf8mb4"
)

# --- Redis -----------------------------------------------------------------
redis = urlparse(need("REDIS_URL"))
redis_auth = ""
if redis.password:
    redis_auth = f"{quote(unquote(redis.username or 'default'), safe='')}:{enc(unquote(redis.password))}@"
redis_base = f"redis://{redis_auth}{redis.hostname}:{redis.port or 6379}"

# --- Search, vectors, object storage ---------------------------------------
es_password = need("ELASTIC_PASSWORD")
es_ssl_verify = repr({"basic_auth": ("elastic", es_password)})
s3_endpoint = need("S3_ENDPOINT")

config = {
    "database_url": database_url,
    "database_pool": {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "10")),
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "ssl": {"enabled": False},
    },
    "redis_url": f"{redis_base}/1",
    "celery_redis_url": f"{redis_base}/2",
    "openfga": {"enabled": True, "api_url": need("OPENFGA_URL")},
    "knowledge_file_worker": {"ocr_queue_enabled": False, "ocr_queue": "ocr_celery",
                              "fair_scheduler_enabled": False},
    "celery_task": {"task_routers": {"bisheng.worker.knowledge.*": {"queue": "knowledge_celery"}}},
    "vector_stores": {
        "milvus": {
            "connection_args": json.dumps({"host": need("MILVUS_HOST"),
                                           "port": os.environ.get("MILVUS_PORT", "19530"),
                                           "user": "", "password": "", "secure": False}),
            "is_partition": "true",
            "partition_suffix": "1",
        },
        "elasticsearch": {"url": need("ELASTICSEARCH_URL"), "ssl_verify": es_ssl_verify},
    },
    "object_storage": {
        "type": "minio",
        "minio": {
            "schema": False,
            "cert_check": False,
            "endpoint": s3_endpoint,
            "sharepoint": s3_endpoint,
            "access_key": need("S3_ACCESS_KEY"),
            "secret_key": need("S3_SECRET_KEY"),
            "public_bucket": "bisheng",
            "tmp_bucket": "tmp-dir",
        },
    },
    "environment": {
        "env": "dev",
        "uns_support": ["png", "jpg", "jpeg", "bmp", "doc", "docx", "ppt", "pptx", "xls", "xlsx",
                        "txt", "md", "html", "pdf", "csv", "tiff"],
    },
    "logger_conf": {
        "level": os.environ.get("LOG_LEVEL", "INFO"),
        "format": "<level>[{time:YYYY-MM-DD HH:mm:ss.SSSSSS}] [{level.name} process-{process.id}-{thread.id} {name}:{line}]</level> - <level>trace={extra[trace_id]} {message}</level>",
        "handlers": [],
    },
}

# No admin block: in v3.0.1 a config-file admin gets no external_id (the login
# account), so it can't log in. The first account registered in the web UI
# becomes the super admin instead (upstream behaviour).

with open("/app/bisheng/config.yaml", "w", encoding="utf-8") as fh:
    yaml.safe_dump(config, fh, allow_unicode=True, sort_keys=False)
os.chmod("/app/bisheng/config.yaml", 0o600)
print(f"railway_config: wrote /app/bisheng/config.yaml for role '{ROLE}'")
