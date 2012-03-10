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
import subprocess
import sys
import time
import threading
import traceback

try:
    from termcolor import colored
except:
    colored = lambda t, c: t

from twisted.internet import defer, reactor, error

from flumotion.admin.command import common
from flumotion.admin.command import main

from flumotion.common import errors, planet, log
from flumotion.common.planet import moods

from flumotion.monitor.nagios import util


class Counter(object):
    def __init__(self):
        self.count = 0

    def acquire(self, empty=False):
        if empty and self.count != 0:
            return False
        self.count += 1
        return True
    def release(self):
        self.count -= 1


class StateTracker(object):
    """Tracks the current state of Flumotion."""

    # States which are considered happy
    HAPPY = [moods.happy.name]
    # States which are transitional
    WAITING_LONG = [moods.waking.name, moods.hungry.name]
    WAITING_SHORT = [moods.sleeping.name]
    # States which are considered borked
    BORKED = [moods.sad.name]
    # States which are considered fatal
    FATAL = [moods.lost.name]

    THRESHOLD = 100

    def __init__(self):
        self.__history = {}
        self.__current = {}
        self.__cobjs = {}
        self.__counts = {}

        self.__lock = threading.Lock()

    def update(self, obj):
        cname = obj.get('name')
        new_mood = moods.get(obj.get('mood')).name

        self.__cobjs[cname] = obj

        with self.__lock:
            previous_state = self.__current.get(cname, ['unknown', 0])
            if new_mood != previous_state[0]:
                    # Move the previous state into the history
                    history = self.age(cname)

                    if cname not in self.__history:
                        self.__history[cname] = []

                    if previous_state[0] != 'unknown':
                        self.__history[cname].append((
                            previous_state[0], previous_state[-1], history))

                    # Update the mood
                    self.__current[cname] = (new_mood, time.time())

    def mood(self, cname):
        """Get the current mood of an component."""
        try:
            if not isinstance(cname, (str, unicode)):
                cname = cname.get('name')

            return self.__current[cname][0]
        except KeyError:
            return "unknown"

    def entered(self, cname):
        """Get how the time that a component entered the current mood."""
        try:
            if not isinstance(cname, (str, unicode)):
                cname = cname.get('name')

            return self.__current[cname][-1]
        except KeyError:
            return 0

    def age(self, cname):
        """Get how long the component has been at the current mood."""
        try:
            if not isinstance(cname, (str, unicode)):
                cname = cname.get('name')

            return time.time() - self.entered(cname)
        except KeyError:
            return 0

    def dump(self):
        """Dump a status string."""
        def totime(s):
            return time.strftime('%H:%M:%S', time.localtime(s))

        s = StringIO.StringIO()
        s.write('\n')
        for cname in self.components():
            mood = self.mood(cname)

            if mood in self.HAPPY:
                color = 'green'
            elif mood in self.WAITING_SHORT:
                color = 'blue'
            elif mood in self.WAITING_LONG:
                color = 'blue'
            elif mood in self.BORKED:
                color = 'yellow'
            elif mood in self.FATAL:
                color = 'red'
            else:
                color = 'white'

            s.write('%30s (at %s) in %s for %4.2fs\n' % (
                cname,
                totime(self.entered(cname)),
                colored('%8s' % mood, color),
                self.age(cname),
                ))
            for m, t, a in self.history(cname):
                s.write(colored('%30s (at %s) in %s for %4.2f\n', 'grey') % (
                    '', totime(t), colored('%8s' % m, 'grey'), a))
        return s.getvalue()

    def history(self, cname, number=5):
        """Get the history of a component.

        Doesn't include the current state.

        Format is a list of:
            mood,
            time entered that mood,
            how long in that mood
        """
        return self.__history[cname][-number:]

    def components(self):
        """Get a list of the current components."""
        return list(sorted(self.__current.keys()))

    def component(self, cname):
        """Get the flumotion component associated with a name."""
        return self.__cobjs[cname]

    def count(self, cname):
        """Get a count for a given component."""
        if not isinstance(cname, (str, unicode)):
            cname = cname.get('name')

        if cname not in self.__counts:
            self.__counts[cname] = Counter()
        return self.__counts[cname]


class WatchDog(common.AdminCommand):
    description = "Watch Dog the components."
    usage = ""

    def __init__(self, *args, **kw):
        self.error_sum = 0

        self.flumotion_state = StateTracker()

        self.check_thread = threading.Thread(target=self.loop)
        self.check_thread.daemon = True

        common.AdminCommand.__init__(self, *args, **kw)

    def eb(self, e):
        logging.error(e)
        self.exit()

    def restart_full(self):
        """Restart the whole of flumotion."""
        return subprocess.call('/etc/init.d/flumotion restart', shell=True)

    def restart_component(self, component, count=Counter()):
        """Restart an individual flumotion component."""
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

    def start_component(self, component, count=Counter()):
        """Start an individual flumotion component."""
        logging.info("%s - trying to start", component.get('name'))
        def started_cb(error=None, component=component):
            logging.info('%s - started%s',
                component.get('name'),
                (" (Error r"+repr(error)+")", "")[error == None])
            count.release()

        d = self.getRootCommand().medium.callRemote(
            'componentStart', component)
        d.addCallback(started_cb)
        d.addErrback(started_cb)

    def handleOptions(self, options):
        self.getRootCommand().loginDeferred.addCallback(self._callback)

    def exit(self):
        # Unpause the edit
        self.getRootCommand().loginDeferred.unpause()

        # Cause the reactor to stop
        try:
            reactor.callLater(0, reactor.stop)
        except error.ReactorNotRunning, e:
            logging.error(e)

    def _callback(self, *args):
        # Pause the exit which would normally be caused after a login in
        # a normal cmd line program.
        self.getRootCommand().loginDeferred.pause()

        # Start update thread.
        self.check_thread.start()

        # Start getting the update information
        return self.getstate(*args)

    def getstate(self, *args):
        d = self.getRootCommand().medium.callRemote('getPlanetState')
        def gotPlanetStateCb(planetState, self=self):
            for f in planetState.get('flows') + [planetState.get('atmosphere')]:
                ds = []
                for component in sorted(f.get('components'), cmp=lambda a, b: cmp(a.get('name'), b.get('name'))):
                    self.flumotion_state.update(component)

            reactor.callLater(1, self.getstate)

        d.addCallback(gotPlanetStateCb)
        d.addErrback(self.eb)
        return d

    def loop(self, *args):
        try:
            while True:
                logging.info('Checking state.')
                if not self.checkstate():
                    logging.info('Restarting.')
                    return
                logging.info('Sleeping.')
                time.sleep(1)
        finally:
            self.exit()

    def checkstate(self):
        logging.info(self.flumotion_state.dump())

        for component in self.flumotion_state.components():
            flucomponent = self.flumotion_state.component(component)
            mood = self.flumotion_state.mood(component)

            count = self.flumotion_state.count(component)
            if not count.acquire(True):
                logging.info('%s was locked for changing', component)
                self.error_sum += 1
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
                    self.error_sum += 1*age

                    self.restart_component(flucomponent, count)

            # Waiting components which have been waiting for a *really* long time.
            elif mood in StateTracker.WAITING_LONG:
                age = self.flumotion_state.age(component)
                # How long has it been in a waiting state?
                if age >= 120:
                    self.error_sum += 1*age

                    self.restart_component(flucomponent, count)

            # Restart components which are currently borked.
            elif mood in StateTracker.BORKED:
                self.error_sum += 1
                self.restart_component(flucomponent, count)

            # Fatal components need flumotion to be restarted.
            elif mood in StateTracker.FATAL:
                self.error_sum += 1e6

            else:
                logging.error('Component %s in unknown state %s', mood, state)

            count.release()

        if self.error_sum > StateTracker.THRESHOLD:
            self.restart_full()
            return False
        else:
            return True


class Command(main.Command):
    description = "Send stats to the streamti.me server."

    subCommandClasses = [WatchDog]


def main(args):
    logging.basicConfig(stream=sys.stdout,level=logging.DEBUG)

    args.append('watchdog')

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
