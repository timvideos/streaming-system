#! /usr/bin/python
# vim: set ts=4 sw=4 et sts=4 ai:

import requests
import pprint
import sys
import hashlib
import cStringIO as StringIO
import re
import time

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
}

if CONFIG['config']['schedule-format'] != 'symposion':
    print ('Schedule format must be `symposion` (was actually: %r)' % CONFIG['config']['schedule-format'])
    sys.exit(1)

URL = CONFIG['config']['schedule']


# Make pretty-print output a valid python string for UTC timezone object.
def utc__repr__(self):
    return "pytz.utc"
pytz.utc.__class__.__repr__ = utc__repr__


defaulttime = datetime.now(pytz.timezone(CONFIG['config']['schedule-timezone']))
convert = markdown.Markdown().convert


ONE_DAY = timedelta(days=1)

if __name__ == "__main__":
    req = requests.get(URL)
    if req.status_code != 200:
        print ('got non-200 status code from server (%d)' % req.status_code)
        sys.exit(1)
    incoming_data = req.json()

    # Resort into
    # <room>: (start, end) : <data>

    outgoing_data = {}
    for item in incoming_data['schedule']:
        if 'kind' in item and item['kind'] not in ('plenary', 'talk'):
            continue


        room = item['room'].strip()
        channel = ROOM_MAP.get(room, None)
        if not channel:
            continue
        if channel not in outgoing_data:
            outgoing_data[channel] = {}

        outitem = {}

        outitem['start'] = parser.parse(item['start'], default=defaulttime)
        if 'end' in item:
            outitem['end'] = parser.parse(item['end'], default=defaulttime)


        if 'conf_url' in item and item['conf_url']:
            outitem['url'] = item['conf_url']
        else:
            outitem['url'] = None

        name = '%s - %s' % (item['kind'], item['name'])
        
        if item['kind'] in ('talk', 'tutorial'):
            if item['name'] == 'Slot':
                # Empty position in the schedule
                continue
            # Only show the name
            name = item['name']
        
        if item['name'] == 'Slot':
            name = item['kind']
            
        if name == 'Keynote':
            outitem['title'] = "%s: %s" % (name, ', '.join(item['authors']))
        else:
            outitem['title'] = name

        if 'abstract' in item:
            outitem['abstract'] = convert(item['abstract'])
        else:
            outitem['abstract'] = ''

        outitem['guid'] = item['conf_key']

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

            if end.date() != start.date():
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

                # Fill in blank days
                current = end + ONE_DAY
                while current.date() != start.date():
                    newdata = {
                        'start': current.replace(hour=0, minute=0, second=0),
                        'end': current.replace(hour=23, minute=59, second=59),
                        'title': 'Nothing scheduled',
                        'abstract': '',
                        'guid': hashlib.md5(str(current)+channel).hexdigest(),
                        'generated': True,
                        }
                    final_data[channel].append(newdata)
                    current = current + ONE_DAY

                newdata = {
                    'start': start.replace(hour=0, minute=0, second=0),
                    'end': start,
                    'title': 'Not yet started',
                    'abstract': '',
                    'guid': hashlib.md5(str(start)+channel).hexdigest(),
                    'generated': True,
                    }
                final_data[channel].append(newdata)
                end = newdata['end']

            delta = (start - end).total_seconds()/60
            if delta and delta <= 10:
                final_data[channel][-1]['end'] = final_data[channel][-1]['end']+timedelta(seconds=delta*60)
            elif delta:
                title = BREAK_NAMES.get(delta, 'Unscheduled')

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
