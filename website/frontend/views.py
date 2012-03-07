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
import sys
import time
import re
import urllib2

from bs4 import BeautifulSoup

from django import http
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control

# Our App imports
from common.views.simple import never_cache_redirect_to
from tracker import models

config_path = os.path.realpath(os.path.dirname(__file__)+"/../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()


def group(request, group):
    if not common_config.group_valid(CONFIG, group):
        return never_cache_redirect_to(request, url="/")

    config = common_config.config_all(CONFIG, group)

    template = request.GET.get('template', 'group')
    if not re.match('[a-z]+', template):
        # Is the request coming from the room?
        for ipregex in LOCALIPS:
            if re.match(ipregex, request.remote_addr):
                template = 'inroom'
                break
        else:
            return never_cache_redirect_to(request, url="/")

    screenstr = request.GET.get('screen', 'False')
    if screenstr.lower()[0] in ('y', 't'):
        screen = True
    else:
        screen = False

    return render_to_response('%s.html' % template, locals())


def index(request, template="index"):
    # Get the currently active groups
    ten_mins_ago = datetime.datetime.now() - datetime.timedelta(seconds=30)
    groups = set()
    for server in models.Encoder.objects.all():
        if server.lastseen < ten_mins_ago:
            continue
        groups.add(server.group)

    groups = CONFIG.keys()
    groups.remove('config')

    config = common_config.config_all(CONFIG, 'default')
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


@cache_control(must_revalidate=True, max_age=600)
def logs(request, group):
    if not common_config.group_valid(CONFIG, group):
        return never_cache_redirect_to(request, url="/")

    config = common_config.config_all(CONFIG, group)

    log = config['irclog']
    soup = BeautifulSoup(urllib2.urlopen(log).read())

    # Fix up the css link
    l = soup.find("link")
    l['href'] = "%s/%s" % (os.path.dirname(log), l['href'])

    # Remove the unwanted decoration.
    [x.decompose() for x in soup.find_all("div", {"class": "navigation"})]
    [x.decompose() for x in soup.find_all("div", {"class": "generatedby"})]
    [x.decompose() for x in soup.find_all("h1")]
    [x.decompose() for x in soup.find_all("div", {"class": "searchbox"})]

    # Reverse the table rows.
    table = soup.find("table")
    new_order = []
    for row in list(table.children):
        new_order.insert(0, row.extract())
    for row in new_order:
        table.append(row)

    table['style'] = "font-size: 8pt;"

    response = http.HttpResponse(content_type='text/html')
    response.write(soup)
    return response

