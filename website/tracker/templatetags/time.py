#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import datetime

from django import template
from django.template import defaultfilters

register = template.Library()

@register.filter(name="udate")
def udate(s, date):
    try:
        d = datetime.datetime.fromtimestamp(s)
        return defaultfilters.date(d, date)
    except:
        return None

@register.filter(name="timedelta")
def timedelta(a, b):
    if not isinstance(a, datetime.datetime):
        a = datetime.datetime.fromtimestamp(a)
    if not isinstance(b, datetime.datetime):
        b = datetime.datetime.fromtimestamp(b)

    delta = b-a
    return "%im%2is" % (delta.seconds/60, delta.seconds%60)
