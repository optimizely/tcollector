#!/usr/bin/python
import os
import sys

from collectors.lib.samza_custom_metric_reporter import SamzaCustomMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_custom_metric_staging"


def main():
    kafka_bootstrap_servers_csv = os.getenv('KAFKA_BOOTSTRAP_SERVERS_STAGING')
    kafka_bootstrap_servers_eet_csv = os.getenv('KAFKA_BOOTSTRAP_SERVERS_STAGING_EET')

    if kafka_bootstrap_servers_csv:
        kakfa_bootstrap_servers = kafka_bootstrap_servers_csv.split(',')
        reporter = SamzaCustomMetricReporter(CONSUMER_GROUP_ID, kakfa_bootstrap_servers)
        reporter.run()

    if kafka_bootstrap_servers_eet_csv:
        kakfa_bootstrap_servers_eet = kafka_bootstrap_servers_eet_csv.split(',')
        reporter = SamzaCustomMetricReporter(CONSUMER_GROUP_ID, kakfa_bootstrap_servers_eet)
        reporter.run()

if __name__ == "__main__":
    sys.exit(main())
