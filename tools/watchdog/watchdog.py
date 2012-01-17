#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Connect to the streamti.me server and report our stats."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"

import datetime
import time
import urllib
import urllib2

from twisted.internet import defer, reactor

from flumotion.admin.command import common
from flumotion.admin.command import main

from flumotion.common import errors, planet, log
from flumotion.common.planet import moods

from flumotion.monitor.nagios import util


class WatchDog(common.AdminCommand):
    description = "Watch Dog the components."
    usage = ""

    def eb(self, e):
        print "error", e
        self.getRootCommand().loginDeferred.unpause()

    def handleOptions(self, options):
        self.getRootCommand().loginDeferred.addCallback(self._callback)

    def restart(self, component):
        print component.get('name'), "- trying to stop"
        def cb(error=None, self=self, component=component):
            print component.get('name'), "- stopped!", ["Error", ""][error != None]
            self.start(component)

        d = self.getRootCommand().medium.callRemote(
            'componentStop', component)
        d.addCallback(cb)
        d.addErrback(cb)

    def start(self, component):
        print component.get('name'), "- trying to start"
        def cb(error=None, component=component):
            print component.get('name'), "- started!", ["Error", ""][error != None]

        d = self.getRootCommand().medium.callRemote(
            'componentStart', component)
        d.addCallback(cb)
        d.addErrback(cb)

    def _callback(self, *args):
        self.getRootCommand().loginDeferred.pause()
        print
        print datetime.datetime.now()
        d = self.getRootCommand().medium.callRemote('getPlanetState')
        def gotPlanetStateCb(planetState, self=self):
            for f in planetState.get('flows') + [planetState.get('atmosphere')]:
                ds = []
                for component in sorted(f.get('components'), cmp=lambda a, b: cmp(a.get('name'), b.get('name'))):
                    name = component.get('name')
                    mood = component.get('mood')

                    print "%30s %10s (%i)" % (
                        name, moods.get(mood).name, mood)

                    if moods.get(mood) in (moods.sad, moods.sleeping):
                        self.restart(component)

            reactor.callLater(1, self._callback)

        d.addCallback(gotPlanetStateCb)
        d.addErrback(self.eb)
        return d

    def _connectedCb(self, result):
        print 'Connected to manager.'
        #self.loginDeferred.callback(result)


class Command(main.Command):
    description = "Send stats to the streamti.me server."

    subCommandClasses = [WatchDog]


def main(args):
    args.append('watchdog')

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
