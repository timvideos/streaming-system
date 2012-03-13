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
