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


# Our App imports
import models

CONFIG = ConfigParser.ConfigParser()
CONFIG.read([os.path.dirname(__file__)+'/config.ini'])
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


def nocache(headers):
    headers['Pragma'] = 'no-cache'
    headers['Cache-Control'] = 'max-age=0, no-cache, no-store, private, must-revalidate'
    headers['Expires'] = 'Wed, 11 Jan 1984 05:00:00 GMT'


def base(request, group):
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


def streams(request, group):
    """Renders the streams.js file."""

    group = check_group(group)
    if not group:
        response = http.HttpResponse()
        nocache(response)
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
        nocache(response)
        response.write("window.src = '/';\n");
        return response
    else:
        # Choose the least loaded server
        server = sorted(active_servers, cmp=lambda a, b: cmp(a.bitrate, b.bitrate))[0].ip

    # Make sure this page isn't cached, otherwise the server load balancing won't work.
    return render_to_response('streams.js', locals(), content_type='text/javascript')


def whats_on(request):
    """Renders the whats_on.js file."""
    response = http.HttpResponse()
    response['Content-Type'] = 'text/javascript'
    nocache(response)

    current_time = int(time.time())
    response.write(render_to_response('whats_on.js', locals()))
    return response


def register(request, group):
    """Registers an encoding server into the application."""
    response = http.HttpResponse(content_type='text/plain')
    nocache(response)

    secret = request.get('secret')
    if secret != CONFIG.get('config', 'secret'):
        response.write('ERROR SECRET\n')
        return

    group = request.get('group')
    if group not in GROUPS:
        response.write('ERROR GROUP\n')
        return

    ip = request.get('ip')
    clients = int(request.get('clients'))
    bitrate = int(request.get('bitrate'))

    s = models.Encoder(
            key_name='%s-%s' % (group, ip),
            group=group,
            ip=ip,
            clients=clients,
            bitrate=bitrate)
    s.put()
    response.write('OK\n')
    return response


def groups(request, template="groups"):
    # Get the currently active groups
    ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    groups = set()
    for server in models.Encoder.objects.all():
        if server.lastseen < ten_mins_ago:
            continue
        groups.add(server.group)

    global channels

    hashtag = CONFIG.get('twitter', 'default')
    return render_to_response('%s.html' % template, locals())


def stats(request):
    """Print out some stats about registered encoders."""
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
    nocache(response)

    def table(self, servers):
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


def ip(request):
    """Print out the callers IP."""
    response = http.HttpResponse(content_type='text/plain')
    nocache(response)
    response.write(request.META['REMOTE_ADDR'])

    return response

def schedule(request):
    """Get the json schedule from LCA and put it in our domain so we can AJAX it."""
    response = http.HttpResponse(content_type='text/javascript')

    schedule = memcache.get('schedule')
    if not schedule:
        schedule = urlfetch.fetch('http://lca2012.linux.org.au/programme/schedule/json').content
        memcache.set('schedule', schedule, 120)
    response.write(schedule)
    return response
