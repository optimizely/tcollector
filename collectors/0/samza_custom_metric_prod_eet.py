#!/usr/bin/python
import sys

from collectors.lib.samza_custom_metric_reporter import SamzaCustomMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_custom_metric_prod_eet"

KAFKA_BOOTSTRAP_SERVERS = [
    "kafka-eet.us-east-1.backend-production.optimizely:9094",
]


def main():
    reporter = SamzaCustomMetricReporter(CONSUMER_GROUP_ID, KAFKA_BOOTSTRAP_SERVERS)
    reporter.run()

if __name__ == "__main__":
    sys.exit(main())
