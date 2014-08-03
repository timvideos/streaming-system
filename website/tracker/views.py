#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Simple pages."""

# Python imports
import ConfigParser
import datetime
import hashlib
import logging
import ordereddict
import os
import random
import re
import simplejson
import string
import sys
import time
import traceback

from django import http
from django.db import transaction
from django.db import models as django_models
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django import template

# Our App imports
from common.views import NeverCacheRedirectView
from tracker import models


config_path = os.path.realpath(os.path.dirname(__file__)+"/../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config as common_config
CONFIG = common_config.config_load()

# IP Address which are considered "In Room"
LOCALIPS = CONFIG['config']['localips']

class funnydict(dict):
    def __getattr__(self, key):
        return self[key]


@never_cache
def stream(request, group):
    """Gives an end user a streaming server for a group.

    Picks the least loaded by bitrate.
    """
    if not CONFIG.valid(group):
        response = http.HttpResponse()
        response.write("window.src = '/';\n");
        return response

    # Get all the active streaming severs for this channel
    active_servers = models.Endpoint.active(group=group)

    # Pick a server
    if active_servers:
        your_server = sorted(active_servers, cmp=lambda a, b: cmp(a.overall_bitrate, b.overall_bitrate))[0]
    else:
        your_server = None

    # Make sure this page isn't cached, otherwise the server load balancing won't work.
    return render(request, 'stream.js', locals(), content_type='text/javascript',
                  context_instance=template.RequestContext(request))


@never_cache
def streams(request):
    """Renders the streams.js file which contains a list of active streams."""
    # Get all the active streaming severs for this channel
    active_servers = models.Endpoint.active()

    # Make sure this page isn't cached, otherwise the server load balancing won't work.
    return render(request, 'streams.js', locals(), content_type='text/javascript',
                  context_instance=template.RequestContext(request))


@never_cache
def endpoint_stats(request):
    """Print out some stats about registered endpoints."""
    response = http.HttpResponse()

    inactive_servers = []
    active_servers = []

    ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)

    endpoints = models.Endpoint.active(delta=datetime.timedelta(days=7))
    for server in endpoints:
        if server.lastseen < ten_mins_ago:
            inactive_servers.append(server)
        else:
            active_servers.append(server)

    types = list(sorted([x for x in dir(models.Endpoint()) if x.endswith('_clients')]))
    all_types = list(sorted([x for x in dir(models.Endpoint()) if not x.startswith('_')]))

    active_servers = sorted(active_servers, cmp=lambda a, b: cmp((a.group, a.overall_bitrate), (b.group, b.overall_bitrate)))
    active_overall = funnydict((t, sum([0, getattr(x, t, None)][isinstance(getattr(x, t, None), (int, float))] for x in active_servers)) for t in all_types)

    inactive_servers = sorted(inactive_servers, cmp=lambda a, b: cmp((a.group, a.overall_bitrate), (b.group, b.overall_bitrate)))
    inactive_overall = funnydict((t, sum([0, getattr(x, t, None)][isinstance(getattr(x, t, None), (int, float))] for x in inactive_servers)) for t in all_types)

    return render(request, 'stats.html', locals(), content_type='text/html',
                  context_instance=template.RequestContext(request))


def overall_stats_json(request):
    """Generate JSON containing overall data for use by graphs. The data can
    be generated however, and just needs to be a series of x,y points. Any
    number of graphs can be generated. The time range is specified as a GET
    parameter indicating the number of minutes before now.

    The response is a list of graph definitions as dictionaries, and a list of
    annotations, and looks something like:

        {
            'graphs': [
                {
                    'title'     : 'Graph Title',
                    'stacked'   : True,
                    'series'    : [
                        {
                            'label': 'series-1',
                            'data': [ [x1,y1], [x2,y2], ... ]
                        },
                        ...
                    ]
                },
                ...
            ],
            'annotations': [
                {
                    'x': 1332009326000,
                    'label': 'Some event happened'
                },
            ...
            ]
        }

    To add a graph, generate the needed list(s) of [x,y] points and include that
    list in a structure with title and label information similar that described
    above. Then append that "graph definition" to the list of graphs to be
    displayed.

    Note: dates should be sent as ms since epoch (unix time * 1000). Also,
    annotations are applied to all of the graphs.

    Currently, the data is Endpoint overall_bitrate and overall_clients,
    aggregated as an average for each unique lastseen.
    """

    graphs = []
    annotations = []

    DEFAULT_RANGE = 120 # minutes

    # Get the requested time range for the data, in minutes.
    view_range = request.GET.get('range',DEFAULT_RANGE)

    # Ensure the range is an int, falling back to the default if it's not.
    try:
        view_range = int(view_range)
    except ValueError:
        view_range = DEFAULT_RANGE

    range_start_datetime = datetime.datetime.now() - datetime.timedelta(minutes=view_range)

    # Prepare the graphs to be sent back.

    bitrate_graph = {
        'title': 'Overall Bitrate',
        'stacked': True,
        'series': [],
    }

    client_graph = {
        'title': 'Overall Clients',
        'stacked': True,
        'series': [],
    }

    # Retrieve endpoints from within the requested data range.
    recent_endpoints = models.Endpoint.objects.filter(
        lastseen__gte=range_start_datetime,
        lastseen__lte=datetime.datetime.now()
    ).order_by('-lastseen')

    # Assemble the data for each endpoint by group.
    endpoints_by_group = {}

    # Attributes that can be copied directly.
    raw_attrs = ('overall_bitrate', 'overall_clients',)
    for endpoint in recent_endpoints:
        if endpoint.group not in endpoints_by_group:
            endpoints_by_group[endpoint.group] = []

        # Send time as a unix timestamp.
        endpoint_data = {
            'lastseen' : int(endpoint.lastseen.strftime('%s')) * 1000,
        }
        for attr in raw_attrs:
            endpoint_data[attr] = getattr(endpoint, attr)
        endpoints_by_group[endpoint.group].append(endpoint_data)

    for group, endpoints in endpoints_by_group.items():
        bitrate_data = []
        client_data = []
        for point in endpoints:
            bitrate_data.append([point['lastseen'], point['overall_bitrate'] / (1000000)])
            client_data.append([point['lastseen'], point['overall_clients']])
        bitrate_graph['series'].append({
            'label': group,
            'data': bitrate_data,
        })
        client_graph['series'].append({
            'label': group,
            'data': client_data,
        })

    graphs.append(bitrate_graph)
    graphs.append(client_graph)


    # SAMPLE GRAPH AND ANNOTATION GENERATION
    # Uncomment these to see sample graphs and annotations using data generated
    # based on the current time.

    # Graphs:
    # now = datetime.datetime.now()
    # graphs.append({
    #     'title': 'Test graph',
    #     'stacked': True,
    #     'series': [{
    #         'label': 'series-' + str(i),
    #         'data': [[int((now - datetime.timedelta(minutes=j)).strftime('%s')) * 1000,random.randint(1,11)] for j in range(200)]
    #     } for i in range(5)]
    # })

    # Annotations:
    # annotations.append({
    #     'x': int((datetime.datetime.now() - datetime.timedelta(minutes=12)).strftime('%s')) * 1000,
    #     'label': 'Chow!'
    # })


    # Send the data back as JSON data.
    response = http.HttpResponse(content_type='application/json')
    response.write(simplejson.dumps({
        'graphs': graphs,
        'annotations': annotations,
    }))
    return response

###########################################################################################
# Code which collects the client side system reporting.
###########################################################################################

def generate_salt():
    """Generate a suitable ASCII alpha salt."""
    return "".join(random.choice(string.ascii_letters) for x in range(16))


def user_key(request, salt=None):
    """Generate a unique key for this user."""
    if salt is None:
        salt = generate_salt()

    in_data = [salt]
    in_data.append(request.META['HTTP_USER_AGENT'])
    in_data.append(request.META['HTTP_X_REAL_IP'])
    return '%s:%s' % (salt, hashlib.sha224("".join(in_data)).hexdigest())


class error(object):
    """Class defining error messages which are returned to the client."""
    SUCCESS = 0

    # All errors are between 1 and 1024
    ERROR_GROUP = 1
    ERROR_JSON = 2

    # All warnings are above 1024
    WARNING_COOKIE = 1025


def client_common(request, group):
    """Check the common information for an client request."""
    if request.method != 'POST':
        return NeverCacheRedirectView.as_view(url="/")(request)

    response = http.HttpResponse(content_type='application/javascript')

    if not CONFIG.valid(group):
        response.write(simplejson.dumps({
            'code': error.ERROR_GROUP,
            'error': 'Unknown group',
            'next': -1,
            }))
        return (response, None, None)

    # Check the cookie value exists
    if 'user' not in request.COOKIES:
        response.set_cookie('user', value=user_key(request))
        response.write(simplejson.dumps({
            'code': error.WARNING_COOKIE,
            'error': 'No cookie set',
            'next': 0,
            }))
        return (response, None, None)

    # Check the cookie value is valid
    salt, digest = request.COOKIES['user'].split(':')
    if user_key(request, salt) != request.COOKIES['user']:
        response.delete_cookie('user')
        response.write(simplejson.dumps({
            'code': error.WARNING_COOKIE,
            'error': 'Cookie was invalid?',
            'next': 0,
            }))
        return (response, None, None)

    return (None, group, request.COOKIES['user'])


def dump_request_headers(request):
    return dump


@csrf_exempt
@never_cache
@transaction.commit_on_success
def client_stats(request, group, _now=None):
    """
    Save stats about a client.

    Args:
        request: Django request object.
        group: Group to save stats about.
        _now: A datetime.datetime object to pretend is "now". Used for testing
              only.

    Returns:
        Django response object.
    """
    response, group, user = client_common(request, group)
    if response is not None:
        return response

    try:
        data = simplejson.loads(request.POST.get('data', "{}"))
    except simplejson.JSONDecodeError, e:
        response = http.HttpResponse(content_type='application/javascript')
        response.write(simplejson.dumps({
            'code': error.ERROR_JSON,
            'error': 'Invalid JSON: %s' % e,
            'next': -1,
            }))
        return response

    data['user-agent'] = request.META['HTTP_USER_AGENT']
    data['ip'] = request.META['HTTP_X_REAL_IP']
    if 'HTTP_REFERER' in request.META:
        data['referrer'] = request.META['HTTP_REFERER']

    # Save the stats
    s = models.ClientStats(
        group=group,
        created_by=user)
    if _now is not None:
        s.created_on = _now
    s.save()
    s.from_dict(data)

    # Return success
    response = http.HttpResponse(content_type='application/javascript')
    response.write(simplejson.dumps({
        'code': error.SUCCESS,
        'next': 5,
        }))
    return response

###########################################################################################
# Code which collects the endpoint system reporting.
###########################################################################################


def endpoint_common(request, check_group=True):
    """Check the common information for an endpoint request."""
    if request.method != 'POST':
        return NeverCacheRedirectView.as_view(url="/")(request)

    response = http.HttpResponse(content_type='text/plain')

    if not CONFIG['config'].get('secret', None):
        response.write('ERROR CONFIG (No secret)\n')
        return response, None, None

    secret = request.POST.get('secret', '')
    if secret != CONFIG['config']['secret']:
        response.write('ERROR SECRET\n')
        return response, None, None

    if check_group:
        group = request.POST.get('group', '')
        if not CONFIG.valid(group):
            response.write('ERROR GROUP\n')
            return response, None, None
    else:
        group = None

    ip = request.META['HTTP_X_REAL_IP']

    return None, group, ip


@csrf_exempt
@never_cache
@transaction.commit_on_success
def endpoint_register(request):
    """Registers an endpoint server.

    An endpoint server is one which is sending data to end users. It might be
    an endpoint in smaller setups, or in more advanced systems an amplifier.
    """
    response, group, ip = endpoint_common(request)
    if response is not None:
        return response

    try:
        data = simplejson.loads(request.POST.get('data', '{}'))
        # Check that the data doesn't override these two important values
        assert 'ip' not in data
        assert 'group' not in data

        s = models.Endpoint(
                group=group,
                ip=ip,
                **data)
        s.save()

        response = http.HttpResponse(content_type='text/plain')
        response.write('OK\n')
        return response
    except Exception, e:
        response = http.HttpResponse(content_type='text/plain')
        response.write('ERROR %s\n' % e.__class__.__name__)
        traceback.print_exc(file=response)
        return response


# Log line format
# 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
# <ip> - <user> [<date>] "<request>" <status code> <bytes> "<referer>" "<user-agent>"
@csrf_exempt
@never_cache
def endpoint_logs(request):
    """Saves an endpoint server Apache logs."""
    response, group, ip = endpoint_common(request)
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


# Save some data about flumotion
@csrf_exempt
@never_cache
def flumotion_logging(request):
    """Saves the client's log files."""
    response, group, ip = endpoint_common(request, check_group=False)
    if response is not None:
        return response

    try:
        data = simplejson.loads(request.POST.get('data', "{}"))
    except simplejson.JSONDecodeError, e:
        response = http.HttpResponse(content_type='text/plain')
        response.write('ERROR %s' % e)
        return response

    s = models.Flumotion(
            identifier=request.POST['identifier'],
            recorded_time=request.POST['recorded_time'],
            type=request.POST.get('type', ''),
            ip=request.META['HTTP_X_REAL_IP'],
            data=simplejson.dumps(data),
            )
    s.save()

    # Write out that everything went okay
    response = http.HttpResponse(content_type='text/plain')
    response.write('OK\n')
    return response


@never_cache
def flumotion_stats(request):
    ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)

    flumotion = models.Flumotion.objects.order_by(
        'type', 'identifier', 'ip', '-lastseen'
        ).filter(lastseen__gte = ten_mins_ago)

    [(x.identifier, x.lastseen, x.type) for x in flumotion]

    types = set()
    keys = {}

    active_servers = ordereddict.OrderedDict()
    for server in flumotion:
        types.add(server.type)
        if server.type not in keys:
            keys[server.type] = set()

        key = '%s-%s' % (server.identifier, server.ip)

        # Format the data a bit nicer
        server.full_data = simplejson.loads(server.data)

        # Append to the list of components
        for k in server.full_data['current'].keys():
            keys[server.type].add(k)

        if not key in active_servers:
            active_servers[key] = server
        else:
            # Append history
            newest = active_servers[key]
            for k in newest.full_data['current'].keys():
                if k not in server.full_data['history']:
                    continue
                active_servers[key].full_data['history'][k].append((
                    server.full_data['current'][k][0],
                    -1,
                    server.full_data['current'][k][-1],
                    ))
                newest.full_data['history'][k] += server.full_data['history'][k]

                # Filter the history
                filtered_history = [('', 0, '')]
                for history in reversed(newest.full_data['history'][k]):
                    if filtered_history[-1][0] != history[0]:
                        filtered_history.append(history)

                newest.full_data['history'][k] = list(reversed(filtered_history[1:]))

    for k in keys:
        keys[k] = list(sorted(keys[k]))

    return render(request, 'flumotion.html', locals(), content_type='text/html',
                  context_instance=template.RequestContext(request))
