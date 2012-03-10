#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django import template
from django.template import defaultfilters

register = template.Library()

@register.filter(name="bitrate")
def bitrate_filter(bits):
    return defaultfilters.filesizeformat(bits).replace('B', 'bits')

@register.filter(name="byterate")
def byterate_filter(bits):
    return defaultfilters.filesizeformat(bits/8).replace('B', 'bytes')
