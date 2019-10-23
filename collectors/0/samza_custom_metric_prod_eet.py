#!/usr/bin/python
import sys

from collectors.lib.samza_custom_metric_reporter import SamzaCustomMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_custom_metric_prod_eet"

# retry 4 times if any region node gets de-registered from DNS
KAFKA_BOOTSTRAP_SERVERS = [
    "prod-kafka-eet.us-east-1.optimizely:9094"
] * 4


def main():
    reporter = SamzaCustomMetricReporter(CONSUMER_GROUP_ID, KAFKA_BOOTSTRAP_SERVERS, depth_range=xrange(5))
    reporter.run()


if __name__ == "__main__":
    sys.exit(main())
