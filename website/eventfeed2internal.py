#! /usr/bin/python
# vim: set ts=4 sw=4 et sts=4 ai:

import simplejson
import pprint
import sys
import hashlib
import cStringIO as StringIO

import urllib2

import os
import sys

config_path = os.path.realpath(os.path.dirname(__file__)+"..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()



if __name__ == "__main__":
    rooms = CONFIG.groups()
    incoming_json = urllib2.urlopen("http://lca2014.linux.org.au/programme/schedule/json").read()
    incoming_data = simplejson.loads(incoming_json)

    outgoing_data = {}

    for room in rooms:
        if room in incoming_data:
            outgoing_data[room] = incoming_data[room]

    out = StringIO.StringIO()
    pprint.pprint(outgoing_data, stream=out)
    print """\
import datetime
import pytz

data = \\"""
    print out.getvalue()
