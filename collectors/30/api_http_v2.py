#!/usr/bin/env python
import time
import requests
import sys

from collectors.lib.optimizely_utils import format_tsd_key, get_json

# Constants
TIME = int(time.time())
URL = 'http://127.0.0.1:8081/metrics'
METRIC_PREFIX = 'optimizely.codahale.'

def main():
    json = get_json(URL)
    metric_types = ['timers', 'meters', 'counters', 'gauges', 'histograms']
    not_metrics = ['duration_units', 'rate_units', 'units']
    for metric_type in metric_types:
        for metric, metrics in json[metric_type].iteritems():
            class_name = None
            split_segs = metric.split(".")
            method_name = "." + split_segs[-1]
            if len(split_segs) > 1:
                if split_segs[0].startswith("results-"):
                    class_name = split_segs[0].split("-")[1]
                elif (len(split_segs) > 2 and split_segs[0] == "com" and split_segs[1] == "optimizely"):
                    class_name = ".".join(split_segs[:-1])

            for metric, value in metrics.iteritems():
                if metric in not_metrics:
                    continue
                print format_tsd_key(METRIC_PREFIX + metric_type + method_name,
                        value, TIME, {'class': class_name} if class_name else {})

if __name__ == '__main__':
    main()
