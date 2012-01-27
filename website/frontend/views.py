#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Simple pages."""

# Python imports
import ConfigParser
import datetime
import logging
import os
import time
import re

from django import http
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_control

# Our App imports
import models

CONFIG = ConfigParser.ConfigParser()
CONFIG.read([os.path.dirname(__file__)+'/../config.ini'])
GROUPS = CONFIG.get('config', 'groups').split()

# IP Address which are considered "In Room"
LOCALIPS = [x[1] for x in CONFIG.items('localips')]


def check_group(group):
    group = group.lower()
    if not re.match('[a-z/]+', group):
        group = None
    if group not in GROUPS:
        group = None
    return group


def group(request, group):
    response = http.HttpResponse()

    group = check_group(group)
    if not group:
        return django.views.generic.simple.redirect_to(request, url='/')

    channel = CONFIG.get('groups', group)
    justintv = CONFIG.get('justintv', group)

    template = request.get('template', '')
    if not re.match('[a-z]+', template):
        template = 'index'

        # Is the request coming from the room?
        for ipregex in LOCALIPS:
            if re.match(ipregex, request.remote_addr):
                template = 'inroom'

    screenstr = request.get('screen', 'False')
    if screenstr.lower()[0] in ('y', 't'):
        screen = True
    else:
        screen = False

    try:
        hashtag = CONFIG.get('twitter', group)
    except ConfigParser.NoOptionError, e:
        hashtag = CONFIG.get('twitter', 'default')

    response['Content-Type'] = 'text/html'
    response.write(render_to_response('%s.html' % template, locals()))
    return response


def index(request, template="index"):
    # Get the currently active groups
    ten_mins_ago = datetime.datetime.now() - datetime.timedelta(seconds=30)
    groups = set()
    for server in models.Encoder.objects.all():
        if server.lastseen < ten_mins_ago:
            continue
        groups.add(server.group)

    global channels

    hashtag = CONFIG.get('twitter', 'default')
    return render_to_response('%s.html' % template, locals())


@cache_control(must_revalidate=True, max_age=600)
def schedule(request):
    """Get the json schedule from LCA and put it in our domain so we can AJAX it."""
    response = http.HttpResponse(content_type='text/javascript')

    schedule = cache.get('schedule')
    if not schedule:
        schedule = urllib.fetch('http://lca2012.linux.org.au/programme/schedule/json').content
        cache.set('schedule', schedule, 120)
    response.write(schedule)
    return response
