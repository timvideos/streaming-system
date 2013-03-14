
import simplejson
import pprint
import sys
import hashlib
import cStringIO as StringIO

import urllib2

from datetime import datetime, timedelta
import pytz
from dateutil import parser

import markdown

ROOM_MAP = {
    'Grand Ballroom AB': 'ab',
    'Grand Ballroom CD': 'cd',
    'Grand Ballroom EF': 'ef',
    'Grand Ballroom GH': 'gh',
    'Great America':  'america',
    'Great America Floor 2B R1': 'america',
    'Great America Floor 2B R2': 'america',
    'Great America Floor 2B R3': 'america',
    'Great America K': 'america',
    'Great America J': 'america',
#    'Great America K': 'america',
    'Mission City': 'mission',
    'Mission City M1': 'mission',
    'Mission City M2': 'mission',
    'Mission City M3': 'mission',
}

BREAK_NAMES = {
    10: None,
    60: 'Lunch',
    40: 'Morning Break',
    30: ['Morning Break', 'Afternoon Break'],
    190: 'Poster Session',
    920: None,
}

tz = pytz.timezone('US/Pacific')
class tzinfo(tz.__class__):
    def __repr__(self):
         return 'pytz.timezone("US/Pacific")'
    __str__ = __repr__
tz.__class__ = tzinfo

defaulttime = datetime.now(tz)
convert = markdown.Markdown().convert

if __name__ == "__main__":
    incoming_json = urllib2.urlopen("https://us.pycon.org/2013/schedule/conference.json").read()
    incoming_data = simplejson.loads(incoming_json)

    # Resort into
    # <room>: (start, end) : <data>
 
    outgoing_data = {}
    while len(incoming_data) > 0:
        item = incoming_data.pop(0)
        if item['kind'] not in ('plenary', 'talk'):
            continue

        if len(item['room'].split(',')) > 1:
            for otherroom in item['room'].split(','):
               otherroom = otherroom.strip()
               if otherroom == "Mission City":
                   continue
               newitem = dict(item)
               newitem['name'] = "Change to Mission for <b>%s</b>" % newitem['name']
               newitem['abstract'] = ''
               newitem['room'] = otherroom
               newitem['abstract'] = ''
               newitem['conf_url'] += '?'
               incoming_data.insert(0, newitem)

            room = 'Mission City'
        else:
            room = item['room'].strip()

        channel = ROOM_MAP.get(room, None)
        if not channel:
            print room, channel
            continue
        if channel not in outgoing_data:
            outgoing_data[channel] = {}

        outitem = {}

        outitem['start'] = parser.parse(item['start'], default=defaulttime)
        outitem['end'] = parser.parse(item['end'], default=defaulttime)

        outitem['url'] = item['conf_url']

        if item['name'] == 'Keynote':
            outitem['title'] = "%s: <b>%s</b>" % (item['name'], item['authors'][0])
        else:
            outitem['title'] = item['name']
        outitem['abstract'] = convert(item['abstract'])

        outitem['guid'] = hashlib.md5(item['conf_url']).hexdigest()

	outgoing_data[channel][(outitem['start'], outitem['end'])] = outitem

    # Fill in the breaks
    final_data = {}
    for channel in outgoing_data.keys():
        final_data[channel] = []
        channel_data = list(sorted(outgoing_data[channel].items()))

	newdata = {
	    'start': datetime.fromtimestamp(0, defaulttime.tzinfo),
	    'end': channel_data[0][0][0],
	    'title': '<i>Not Yet Started</i>',
	    'abstract': '',
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
                    'title': '<i>Finished for the day</i>',
                    'abstract': '',
                    'guid': hashlib.md5(str(end)+channel).hexdigest(),
                    }
                final_data[channel].append(newdata)

                newdata = {
                    'start': start.replace(hour=0, minute=0, second=0),
                    'end': start,
                    'title': '<i>Not yet started</i>',
                    'abstract': '',
                    'guid': hashlib.md5(str(start)+channel).hexdigest(),
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
                        'title': "<i>%s</i>" % title, 
                        'abstract': '',
                        'guid': hashlib.md5(str(start)+channel).hexdigest(),
                        }
                    final_data[channel].append(newdata)
            final_data[channel].append(data)
            end = data['end']

	newdata = {
	    'start': end,
            'end': end.replace(year=2100),
	    'title': '<i>Conference Finished :(</i>',
	    'abstract': '',
            'guid': hashlib.md5(str(end)+channel).hexdigest(),
	    }
        final_data[channel].append(newdata)

    for channel in final_data.keys():
        sys.stderr.write('\n%s\n' % channel)
        for value in final_data[channel]:
            value['start'] = str(value['start'])
            value['end'] = str(value['end'])
            sys.stderr.write("%s | %s | %s\n" % (value['start'], value['end'], value['title']))

    out = StringIO.StringIO()
    pprint.pprint(final_data, stream=out)
    print """\
import datetime
import pytz

data = \\"""
    print out.getvalue().replace("<DstTzInfo 'US/Pacific' PDT-1 day, 17:00:00 DST>", 'pytz.timezone("US/Pacific")')
