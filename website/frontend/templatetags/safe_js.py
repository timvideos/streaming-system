#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import re

from django import template

register = template.Library()


@register.filter()
def safe_js(s):
    return re.sub('[^A-Za-z0-9]', '_', s)
