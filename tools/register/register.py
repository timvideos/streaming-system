#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Connect to the timvideos.us server and report our stats."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"

import datetime
import json
import time
import urllib
import urllib2

from twisted.internet import defer, reactor

from flumotion.common import errors, planet, log
from flumotion.monitor.nagios import util
from flumotion.common.planet import moods

from flumotion.admin.command import common

from flumotion.admin.command import main


def eb(e):
    print e
    reactor.callLater(0, reactor.stop)


class Register(common.AdminCommand):
    description = "Register this encoder on timvideos.us server and report stats."
    usage = "-g [group]"

    def addOptions(self):
        self.parser.add_option('-g', '--group',
            action="store", dest="group",
            help="group this machine is encoding for")

        default = 'http://timvideos.us/tracker/endpoint/register'
        self.parser.add_option('-r', '--register',
            action="store", dest="register_url",
            help="Server to register on. (defaults to %s)" % default,
            default=default)

        self.parser.add_option('-s', '--secret',
            action="store", dest="secret",
            help="Secret that the is shared with the server")

        self.parser.add_option('-f', '--fake',
            action="store", dest="fake",
            help="Don't connect to flumotion, instead just pretend")

        default = 30
        self.parser.add_option('-i', '--interval',
            action="store", dest="interval",
            help="How often to update the system state (defaults to %i)." % default,
            default=default)

    def handleOptions(self, options):
        if not options.group:
            common.errorRaise("Please specify a group your encoding for "
                "with '-g [group]'")
        self.group = options.group

        if not options.secret:
            common.errorRaise("Please specify the shared secret "
                "with '-s [secret]'")
        self.secret = options.secret

        self.register_url = options.register_url
        self.interval = options.interval

        # call our callback after connecting
        if options.fake is not None:
            totals = eval(options.fake)
            while True:
                self.send_update(totals)
                time.sleep(self.interval)
        else:
            self.getRootCommand().loginDeferred.addCallback(self._callback)

    def _callback(self, *args):
        d = self.getRootCommand().medium.callRemote('getPlanetState')
        def gotPlanetStateCb(planetState):
            for f in planetState.get('flows'):
                ds = []
                for component in f.get('components'):
                    name = component.get('name')
                    if not name.startswith('http') or name == 'http-loop':
                        continue

                    def getUIStateCb(uiState, name=name):
                        return (name, int(uiState.get('clients-current')), int(uiState.get('consumption-bitrate-raw')), int(uiState.get('stream-bitrate-raw')))
                    d = self.getRootCommand().medium.componentCallRemote(
                        component, 'getUIState')
                    d.addCallback(getUIStateCb)
                    d.addErrback(eb)
                    ds.append(d)

                d = defer.gatherResults(ds)
                d.addCallback(self.send_update)
                d.addErrback(eb)
                return d

        d.addCallback(gotPlanetStateCb)
        d.addErrback(eb)
        return d

    def send_update(self, totals):
        data = {
            "overall_clients": 0,
            "overall_bitrate": 0,
            "overall_cbitrate": 0,
            }
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
                self.register_url,
                urllib.urlencode((
                    ('secret', self.secret),
                    ('group', self.group),
                    ('data', json.dumps(data)),
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

        # Schedule another register in 30 seconds
        d = defer.Deferred()
        d.addCallback(self._callback)
        d.addErrback(eb)
        reactor.callLater(self.interval, d.callback, ())
        return d


class Command(main.Command):
    description = "Send stats to the timvideos.us server."

    subCommandClasses = [Register]


MYIP = ""

def main(args):
    args = list(args)
    args_a = [args.pop(0)]
    args_b = []

    while len(args) > 0:
        arg = args.pop(0)
        if arg == '-m':
            args_a.append(arg)
            args_a.append(args.pop(0))
        else:
            args_b.append(arg)
    args = args_a + ["register"] + args_b

    c = Command()
    try:
        ret = c.parse(args[1:])
    except common.Exited, e:
        import sys
        ret = e.code
        if ret == 0:
            sys.stdout.write(e.msg + '\n')
        else:
            sys.stderr.write(e.msg + '\n')

    return ret
