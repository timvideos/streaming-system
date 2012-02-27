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
from django.shortcuts import render_to_response
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

# Our App imports
from common.views.simple import never_cache_redirect_to
from tracker import models


config_path = os.path.realpath(os.path.dirname(__file__)+"/../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()

# IP Address which are considered "In Room"
LOCALIPS = CONFIG['config']['localips']


@never_cache
def streams(request, group):
    """Renders the streams.js file."""
    if not common_config.group_valid(CONFIG, group):
        response = http.HttpResponse()
        response.write("window.src = '/';\n");
        return response

    channel = CONFIG.get('groups', group)

    # Get all the active streaming severs for this channel
    ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    q = models.Encoder.objects.all()
    q.filter('group =', group)

    active_servers = []
    for server in q:
        if server.lastseen < ten_mins_ago:
            continue
        active_servers.append(server)

    if not active_servers:
        # FIXME: Technical difficulties server....
        response = http.HttpResponse()
        response.write("window.src = '/';\n");
        return response
    else:
        # Choose the least loaded server
        server = sorted(active_servers, cmp=lambda a, b: cmp(a.bitrate, b.bitrate))[0].ip

    # Make sure this page isn't cached, otherwise the server load balancing won't work.
    return render_to_response('streams.js', locals(), content_type='text/javascript')


@csrf_exempt
@never_cache
def register(request):
    """Registers an encoding server into the application."""
    if request.method != 'POST':
        return never_cache_redirect_to(request, url="/")

    response = http.HttpResponse(content_type='text/plain')

    secret = request.POST['secret']
    if secret != CONFIG.get('config', 'secret'):
        response.write('ERROR SECRET\n')
        return

    group = request.POST['group']
    if group not in GROUPS:
        response.write('ERROR GROUP\n')
        return

    ip = request.META['REMOTE_ADDR']
    clients = int(request.POST['clients'])
    bitrate = int(request.POST['bitrate'])

    s = models.Encoder(
            group=group,
            ip=ip,
            clients=clients,
            bitrate=bitrate)
    s.save()
    response.write('OK\n')
    return response


@never_cache
def stats(request):
    """Print out some stats about registered encoders."""
    logging.info('stats!')
    response = http.HttpResponse()

    inactive_servers = []
    active_servers = []

    ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    for server in models.Encoder.objects.all():
        if server.lastseen < ten_mins_ago:
            inactive_servers.append(server)
        else:
            active_servers.append(server)

    active_servers = sorted(active_servers, cmp=lambda a, b: cmp((a.group, a.bitrate), (b.group, b.bitrate)))
    inactive_servers = sorted(inactive_servers, cmp=lambda a, b: cmp((a.group, a.bitrate), (b.group, b.bitrate)))

    response['Content-Type'] = 'text/html'

    def table(servers):
        response.write('       <table>')
        response.write('           <tr>')
        response.write('               <th>ip</th>')
        response.write('               <th>group</th>')
        response.write('               <th>clients</th>')
        response.write('               <th>bitrate (bits/s)</th>')
        response.write('               <th>bitrate (megabits/s)</th>')
        response.write('               <th>lastseen</th>')
        response.write('           </tr>')
        for server in servers:
            response.write('           <tr>')
            response.write('               <td>%s</td>' % server.ip)
            response.write('               <td>%s</td>' % server.group)
            response.write('               <td>%i</td>' % server.clients)
            response.write('               <td>%i b/s</td>' % server.bitrate)
            response.write('               <td>%.2f MB/s</td>' % (server.bitrate/1e6))
            response.write('               <td>%s</td>' % server.lastseen)
            response.write('           </tr>')
        response.write('       </table>')

    response.write('<html>')
    response.write('   <head>')
    response.write('       <link rel="stylesheet" type="text/css" href="/static/css/stats.css">')
    response.write('   </head>')
    response.write('   <body>')
    response.write('      <h1>Active Servers</h1>')
    table(active_servers)
    response.write('      <h1>Non-Active Servers</h1>')
    table(inactive_servers)
    response.write('   </body>')
    response.write('</html>')
    return response
