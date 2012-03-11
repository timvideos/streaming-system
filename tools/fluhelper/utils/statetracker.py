#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Tracks the states of Flumotion."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"


import threading

from flumotion.common.planet import moods

try:
    from termcolor import colored
except:
    logging.warn("termcolor package not installed, you won't get any colors!")
    colored = lambda t, c: t


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

    THRESHOLD = 60

    def __init__(self):
        self.__history = {}
        self.__current = {}
        self.__cobjs = {}
        self.__counts = {}
        self.__errors = {}

        self.__lock = threading.Lock()

    def state(self):
        return {
            'current': dict(self.__current),
            'history': dict(self.__history),
            }

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

    def error(self, cname, add=None):
        """Get the current mood of an component."""
        try:
            if not isinstance(cname, (str, unicode)):
                cname = cname.get('name')

            if add:
                if cname not in self.__errors:
                    self.__errors[cname] = 0.0

                self.__errors[cname] += add

            return self.__errors[cname] / self.THRESHOLD * 100.0
        except KeyError:
            return 0.0

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

            error = self.error(cname)

            s.write('%28s (at %s) in %s for %4.0fs (e %s%%)\n' % (
                cname,
                totime(self.entered(cname)),
                colored('%8s' % mood, color),
                self.age(cname),
                colored('%5.2f' % error, color_percent(error)),
                ))
            for m, t, a in self.history(cname):
                s.write(colored('%28s (at %s) in %s for %4.0fs\n', 'white') % (
                    '', totime(t), '%8s' % m, a))
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
