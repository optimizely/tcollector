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
            splitpath = metric.split(".")
            if len(splitpath) == 0:
                continue
            elif len(splitpath) == 1:
                class_name = splitpath[0]
                suffix = "." + class_name
            elif len(splitpath) > 1:
                class_name = ".".join(splitpath[:-1])
                method_name = splitpath[-1]
                suffix = "." + class_name + "." + method_name

            for metric, value in metrics.iteritems():
                if metric in not_metrics:
                    continue
                print format_tsd_key(METRIC_PREFIX + metric_type + suffix,
                        value, TIME, {'class': class_name})

if __name__ == '__main__':
    main()
