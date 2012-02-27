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
import random
import re
import string
import time

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

###########################################################################################
# Code which collects the client side system reporting.
###########################################################################################

class StatsError(SystemError):
    pass


def generate_salt():
    return "".join(random.choice(string.ascii_letters) for x in range(16))


def key(request, salt=None):
    if salt is None:
        salt = generate_salt()

    in_data = [salt]
    in_data.append(request.META['HTTP_USER_AGENT'])
    in_data.append(request.META['REMOTE_ADDR'])
    return hashlib.sha224.hexdigest()

class error(object):
    # All errors are between 0 and 1024
    ERROR_GROUP = 1

    # All warnings are above 1024
    WARNING_COOKIE = 1025


def client(request):
    """Check the common information for an encoder request."""
    if request.method != 'POST':
        return never_cache_redirect_to(request, url="/")

    response = http.HttpResponse(content_type='application/javascript')

    group = request.POST['group']
    if not common_config.group_valid(CONFIG, group):
        response.write(simplejson.dumps({
            'code': error.ERROR_GROUP,
            'error': 'Unknown group',
            }))
        return response, None, None

    # Check the cookie value
    if 'user' not in request.COOKIES:
        response.set_cookie('user', value=user_key(request))
        response.write(simplejson.dumps({
            'code': error.WARNING_COOKIE,
            'error': 'No cookie set',
            }))
        return response, None, None

    salt, digest = request.COOKIES['user'].split(':')
    assert userid(request, salt) == digest

    return None, group, ip


def client_stats(request):
    response, group, ip = client(request)
    if reponse is not None:
        return response

    response = http.HttpResponse(content_type='application/javascript')

    data = simplejson.loads(int(request.POST['data']))
    data['ip'] = ip
    data['user-agent'] = request.META['HTTP_USER_AGENT']
    data['referrer'] = request.META['HTTP_REFERER']

    s = models.ClientStats()


###########################################################################################
# Code which collects the encoder system reporting.
###########################################################################################

class EncoderError(SystemError):
    pass

def encoder(request):
    """Check the common information for an encoder request."""
    if request.method != 'POST':
        return never_cache_redirect_to(request, url="/")

    response = http.HttpResponse(content_type='text/plain')

    secret = request.POST['secret']
    if secret != CONFIG.get('config', 'secret'):
        response.write('ERROR SECRET\n')
        return response, None, None

    group = request.POST['group']
    if not common_config.group_valid(CONFIG, group):
        response.write('ERROR GROUP\n')
        return response, None, None

    ip = request.META['REMOTE_ADDR']

    return None, group, ip


@csrf_exempt
@never_cache
def encoder_register(request):
    """Registers an encoding server, plus a bunch of stats."""
    response, group, ip = encoder(request)
    if response is not None:
        return response

    data = simplejson.loads(int(request.POST['data']))
    # Check that the data doesn't override these two important values
    assert 'ip' not in data
    assert 'group' not in data

    s = models.Encoder(
            group=group,
            ip=ip,
            **data)
    s.save()

    response = http.HttpResponse(content_type='text/plain')
    response.write('OK\n')
    return response


# Log line format
# 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
# <ip> - <user> [<date>] "<request>" <status code> <bytes> "<referer>" "<user-agent>"
@csrf_exempt
@never_cache
def encoder_logs(request):
    """Saves the client's log files."""
    response, group, ip = encoder(request)
    if response is not None:
        return response

    # Take a lock on the file
    while True:
        logfile = file(os.path.join(CONFIG['config']['logdir'], "access-%s-%s.log" % (group, ip)), 'a')
        try:
            fcntl.lockf(logfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError, e:
            time.sleep(1)
        else:
            break

    # Write out the log lines
    logfile.write(request.POST['data'])
    logfile.flush()

    # Unlock the file
    fcntl.lockf(logfile, fcntl.LOCK_UN)

    # Close the file
    logfile.close()

    # Write out that everything went okay
    response = http.HttpResponse(content_type='text/plain')
    response.write('OK\n')
    return response
