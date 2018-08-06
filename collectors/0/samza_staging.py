#!/usr/bin/python
import os
import sys

from collectors.lib.samza_metric_reporter import SamzaMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_staging"


def main():
    kafka_bootstrap_servers_csv = os.getenv('KAFKA_BOOTSTRAP_SERVERS_STAGING')
    kafka_bootstrap_servers_eet_csv = os.getenv('KAFKA_BOOTSTRAP_SERVERS_STAGING_EET')

    if kafka_bootstrap_servers_csv:
        kakfa_bootstrap_servers = kafka_bootstrap_servers_csv.split(',')
        reporter = SamzaMetricReporter(CONSUMER_GROUP_ID, kakfa_bootstrap_servers)
        reporter.run()

    # Disabling temporarily until hotspotting is resolved
    # if kafka_bootstrap_servers_eet_csv:
    #     kakfa_bootstrap_servers_eet = kafka_bootstrap_servers_eet_csv.split(',')
    #     reporter = SamzaMetricReporter(CONSUMER_GROUP_ID, kakfa_bootstrap_servers_eet)
    #     reporter.run()

if __name__ == "__main__":
    sys.exit(main())
