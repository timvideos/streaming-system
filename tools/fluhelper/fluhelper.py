#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Connect to the streamti.me server and report our stats."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"

import cStringIO as StringIO
import datetime
import logging
import pprint
import simplejson
import subprocess
import sys
import time
import threading
import traceback
import urllib
import urllib2

try:
    from termcolor import colored
except:
    logging.warn("termcolor package not installed, you won't get any colors!")
    colored = lambda t, c: t

from twisted.internet import defer, reactor, error
import twisted.spread.pb

from flumotion.admin.command import common
from flumotion.admin.command import main

from flumotion.common import errors, planet, log
from flumotion.common.planet import moods

from flumotion.monitor.nagios import util


class WatchDog(common.AdminCommand):
    description = "Watch Dog the components."
    usage = ""

    def restart_full(self):
        """Restart the whole of flumotion."""
        logging.error('Starting the whole of flumotion')
        return subprocess.call('/etc/init.d/flumotion restart', shell=True)

    def restart_component(self, component, count=Counter()):
        """Restart an individual flumotion component."""
        try:
            count.acquire()

            logging.info("%s - trying to stop", component.get('name'))

            def stopped_cb(error=None, self=self, component=component):
                logging.info('%s - stopped%s',
                    component.get('name'),
                    (" (Error r"+repr(error)+")", "")[error == None])
                self.start_component(component, count)

            d = self.getRootCommand().medium.callRemote(
                'componentStop', component)
            d.addCallback(stopped_cb)
            d.addErrback(stopped_cb)
        except twisted.spread.pb.DeadReferenceError, e:
            logging.error(e)
            return

    def start_component(self, component, count=Counter()):
        """Start an individual flumotion component."""
        try:
            logging.info("%s - trying to start", component.get('name'))
            def started_cb(error=None, component=component):
                logging.info('%s - started%s',
                    component.get('name'),
                    (" (Error r"+repr(error)+")", "")[error == None])

                def cooldown(count=count):
                    time.sleep(5)
                    count.release()
                t = threading.Thread(target=cooldown)
                t.daemon = True
                t.start()

            d = self.getRootCommand().medium.callRemote(
                'componentStart', component)
            d.addCallback(started_cb)
            d.addErrback(started_cb)
        except twisted.spread.pb.DeadReferenceError, e:
            logging.error(e)
            return

    def checkstate(self):
        dump = self.flumotion_state.dump()
        logging.info(dump)

        if self.register and not self.sending and dump.strip():
            def send_state(self=self):
                data = {
                    'recorded_time': time.time(),
                    'identifier': self.identifier,
                    'type': self.type,
                    'secret': self.secret,
                    'data': simplejson.dumps(self.flumotion_state.state()),
                    }
                logging.debug("%s %s", self.register, data)
                try:
                    urllib2.urlopen(self.register, data=urllib.urlencode(data))
                except urllib2.HTTPError, e:
                    logging.error("%s: %s", e, e.read())

                logging.debug('Sent flumotion state up.')

                time.sleep(30)

                self.sending = None

            self.sending = threading.Thread(target=send_state)
            self.sending.daemon = True
            self.sending.start()

        num = len(self.flumotion_state.components())
        for component in self.flumotion_state.components():
            flucomponent = self.flumotion_state.component(component)
            mood = self.flumotion_state.mood(component)

            count = self.flumotion_state.count(component)
            if not count.acquire(True):
                logging.info('%s was locked for changing', component)
                self.flumotion_state.error(component, 1)
                continue

            # States which are considered happy
            #HAPPY, WAITING, BORKED, FATAL

            # Happy components are good components.
            if mood in StateTracker.HAPPY:
                count.release()
                continue

            # Waiting components which have been waiting for a long time and
            # should only be in the state for a short time.
            elif mood in StateTracker.WAITING_SHORT:
                age = self.flumotion_state.age(component)

                # How long has it been in a waiting state?
                if age >= 10:
                    self.flumotion_state.error(component, 10)
                    self.restart_component(flucomponent, count)

            # Waiting components which have been waiting for a *really* long time.
            elif mood in StateTracker.WAITING_LONG:
                age = self.flumotion_state.age(component)

                # How long has it been in a waiting state?
                if age >= 30:
                    self.flumotion_state.error(component, 1)
                    self.restart_component(flucomponent, count)

            # Restart components which are currently borked.
            elif mood in StateTracker.BORKED:
                self.flumotion_state.error(component, 15)
                self.restart_component(flucomponent, count)

            # Fatal components need flumotion to be restarted.
            elif mood in StateTracker.FATAL:
                self.flumotion_state.error(component, 1e6)

            else:
                logging.error('Component %s in unknown state %s', mood, state)

            count.release()

        for component in self.flumotion_state.components():
            if self.flumotion_state.error(component) > 100.0:
                self.restart_full()
                return False
        else:
            return True


class Command(main.Command):
    description = "Send stats to the streamti.me server."

    subCommandClasses = [WatchDog]


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
    args = args_a + ["watchdog"] + args_b

    c = Command()
    try:
        ret = c.parse(args[1:])
    except common.Exited, e:
        ret = e.code
        if ret == 0:
            sys.stdout.write(e.msg + '\n')
        else:
            sys.stderr.write(e.msg + '\n')

    return ret
