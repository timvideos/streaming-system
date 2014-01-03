#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Simple pages."""

# Python imports
import ConfigParser
import datetime_tz
import logging
import ordereddict
import os
import re
import simplejson as json
import sys
import urllib2
from itertools import ifilter, islice

from django import http
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control

# Our App imports
from common.views.simple import NeverCacheRedirectView
from tracker import models

config_path = os.path.realpath(os.path.dirname(__file__)+"/../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()
LOCALIPS = [re.compile(x) for x in CONFIG['config']['localips'] if x]

from .data import data


def group(request, group):
    if not CONFIG.valid(group):
        if settings.DEBUG:
            raise Exception("Invalid group: %s (valid groups %s)" % (group, CONFIG.keys()))
        else:
            return NeverCacheRedirectView.as_view(url="/")(request)

    config = CONFIG.config(group)

    template = request.GET.get('template', 'default')
    if not re.match('[a-z]+', template):
        if settings.DEBUG:
            raise Exception("Unknown template: %s" % template)
        else:
            return NeverCacheRedirectView.as_view(url="/")(request)
    elif template == 'default':
        template = "group"
        # Is the request coming from the room?
        for ipregex in LOCALIPS:
            if ipregex.match(request.META['HTTP_X_REAL_IP']):
                template = 'inroom'
                break

    screenstr = request.GET.get('screen', 'False')
    if screenstr.lower()[0] in ('y', 't'):
        screen = True
    else:
        screen = False

    return render_to_response('%s.html' % template, locals())


def index(request, template="index"):
    groups = ordereddict.OrderedDict()
    for group in sorted(CONFIG.groups()):
        groups[group] = CONFIG.config(group)

    config = CONFIG['config']
    default = CONFIG['default']
    return render_to_response('%s.html' % template, locals())


def get_current_next(group, howmany=2, delta=datetime_tz.timedelta()):
    if group in data:
        now = datetime_tz.datetime_tz.utcnow()
        return islice(
            ifilter(
                lambda x: x['end'] > now,
                data[group]
            ),
            howmany
        )
    else:
        return []

def json_feed(request, group):
    response = http.HttpResponse(content_type='text/javascript')

    delta = datetime_tz.timedelta(seconds=int(request.GET.get('delta', 0)))
    two_elements = list(get_current_next(group, delta=delta))

    for index, element in enumerate(two_elements):
        element = dict(element)
        for key in ('start', 'end'):
            element[key] = str(element[key])
        two_elements[index] = element

    response.write(json.dumps(two_elements))
    return response
