# Elasticsearch 8 for Bisheng's keyword search. Single node, password auth on
# (user "elastic", ELASTIC_PASSWORD), HTTP on [::]:9200 on Railway's private
# network only (no public domain).
FROM elastic/elasticsearch:8.19.25@sha256:5bfdf4313b9bc05c0d46fe219d6e67710eb0c7654ed6c275167bdf9beefc56f0

USER root
COPY --chown=1000:0 elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
COPY railway-start.sh /railway-start.sh

ENV ES_JAVA_OPTS="-Xms1g -Xmx1g"

ENTRYPOINT ["/bin/bash", "/railway-start.sh"]
