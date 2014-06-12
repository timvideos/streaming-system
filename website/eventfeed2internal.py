#! /usr/bin/python
# vim: set ts=4 sw=4 et sts=4 ai:

"""
This tool generates the data.py file needed by the system.

This file is in the following format:
    import datetime
    import pytz

    data = \
    // Dictionary of GROUP to sorted list of all events for that group.
    {'GROUP1' : [
       // Sorted list of all events in that group.
       {'abstract': 'Long description of event proceedings',
        'end': 'End time in YYYY-MM-DD HH:MM:SS in UTC',
        'start': 'Start time in YYYY-MM-DD HH:MM:SS in UTC',
        'title': 'Short title for event proceedings',
        'url': 'URL for details to link too.'},
       {...},
       {...}],
     'GROUP2': []
    }




"""

import cStringIO as StringIO
import hashlib
import os
import pprint
import pytz
import simplejson
import sys
import sys
import urllib2

from collections import defaultdict
from datetime_tz import datetime_tz, timedelta, iterate as dt_iterate

config_path = os.path.realpath(os.path.dirname(__file__)+"..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()

# Make pretty-print output a valid python string for UTC timezone object.
def utc__repr__(self):
    return "pytz.utc"

pytz.utc.__class__.__repr__ = utc__repr__



url_cache = {}
def get_schedule_json(url, tzinfo=None):
    if not url in url_cache:
        sys.stderr.write("Downloading %s\n" % url)
        url_json = urllib2.urlopen(url).read()

        url_data = simplejson.loads(url_json)

        # Convert the time/date values into datetime objects
        for room in url_data:
            for item in url_data[room]:
                for value in item:
                    if value not in ('start', 'end',):
                        continue

                    dt = datetime_tz.smartparse(item[value], tzinfo)
                    item[value] = dt.astimezone(pytz.utc)

                # If no end time, generate one from start+duration...

        url_cache[url] = url_data

    return url_cache[url]


def print_schedule(conference_schedules):
    for conference in conference_schedules:
        sys.stderr.write("\n\n%s\n" % conference)
        sys.stderr.write("========================================================\n")
        for channel in conference_schedules[conference]:
            config = CONFIG.config(channel)

            tzinfo = pytz.utc
            if config['schedule-timezone']:
               tzinfo = pytz.timezone(config['schedule-timezone'])

            sys.stderr.write('\n%s\n' % channel)
            for item in conference_schedules[conference][channel]:
                start = str(item['start'].astimezone(tzinfo))
                end = str(item['end'].astimezone(tzinfo))
                sys.stderr.write(("%s | %s | %s\n" % (start, end, item['title'][:50])).encode('utf-8'))


def main(argv):
    conference_schedules = defaultdict(dict)

    # Download the schedule details for each channel and group into
    # conferences.
    for channel in CONFIG.groups():
        config = CONFIG.config(channel)

    	if 'schedule' not in config or not config['schedule']:
            sys.stderr.write("Channel %s doesn't have a schedule.\n" % channel)
            continue

        tzinfo = None
        if config['schedule-timezone']:
            tzinfo = pytz.timezone(config['schedule-timezone'])

        channel_schedule = get_schedule_json(config['schedule'], tzinfo)
        if config['schedule-key'] not in channel_schedule:
            raise IOError()

        conference = config['group']
        if config['conference']:
            conference = config['conference']

        schedule = []
        for schedule_key in [config['schedule-key']] + config['schedule-see-also']:
            for item in channel_schedule[schedule_key]:
                if item['title'] in ("miniconf schedules to be determined",):
                    continue

                data = {
                    'start': item['start'],
                    'end': item['end'],
                    'title': item['title'],
                    'abstract': item['abstract'],
                    'url': '',
                    }

                if 'url' in item:
                    data['url'] = item['url']

                if schedule_key == 'uncatered':
                    data['via'] = schedule_key
                    data['title'] = "Lunch Break"
                elif schedule_key != config['schedule-key']:
                    data['via'] = schedule_key
                    data['title'] = "Move to %s for %s" % (schedule_key, item['title'])

                schedule.append(data)

        schedule.sort(key=lambda i: i['start'])
        conference_schedules[conference][channel] = schedule

    # Fill in day start / day end events for each conference day.
    # (We need to work in the schedule's timezone for this to work properly.)
    for conference in conference_schedules:
        # First earliest and latest event in a conference.
        all_events = []
        for channel_schedule in conference_schedules[conference].values():
            all_events.extend(channel_schedule)
        all_events.sort(key=lambda i: i['start'])

        starting_event = all_events[0]
        ending_event = all_events[-1]

        for channel in conference_schedules[conference]:
            oldevents = conference_schedules[conference][channel]

            config = CONFIG.config(channel)
            if not config['schedule-timezone']:
                sys.stderr.write("%s has not timezone, can't add conference day events\n" % channel)
                continue
            tzinfo = pytz.timezone(config['schedule-timezone'])

            # Group events onto days
            perday_events = defaultdict(list)
            for event in oldevents:
                perday_events[event['end'].astimezone(tzinfo).date()].append(event)

            # Remove any days which are 100% via another schedule.
            for day in list(perday_events.keys()):
                for event in perday_events[day]:
                    if not event.get('via', False):
                        break
                else:
                    # All generated
                    del perday_events[day]

            # Add in any missing days
            startdate = datetime_tz.combine(
                starting_event['start'].astimezone(tzinfo).date(),
                datetime_tz.min.time(),
                tzinfo)
            enddate = datetime_tz.combine(
                ending_event['start'].astimezone(tzinfo).date(),
                datetime_tz.min.time(),
                tzinfo)
            for day in dt_iterate.days(startdate, enddate):
                if day.date() not in perday_events:
                    day_skipped_event = {
                        'start': datetime_tz.combine(day, datetime_tz.min.time(), tzinfo).astimezone(pytz.utc),
                        'end': datetime_tz.combine(day, datetime_tz.max.time(), tzinfo).astimezone(pytz.utc),
                        'title': '<i>Nothing in %s today</i>' % config['title'],
                        'abstract': '',
                        'generated': True,
                        }

                    perday_events[day.date()].append(day_skipped_event)

            # Add start of day / end of day events
            for day, events in perday_events.items():
                if day > startdate.date() and events[0]['start'].astimezone(tzinfo).time() != datetime_tz.min.time():
                    events.insert(0, {
                        'start': datetime_tz.combine(day, datetime_tz.min.time(), tzinfo).astimezone(pytz.utc),
                        'end': events[0]['start'],
                        'title': '<i>Not yet started in %s</i>' % config['title'],
                        'abstract': '',
                        'generated': True,
                        })

                if day < enddate.date() and events[-1]['end'].astimezone(tzinfo).time() != datetime_tz.max.time():
                    events.append({
                        'start': events[-1]['end'],
                        'end': datetime_tz.combine(day, datetime_tz.max.time(), tzinfo).astimezone(pytz.utc),
                        'title': '<i>Finished for the day in %s</i>' % config['title'],
                        'abstract': '',
                        'generated': True,
                        })

            # Create a before conference start event.
            before_event = {
                'start': datetime_tz(datetime_tz.min.asdatetime(naive=True), tzinfo).astimezone(pytz.utc),
                'end': starting_event['start'],
                'title': '<i>%s not yet started</i>' % conference,
                'abstract': '',
                'generated': True,
                }
            # Create an after conference end event.
            after_event = {
                'start': ending_event['end'],
                'end': datetime_tz(datetime_tz.max.asdatetime(naive=True), tzinfo).astimezone(pytz.utc),
                'title': '<i>%s finished :(</i>' % conference,
                'abstract': '',
                'generated': True,
                }

            # Put everything back together
            newevents = [before_event]
            for day in sorted(perday_events.keys()):
                newevents.extend(perday_events[day])
            newevents.append(after_event)

            conference_schedules[conference][channel] = newevents

    # Fill in any gaps
    for conference in conference_schedules:
        for channel in conference_schedules[conference]:
            oldevents = conference_schedules[conference][channel]

            newevents = [oldevents.pop(0)]
            conference_schedules[conference][channel] = newevents

            while len(oldevents) > 0:
                delta = oldevents[0]['start'] - newevents[-1]['end']

                if delta.seconds > (5*60):
                    unknown_event = {
                        'start': newevents[-1]['end'],
                        'end': oldevents[0]['start'],
                        'abstract': '',
                        'generated': True,
                        }
                    unknown_event['title'] = '<i>%i minute break</i>' % ((unknown_event['end'] - unknown_event['start']).seconds/60)
                    newevents.append(unknown_event)
                newevents.append(oldevents.pop(0))

    # Add guid to each event
    for conference in conference_schedules:
        for channel in conference_schedules[conference]:
            for item in conference_schedules[conference][channel]:
                if 'guid' not in item:
                    item['guid'] = hashlib.md5(str(item['start'])+channel).hexdigest()

    print_schedule(conference_schedules)

    output_data = {}
    for conference in conference_schedules:
        for channel in conference_schedules[conference]:
            output_data[channel] = conference_schedules[conference][channel]

    out = StringIO.StringIO()
    pprint.pprint(output_data, stream=out)
    print """\
from datetime_tz import datetime_tz
import pytz

data = \\"""
    print out.getvalue()

if __name__ == "__main__":
    import sys
    main(sys.argv)
