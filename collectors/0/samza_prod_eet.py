#!/usr/bin/python
import sys

from collectors.lib.samza_metric_reporter import SamzaMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_prod_eet"

# retry 4 times if any region node gets de-registered from DNS
KAFKA_BOOTSTRAP_SERVERS = [
    "kafka-eet.us-east-1.backend-production.optimizely:9094"
] * 4


def main():
    reporter = SamzaMetricReporter(CONSUMER_GROUP_ID, KAFKA_BOOTSTRAP_SERVERS, 'prod_eet.')
    reporter.run()

if __name__ == "__main__":
    sys.exit(main())
