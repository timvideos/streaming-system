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
        reactor.callLater(0, reactor.stop)

    def handleOptions(self, options):
        self.getRootCommand().loginDeferred.addCallback(self._callback)

    def _callback(self, *args):
        if not hasattr(self, 'dead'):
            self.dead = {}

        if sum(self.dead.values()) > 10:
            print "Found to many inactive items:", self.dead
            subprocess.call('/etc/init.d/flumotion restart', shell=True)
            del self.dead

        self.getRootCommand().loginDeferred.pause()
        print
        print datetime.datetime.now()
        print "Dead count:", self.dead

        d = self.getRootCommand().medium.callRemote('getPlanetState')
        def gotPlanetStateCb(planetState, self=self):
            for f in planetState.get('flows') + [planetState.get('atmosphere')]:
                ds = []
                for component in sorted(f.get('components'), cmp=lambda a, b: cmp(a.get('name'), b.get('name'))):
                    name = component.get('name')
                    if name == "justintv":
                        continue

                    mood = component.get('mood')

                    print "%30s %10s (%i)" % (
                        name, moods.get(mood).name, mood)

                    if moods.get(mood) in (moods.sad,):
                        self.dead[name] = 4 + self.dead.get(name, 0)
                    if moods.get(mood) not in (moods.happy, moods.waking):
                        self.dead[name] = 1 + self.dead.get(name, 0)

            reactor.callLater(1, self._callback)

        d.addCallback(gotPlanetStateCb)
        d.addErrback(self.eb)
        return d


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
