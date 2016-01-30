#! /usr/bin/python
# vim: set ts=4 sw=4 et sts=4 ai:

import json
import pprint
import sys
import hashlib
import cStringIO as StringIO
import re
import time

import urllib2

from datetime import datetime, timedelta
import pytz
from dateutil import parser

import markdown

import os
config_path = os.path.realpath(os.path.dirname(__file__)+"..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()

ROOM_MAP = dict((CONFIG.config(g)['schedule-key'], g) for g in CONFIG.groups() if CONFIG.config(g)['schedule-key'])
BREAK_NAMES = {
    10: None,
    60: 'Lunch',
    40: 'Morning Break',
    30: ['Morning Break', 'Afternoon Break'],
    90: 'Lunch Break',
    190: 'Poster Session',
    920: None,
    1080: None,
    1020: None,
}

assert CONFIG['config']['schedule-format'] == 'pycon'
URL = CONFIG['config']['schedule-url']


# Make pretty-print output a valid python string for UTC timezone object.
def utc__repr__(self):
    return "pytz.utc"
pytz.utc.__class__.__repr__ = utc__repr__


defaulttime = datetime.now(pytz.timezone(CONFIG['config']['schedule-timezone']))
convert = markdown.Markdown().convert


def tolower(d):
    newd = {}
    for key, value in d.items():
        if type(value) is dict:
            value = tolower(value)
        newd[key.lower()] = value
    return newd


def parse_duration(s):
    bits = re.split('[^0-9]+', s)
    if len(bits) == 2:
        return timedelta(hours=int(bits[0]), minutes=int(bits[1]))
    elif len(bits) == 3:
        return timedelta(hours=int(bits[0]), minutes=int(bits[1]), seconds=int(bits[2]))


if __name__ == "__main__":
    incoming_json = urllib2.urlopen(URL).read()
    incoming_data = json.loads(incoming_json)

    # Resort into
    # <room>: (start, end) : <data>

    outgoing_data = {}
    while len(incoming_data) > 0:
        item = tolower(incoming_data.pop(0))
        if 'kind' in item and item['kind'] not in ('plenary', 'talk'):
            continue

        roomkey = 'room'
        if roomkey not in item:
            roomkey = 'room name'

        namekey = 'name'
        if namekey not in item:
            namekey = 'title'

        room = item[roomkey].strip()
        channel = ROOM_MAP.get(room, None)
        if not channel:
            continue
        if channel not in outgoing_data:
            outgoing_data[channel] = {}

        outitem = {}

        outitem['start'] = parser.parse(item['start'], default=defaulttime)
        if 'end' in item:
            outitem['end'] = parser.parse(item['end'], default=defaulttime)
        else:
            outitem['end'] = outitem['start'] + parse_duration(item['duration'])

        if 'conf_url' in item and item['conf_url']:
            outitem['url'] = item['conf_url']
        else:
            outitem['url'] = str(time.time())

        if item[namekey] == 'Keynote':
            outitem['title'] = "%s: %s" % (item[namekey], item['authors'][0])
        else:
            outitem['title'] = item[namekey]

        if 'abstract' in item:
            outitem['abstract'] = convert(item['abstract'])
        else:
            outitem['abstract'] = ''

        outitem['guid'] = hashlib.md5(outitem['url']).hexdigest()

        outgoing_data[channel][(outitem['start'], outitem['end'])] = outitem

    # Fill in the breaks
    final_data = {}
    for channel in outgoing_data.keys():
        final_data[channel] = []
        channel_data = list(sorted(outgoing_data[channel].items()))

        newdata = {
            'start': datetime.fromtimestamp(0, defaulttime.tzinfo),
            'end': channel_data[0][0][0],
            'title': 'Not Yet Started',
            'abstract': '',
            'generated': True,
            }
        final_data[channel].append(newdata)

        end = channel_data[0][0][0]
        while len(channel_data) > 0:
            (start, _), data = channel_data.pop(0)

            if end.day != start.day:
                # Insert start / end time
                newdata = {
                    'start': end,
                    'end': end.replace(hour=23, minute=59, second=59),
                    'title': 'Finished for the day',
                    'abstract': '',
                    'guid': hashlib.md5(str(end)+channel).hexdigest(),
                    'generated': True,
                    }
                final_data[channel].append(newdata)

                newdata = {
                    'start': start.replace(hour=0, minute=0, second=0),
                    'end': start,
                    'title': 'Not yet started',
                    'abstract': '',
                    'guid': hashlib.md5(str(start)+channel).hexdigest(),
                    'generated': True,
                    }
                final_data[channel].append(newdata)

            delta = (start - end).seconds/60
            if delta and delta == 10:
                final_data[channel][-1]['end'] = final_data[channel][-1]['end']+timedelta(seconds=delta*60)
            elif delta:
                title = BREAK_NAMES.get(delta, 'Unknown %s' % delta)

                if title is not None:
                    if len(title) == 2:
                        title = title[start.hour >= 12]
                    newdata = {
                        'start': end,
                        'end': start,
                        'title': "%s" % title,
                        'abstract': '',
                        'guid': hashlib.md5(str(start)+channel).hexdigest(),
                        'generated': True,
                        }
                    final_data[channel].append(newdata)
            final_data[channel].append(data)
            end = data['end']

        newdata = {
            'start': end,
            'end': end.replace(year=2100),
            'title': 'Conference Finished :(',
            'abstract': '',
            'guid': hashlib.md5(str(end)+channel).hexdigest(),
            'generated': True,
            }
        final_data[channel].append(newdata)

    for channel in final_data.keys():
        sys.stderr.write('\n%s\n' % channel)
        for value in final_data[channel]:
            sys.stderr.write("%s | %s | %s\n" % (str(value['start']), str(value['end']), value['title']))
            value['start'] = value['start'].astimezone(pytz.utc)
            value['end'] = value['end'].astimezone(pytz.utc)

    out = StringIO.StringIO()
    pprint.pprint(final_data, stream=out)
    print """\
import datetime
import pytz

data = \\"""
    print out.getvalue().replace("<DstTzInfo 'US/Pacific' PDT-1 day, 17:00:00 DST>", 'pytz.timezone("US/Pacific")')
