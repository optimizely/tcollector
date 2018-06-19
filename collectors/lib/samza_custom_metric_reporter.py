import sys
import re

from samza_metric_reporter import SamzaMetricReporter

class SamzaCustomMetricReporter(SamzaMetricReporter):

    """
    This reporter only prints custom samza jobs related metrics. All
    generic Samza metrics, such as number of messages processed,
    are reported by SamzaMetricReporter.
    """

    def __init__(self, consumer_group_id, kafka_bootstrap_servers, kafka_metrics_topic='samza_metrics'):
        SamzaMetricReporter.__init__(self, consumer_group_id, kafka_bootstrap_servers, kafka_metrics_topic)
        self.methods_to_run = [self.report_samza_custom_metrics]

    def report_samza_custom_metrics(self, metrics_raw, header_raw):
        for class_name, metric in metrics_raw.iteritems():
            tags = self.create_standard_tags(header_raw)
            ts = int(header_raw['time'] / 1000)
            tags['source'] = self.sanitize(header_raw['source'])
            metric_name_string = self.convert_class_to_metric_name(class_name)
            if not metric_name_string:
                continue

            for metric_name, metric_val in metric.iteritems():
                self.print_metrics(
                    metric_name,
                    ts,
                    metric_val,
                    tags,
                    metric_name_string)

            sys.stdout.flush()

    def print_metrics(self, metric_name, ts, value, tags, metric_name_string):
        if self.is_number(value):
            print("%s.%s %d %s %s" % (metric_name_string, metric_name, ts, value, self.to_tsdb_tag_str(tags)))


    def convert_class_to_metric_name(self, class_name):
        # generic func to extract metric_name_string from class_name, compatible with exsiting mapping like
        #  'com.optimizely.sessionization.samza.SessionizationTask' : 'sessionization.metrics',
        #  'com.optimizely.preprocessing.samza.enrichevent.EnrichProjectIdTask' : 'enrichevents.metrics',
        #  'com.optimizely.preprocessing.samza.enrichevent.processor.EventTicketProjectIdProcessor' : 'enrichevents.metrics',
        #  'com.optimizely.preprocessing.samza.enrichevent.processor.DecisionEventTicketProjectIdProcessor' : 'enrichevents.metrics',
        #  'com.optimizely.validator.samza.ValidatorTask': 'validator.metrics',
        #  'com.optimizely.achievement.samza.AchievementTask': 'achievement.metrics',

        match = re.match('^com\.optimizely\.([a-z]+)\.samza\.\w+\.{0,1}', class_name)
        if not match:
            return None

        metric_name = match.group(1)

        # Exception: 'com.optimizely.preprocessing.samza.enrichevent.EnrichProjectIdTask' -> 'enrichevents.metrics'
        if metric_name == 'preprocessing':
            metric_name = 'enrichevents'

        return metric_name + '.metrics'
