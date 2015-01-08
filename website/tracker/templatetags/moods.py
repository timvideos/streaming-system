#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django import template

register = template.Library()

# States which are considered happy
HAPPY = ['happy']
# States which are transitional
WAITING = ['waking', 'hungry', 'sleeping']
# States which are considered borked
BORKED = ['sad']
# States which are considered fatal
FATAL = ['lost']


@register.filter()
def mood_style(m):
    if m in HAPPY:
        return 'mood_happy'
    elif m in WAITING:
        return 'mood_wait'
    elif m in BORKED:
        return 'mood_bork'
    elif m in FATAL:
        return 'mood_fatal'
    else:
        return 'mood_unknown'
