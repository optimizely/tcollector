#!/usr/bin/env bash

java -Dlog4j.rootlogger=OFF \
  -Djava.util.logging.config.file=/opt/backend-jars/tool/resources/logging.properties \
  -cp /opt/backend-jars/tool/resources:/opt/backend-jars/tool/current/tool-all.jar:/opt/backend-jars/tool/current/tool-provided.jar \
  com.optimizely.backend.tcollector.SessionDBCollector \
  -zk $MONITORED_ZOOKEEPER_QUORUMS | grep sessiondb
