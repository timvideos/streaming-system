#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django import template

register = template.Library()


@register.filter(name="getattr")
def getattr_filter(o, key):
    return getattr(o, key)
