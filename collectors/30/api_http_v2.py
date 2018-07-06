#!/usr/bin/env python
import time
import requests
import sys
import re

from collectors.lib.optimizely_utils import format_tsd_key, get_json

# Constants
TIME = int(time.time())
URL = 'http://127.0.0.1:8081/metrics'
METRIC_PREFIX = 'optimizely.codahale.'

def main():
    json = get_json(URL)
    # Matches strings such as results-resultsApi, results-composite
    res_mode_pattern = re.compile(r"results-\w+")
    # Matches strings such as com.optimizely.some.package.MyImpl and places a grouping around the 
    # pacakge and simple class name.
    res_service_pattern = re.compile(r"(com.optimizely(?:\.[a-z]+)+)\.((?:[A-Z][a-z]+)+)")
    metric_types = ['timers', 'meters', 'counters', 'gauges', 'histograms']
    not_metrics = ['duration_units', 'rate_units', 'units']
    for metric_type in metric_types:
        for metric_class, metrics in json[metric_type].iteritems():
            metric_name = "." + metric_class
            class_name = None
            package_name = None
            res_mode_match = res_mode_pattern.match(metric_class)
            res_service_match = res_service_pattern.match(metric_class)

            if res_mode_match:
                metric_name = re.sub(res_mode_pattern, '', metric_class)
                class_name = res_mode_match.group(0)
            elif res_service_match:
                metric_name = re.sub(res_service_pattern, '', metric_class)
                package_name= res_service_match.group(1)
                class_name = res_service_match.group(2)

            for metric, value in metrics.iteritems():
                if metric in not_metrics:
                    continue

                tags = {}
                if (class_name):
                    tags['class'] = class_name
                if (package_name):
                    tags['package'] = package_name

                print format_tsd_key(METRIC_PREFIX + metric_type + metric_name + '.' + metric,
                        value, TIME, tags)

if __name__ == '__main__':
    main()
