#!/usr/bin/env python

import itertools
import json
import logging
import re
import time

from kafka import KafkaClient
from kafka.common import OffsetRequest, LeaderNotAvailableError
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

from collectors.lib.optimizely_utils import format_tsd_key

# TSD UTILITIES


class Metric(object):
    LAG_METRIC = 'kafka.consumer.lag'
    CONSUMER_OFFSET_METRIC = 'kafka.consumer.offset'
    TOPIC_SIZE_METRIC = 'kafka.broker.offset'
    BROKER_COUNT_METRIC = 'kafka.broker.count'


class KafkaPaths(object):
    KAFKA_CHROOT = None

    @classmethod
    def topic_offsets(cls, group, topic):
        return '%s/consumers/%s/offsets/%s' % (cls.KAFKA_CHROOT, group, topic)

    @classmethod
    def consumer_topic_partition(cls, group, topic, partition):
        return '%s/%d' % (cls.topic_offsets(group, topic), partition)

    @classmethod
    def broker_partitions(cls, topic):
        return '%s/brokers/topics/%s/partitions' % (cls.KAFKA_CHROOT, topic)

    @classmethod
    def broker_ids(cls):
        return '%s/brokers/ids' % cls.KAFKA_CHROOT

    @classmethod
    def broker(cls, broker_id):
        return '%s/brokers/ids/%s' % (cls.KAFKA_CHROOT, broker_id)

    @classmethod
    def topics(cls, consumer_group):
        return '%s/consumers/%s/offsets' % (cls.KAFKA_CHROOT, consumer_group)

    @classmethod
    def consumer_group_names(cls):
        return '%s/consumers' % cls.KAFKA_CHROOT


class KafkaOffsetCollector(object):
    KAFKA_CHROOT = None
    ZK_QUORUM = None
    CONSUMER_GROUP_PATTERNS = None
    SLEEP_TIME = None
    CLUSTER_NAME = None

    def __init__(self):
        if self.KAFKA_CHROOT is None:
            raise RuntimeError("Kafka chroot not provided!")
        if self.ZK_QUORUM is None:
            raise RuntimeError("Zookeeper quorum not provided!")
        if self.CONSUMER_GROUP_PATTERNS is None:
            raise RuntimeError("Consumer groups not provided!")
        # Compile all the regular expressions to make sure they're valid. If they aren't just throw an error.
        self.CONSUMER_GROUP_PATTERNS = [re.compile(pattern) for pattern in self.CONSUMER_GROUP_PATTERNS]
        KafkaPaths.KAFKA_CHROOT = self.KAFKA_CHROOT
        self.zk_client = KazooClient(hosts=self.ZK_QUORUM)
        self.zk_client.start()
        self.kafka_client = self.get_kafka_client()

    def emit(self, metric, value, timestamp, tags):
        print format_tsd_key(metric, value, timestamp, tags)

    # KAFKA OFFSET MONITORING

    def get_consumer_groups(self):
        """
        Return a list of all consumer groups found in Zookeeper that match the patterns we are looking for.
        """
        consumer_group_names = self.zk_client.get_children(KafkaPaths.consumer_group_names())
        return filter(lambda x: any(regex.match(x) for regex in self.CONSUMER_GROUP_PATTERNS), consumer_group_names)

    def get_partitions(self, group, topic):
        """
        Return a list of all partitions being consumed by a given consumer group on a given topic.
        """
        try:
            return map(int, self.zk_client.get_children(KafkaPaths.topic_offsets(group, topic)))
        except NoNodeError as err:
            logging.exception(err)
            return []

    def get_kafka_topics(self, consumer_group):
        """
        Return a list of all kafka topics consumed by a given single consumer
        group (none if there is any Zookeeper error).
        """
        try:
            return set(map(str, self.zk_client.get_children(KafkaPaths.topics(consumer_group))))
        except NoNodeError as err:
            logging.exception(err)
            return []

    def get_broker_count(self):
        broker_ids = self.zk_client.get_children(KafkaPaths.broker_ids())
        return len(broker_ids)

    def get_kafka_brokers(self):
        """
        Return a list of all kafka broker hosts or an empty list if the broker list
        cannot be fetched
        """
        brokers = []
        for broker_id in self.zk_client.get_children(KafkaPaths.broker_ids()):
            broker_desc = json.loads(self.zk_client.get(KafkaPaths.broker(broker_id))[0])
            brokers.append(broker_desc['host'].split('.')[0])
        return brokers

    def get_consumer_group_offset(self, group, topic, partition):
        """
        Get the consumer group offset for a particular topic and partition.
        """
        path = KafkaPaths.consumer_topic_partition(group, topic, partition)
        return int(self.zk_client.get(path)[0])

    def get_topic_partitions(self, topic):
        """
        Get the list of partitions for a topic - given n topics this will be a
        list containing the numbers [0,...,n-1].
        """
        path = KafkaPaths.broker_partitions(topic)
        return map(int, self.zk_client.get_children(path))

    def get_topic_partition_size(self, topic, partition):
        """
        This will get the size of a particular partition for a topic.
        """
        try:
            offset_response = self.kafka_client.send_offset_request([OffsetRequest(topic, partition, -1, 1)])[0]
            partition_size = offset_response.offsets[0]
            return partition_size
        except LeaderNotAvailableError as err:
            logging.exception(err)
            return None

    def get_kafka_client(self):
        """
        Initialize a Kafka client to connect to the brokers.
        """
        kafka_brokers = self.get_kafka_brokers()
        if not kafka_brokers:
            raise RuntimeError('KAFKA_BROKERS could not be fetched from ZK')
        kafka_init = 'env=production kafka=%s zk=%s' % (','.join(kafka_brokers), self.ZK_QUORUM)
        return KafkaClient(kafka_init)

    def report_topic_partition_sizes(self, timestamp):
        # Get the list of all topics we might be monitoring.
        consumer_groups = self.get_consumer_groups()
        all_topics_consumed = itertools.chain.from_iterable(
            self.get_kafka_topics(consumer_group) for consumer_group in consumer_groups
        )
        all_topics = set(all_topics_consumed)
        for topic in all_topics:
            partitions = self.get_topic_partitions(topic)
            for partition in partitions:
                partition_size = self.get_topic_partition_size(topic, partition)
                if partition_size:
                    self.emit(Metric.TOPIC_SIZE_METRIC, partition_size, timestamp,
                        tags={"topic": topic,
                              "partition": partition,
                              "clusterid": self.CLUSTER_NAME})

    def report_consumer_group_offsets(self, consumer_group, time_):
        topics = self.get_kafka_topics(consumer_group)
        for topic in topics:
            for partition in self.get_partitions(consumer_group, topic):
                offset = self.get_consumer_group_offset(consumer_group, topic, partition)
                partition_size = self.get_topic_partition_size(topic, partition)
                if not partition_size:
                    continue
                lag = partition_size - offset

                self.emit(Metric.CONSUMER_OFFSET_METRIC, offset, time_,
                          tags={"consumer_group": consumer_group,
                                "topic": topic,
                                "partition": partition,
                                "clusterid": self.CLUSTER_NAME})

                self.emit(Metric.LAG_METRIC, lag, time_,
                          tags={"consumer_group": consumer_group,
                                "topic": topic,
                                "partition": partition,
                                "clusterid": self.CLUSTER_NAME})

    def report(self):
        consumer_groups = self.get_consumer_groups()

        while True:
            time_ = int(time.time())

            try:
                num_brokers = self.get_broker_count()
                self.emit(Metric.BROKER_COUNT_METRIC, num_brokers, time_,
                          tags={"clusterid": self.CLUSTER_NAME})
            except Exception:
                logging.exception("Failed to retrieve total broker count for cluster %s" % self.CLUSTER_NAME)

            try:
                self.report_topic_partition_sizes(time_)
            except Exception:
                logging.exception("Failed to retrieve partition sizes on topics for cluster %s" % self.CLUSTER_NAME)

            # For the set of consumer groups we're monitoring,
            # calculate topic size and lag for all the topics/partitions
            for consumer_group in consumer_groups:
                try:
                    self.report_consumer_group_offsets(consumer_group, time_)
                except Exception:
                    logging.exception("Failed to get consumer lag for group %s on cluster %s" % (consumer_group, self.CLUSTER_NAME))

            if self.SLEEP_TIME:
                time.sleep(self.SLEEP_TIME)

        self.zk_client.stop()
        self.kafka_client.close()
        self.zk_client.close()
