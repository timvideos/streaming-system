#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Connect to the streamti.me server and report our stats."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"

import datetime
import simplejson
import time
import urllib
import urllib2

if __name__ == "__main__":
    while True:
        data = {
            "overall_clients": 0,
            "overall_bitrate": 0,
            "overall_cbitrate": 0,
            }
        totals = [('ogg_high', 4, 1e6, 2e6)]
        for name, clients, bitrate, streambitrate in totals:
            fixed_name = name.replace('http-', '').replace('-', '_')
            data[fixed_name+"_clients"] = int(clients)
            data[fixed_name+"_bitrate"] = float(bitrate)
            data[fixed_name+"_cbitrate"] = float(bitrate)
            data["overall_clients"] += clients
            data["overall_bitrate"] += bitrate
            data["overall_cbitrate"] += clients*streambitrate

        try:
            r = urllib2.urlopen(
                'http://localhost:8000/tracker/endpoint/register',
                urllib.urlencode((
                    ('secret', 'publiclyknown'),
                    ('group', 'av'),
                    ('data', simplejson.dumps(data)),
                    ))
                )
        except urllib2.HTTPError, e:
            print e
            print e.read()
            raise
        print "Registered at", datetime.datetime.now(), "result", r.read().strip(),
        print 'clients:', data['overall_clients'],
        print 'bitrate:', data['overall_bitrate'],
        print "(%s %s)" % (data['overall_bitrate']/1e6, 'megabits/second'),
        print 'theory:', data['overall_bitrate']/1e6, 'megabits/second'

        time.sleep(1)
