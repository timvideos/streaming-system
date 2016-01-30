#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Connect to the streamti.me server and report our stats."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"

import datetime
import json
import time
import urllib
import urllib2

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    "--server", help="server to register on", action="store",
    default="http://localhost:8000/tracker/endpoint/register")
parser.add_argument(
    "--secret", help="secret to use to register", action="store",
    default="move me to config.private.json")
parser.add_argument(
    "--group", help="group to register on the server", action="store",
    default="example")
parser.add_argument(
    "--ip", help="IP to pretend to be", action="store",
    default="")

if __name__ == "__main__":
    args = parser.parse_args()

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

        for group in args.group.split(','):
            try:
                req = urllib2.Request(
                    args.server,
                    urllib.urlencode((
                        ('secret', args.secret),
                        ('group', group),
                        ('data', json.dumps(data)),
                        ('REMOTE_ADDR', args.ip),
                        )))
                r = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                print e
                print e.read()
                raise

            print "Registered", group, "at", datetime.datetime.now(), "result", r.read().strip()

        time.sleep(1)
