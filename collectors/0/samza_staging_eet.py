#!/usr/bin/python
import sys

from collectors.lib.samza_metric_reporter import SamzaMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_staging_eet"

KAFKA_BOOTSTRAP_SERVERS = [
    "1.kafka-eet.us-east-1.backend-staging.optimizely:9094",
    "2.kafka-eet.us-east-1.backend-staging.optimizely:9094",
    "3.kafka-eet.us-east-1.backend-staging.optimizely:9094",
    "4.kafka-eet.us-east-1.backend-staging.optimizely:9094",
    "5.kafka-eet.us-east-1.backend-staging.optimizely:9094",
]


def main():
    reporter = SamzaMetricReporter(CONSUMER_GROUP_ID, KAFKA_BOOTSTRAP_SERVERS, 'staging_eet.')
    reporter.run()

if __name__ == "__main__":
    sys.exit(main())
