#!/usr/bin/python
from multiprocessing import Process
import sys

from collectors.lib.samza_custom_metric_reporter import SamzaCustomMetricReporter

CONSUMER_GROUP_ID = "tcollector_samza_custom_metric_prod_eet"

KAFKA_BOOTSTRAP_SERVERS = [
    "kafka-eet.us-east-1.backend-production.optimizely:9094",
]


def main():
    
    reporter_0 = SamzaCustomMetricReporter(CONSUMER_GROUP_ID, KAFKA_BOOTSTRAP_SERVERS, depth_range=xrange(5))

    reporter_1 = SamzaCustomMetricReporter(CONSUMER_GROUP_ID, KAFKA_BOOTSTRAP_SERVERS, depth_range=xrange(5, 100))
    p = Process(target=reporter_1.run)
    
    p.start()
    reporter_0.run()

    p.join()

if __name__ == "__main__":
    sys.exit(main())
