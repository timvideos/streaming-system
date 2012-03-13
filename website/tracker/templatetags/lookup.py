#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django import template

register = template.Library()

@register.filter(name="lookup")
def lookup_filter(o, key):
    try:
        return o[key]
    except KeyError:
        return None
