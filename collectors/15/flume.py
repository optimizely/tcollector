#!/usr/bin/python

"""
    flume stats collector

Connect to flume agents over http and gather metrics
and make them suitable for OpenTSDB to consume

Need to config flume-ng to spit out json formatted metrics over http
See http://flume.apache.org/FlumeUserGuide.html#json-reporting

Tested with flume-ng 1.4.0 only. So far

Based on the elasticsearch collector

"""

import errno
import httplib
try:
  import json
except ImportError:
  json = None  # Handled gracefully in main.  Not available by default in <2.6
import socket
import sys
import time

from collectors.lib import utils

try:
  from collectors.etc import flume_conf
except ImportError:
  flume_conf = None

DEFAULT_TIMEOUT = 10.0    # seconds
FLUME_HOST = "localhost"
FLUME_PORT = 34545

# Exclude values that are not really metrics and totally pointless to keep track of
EXCLUDE = ['StartTime', 'StopTime', 'Type']

def err(msg):
  print >>sys.stderr, msg

class FlumeError(RuntimeError):
  """Exception raised if we don't get a 200 OK from Flume webserver."""
  def __init__(self, resp):
    RuntimeError.__init__(self, str(resp))
    self.resp = resp

def request(server, uri):
  """Does a GET request of the given uri on the given HTTPConnection."""
  server.request("GET", uri)
  resp = server.getresponse()
  if resp.status != httplib.OK:
    raise FlumeError(resp)
  return json.loads(resp.read())


def flume_metrics(server):
  return request(server, "/metrics")

def main(argv):
  if not (flume_conf and flume_conf.enabled() and flume_conf.get_settings()):
    # Status code 13 tells the parent tcollector not to respawn this collector
    return 13

  settings = flume_conf.get_settings()

  if (settings['default_timeout']):
    DEFAULT_TIMEOUT = settings['default_timeout']

  if (settings['flume_host']):
    FLUME_HOST = settings['flume_host']

  if (settings['flume_port']):
    FLUME_PORT = settings['flume_port']

  utils.drop_privileges()
  socket.setdefaulttimeout(DEFAULT_TIMEOUT)
  server = httplib.HTTPConnection(FLUME_HOST, FLUME_PORT)
  try:
    server.connect()
  except:
    # Nothing really wrong if the Flume server is unavailable, we should just try again next time.
    return 0

  if json is None:
    err("This collector requires the `json' Python module.")
    return 1

  def printmetric(component, metric, value, **tags):
    if tags:
      tags = " " + " ".join("%s=%s" % (name, value)
                            for name, value in tags.iteritems())
    else:
      tags = ""
    print ("flume.%s.%s %d %s %s" % (component, metric, ts, value, tags))

  # Get the metrics
  ts = int(time.time())  # In case last call took a while.
  stats = flume_metrics(server)

  for component in stats:
    (component_type, name) = component.split(".")
    tags = {"type": name}
    for metric, value in stats[component].items():
      if metric not in EXCLUDE:
        printmetric(component_type.lower(), metric, value, **tags)
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv))
