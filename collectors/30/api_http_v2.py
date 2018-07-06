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
    res_pattern = re.compile(r"results-(\w+)")
    metric_types = ['timers', 'meters', 'counters', 'gauges', 'histograms']
    not_metrics = ['duration_units', 'rate_units', 'units']
    for metric_type in metric_types:
        for metric, metrics in json[metric_type].iteritems():
            metric_name = "." + metric
            class_name = None
            match = res_pattern.search(metric)
            if match:
                    metric_name = '.' + re.sub(res_pattern, "resultsMode", metric)
                    class_name = match.group(1)
            
            for metric, value in metrics.iteritems():
                if metric in not_metrics:
                    continue
                print format_tsd_key(METRIC_PREFIX + metric_type + metric_name + '.' + metric,
                        value, TIME, {'class': class_name} if class_name else {})

if __name__ == '__main__':
    main()
