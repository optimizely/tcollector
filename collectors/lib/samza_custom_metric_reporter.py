import cProfile
import sys
import re

from samza_metric_reporter import SamzaMetricReporter

class SamzaCustomMetricReporter(SamzaMetricReporter):

    """
    This reporter only prints custom samza jobs related metrics. All
    generic Samza metrics, such as number of messages processed,
    are reported by SamzaMetricReporter.
    """

    def __init__(self, consumer_group_id, kafka_bootstrap_servers, depth_range=None, kafka_metrics_topic='samza_metrics'):
        SamzaMetricReporter.__init__(self, consumer_group_id, kafka_bootstrap_servers, kafka_metrics_topic=kafka_metrics_topic)
        self.depth_range = depth_range
        self.methods_to_run = [self.report_samza_custom_metrics]

    def report_samza_custom_metrics(self, metrics_raw, header_raw):
        for class_name, class_metrics in metrics_raw.iteritems():
            tags = self.create_standard_tags(header_raw)
            ts = int(header_raw['time'] / 1000)
            tags['source'] = self.sanitize(header_raw['source'])
            metric_name  = self.convert_class_to_metric_name(class_name)
            if not metric_name:
                continue

            self.print_metrics(metric_name, ts, class_metrics, tags)

            sys.stdout.flush()

    def print_metrics(self, name, ts, value, tags):
        if type(value) is dict:
            for k, v in value.iteritems():
                self.print_metrics("{}.{}".format(name, k), ts, v, tags)
        elif self.is_number(value):
            if self.depth_range and name.count('.') not in self.depth_range:
                return
            print self.sanitize(name), ts, value, self.to_tsdb_tag_str(tags)

    def convert_class_to_metric_name(self, class_name):
        # generic func to extract metric_name_string from class_name, compatible with exsiting mapping like
        #  'com.optimizely.sessionization.samza.SessionizationTask' : 'sessionization.metrics',
        #  'com.optimizely.preprocessing.samza.enrichevent.EnrichProjectIdTask' : 'enrichevents.metrics',
        #  'com.optimizely.preprocessing.samza.enrichevent.processor.EventTicketProjectIdProcessor' : 'enrichevents.metrics',
        #  'com.optimizely.preprocessing.samza.enrichevent.processor.DecisionEventTicketProjectIdProcessor' : 'enrichevents.metrics',
        #  'com.optimizely.validator.samza.ValidatorTask': 'validator.metrics',
        #  'com.optimizely.achievement.samza.AchievementTask': 'achievement.metrics',

        match = re.match('^com\.optimizely\.([a-z]+)\.samza\.', class_name)
        if not match:
            return None

        metric_name = match.group(1)

        # Exception: 'com.optimizely.preprocessing.samza.enrichevent.EnrichProjectIdTask' -> 'enrichevents.metrics'
        if metric_name == 'preprocessing':
            metric_name = 'enrichevents'

        return metric_name + '.metrics'
