#!/usr/bin/python
import sys

from collectors.lib.samza_metric_reporter import SamzaMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_prod"

# FIXME: Should we set this as an ENV?
KAFKA_BOOTSTRAP_SERVERS = [
    'kafkaprod-1:9092',
    'kafkaprod-2:9092',
    'kafkaprod-3:9092',
    'kafkaprod-4:9092',
    'kafkaprod-5:9092',
    'kafkaprod-6:9092'
]

METRIC_CLASSES = ['org.apache.samza.system.kafka.KafkaSystemConsumerMetrics',
                  'org.apache.samza.metrics.JvmMetrics',
                  'org.apache.samza.container.SamzaContainerMetrics']


def main():
    reporter = SamzaMetricReporter(CONSUMER_GROUP_ID, KAFKA_BOOTSTRAP_SERVERS, metric_classes=METRIC_CLASSES)
    reporter.run()


if __name__ == "__main__":
    sys.exit(main())
