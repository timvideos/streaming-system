#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Simple pages."""

# Python imports
import datetime
import logging
import os
import time
import re

# AppEngine Imports
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import urlfetch

# Our App imports
import models
from utils.render import render as r

twitter = ['@linuxconfau', '#linux.conf.au', '#lca2012']

channels = {
    'caro': 'lca2012-caro',
    'c001': 'lca2012-c001',
    'studio': 'lca2012-studio',
    't101': 'lca2012-t101',
    'studio1': 'lca2012-studio1',
    'studio2': 'lca2012-studio2',
    'studio2': 'lca2012-studio2',
    't102': 'lca2012-t102',
}

# IP Address which are considered "In Room"
LOCALIPS = [
    "^141\.132\.24",
    "^141\.132\.25",
    "^141\.132\.26",
    "^141\.132\.27",
    "^141\.132\.28",
    "^141\.132\.29",
    "^141\.132\.30",
    "^141\.132\.31",
    "^2405:4600:3004:3:",
    "^2405:4600:3004:4:",
]

BACKUP_SERVER = ''


def check_group(group):
    group = group.lower()
    if not re.match('[a-z/]+', group):
        group = None
    if group not in channels:
        group = None
    return group


class StaticTemplate(webapp.RequestHandler):
    """Renders the HTML templates."""

    def get(self, group):
        group = check_group(group)
        if not group:
            self.redirect('/')
            return

        channel = channels[group]
        justintv = channel.replace("-", "_")

        template = self.request.get('template', '')
        if not re.match('[a-z]+', template):
            template = 'index'

            # Is the request coming from the room?
            for ipregex in LOCALIPS:
                if re.match(ipregex, self.request.remote_addr):
                    template = 'inroom'

        screenstr = self.request.get('screen', 'False')
        if screenstr.lower()[0] in ('y', 't'):
            screen = True
        else:
            screen = False

        hashtag = " OR ".join(twitter)

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(r('templates/%s.html' % template, locals()))


class StreamsTemplate(webapp.RequestHandler):
    """Renders the streams.js file."""

    def get(self, group):
        self.response.headers['Content-Type'] = 'text/javascript'

        group = check_group(group)
        if not group:
            self.out.write("window.src = '/';\n");
            return

        channel = channels[group]

        # Get all the active streaming severs for this channel
        ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
        q = models.Encoder.all()
        q.filter('group =', group)

        active_servers = []
        for server in q:
            if server.lastseen < ten_mins_ago:
                continue
            active_servers.append(server)

        if not active_servers:
            # FIXME: Technical difficulties server....
            self.out.write("window.src = '/';\n");
            return
        else:
            # Choose the least loaded server
            server = sorted(active_servers, cmp=lambda a, b: cmp(a.bitrate, b.bitrate))[0].ip

        # Make sure this page isn't cached, otherwise the server load balancing won't work.
        self.response.headers['Pragma'] = 'no-cache'
        self.response.headers['Cache-Control'] = 'no-cache'
        self.response.headers['Expires'] = '-1'
        self.response.out.write(r('templates/streams.js', locals()))


class WhatsOnTemplate(webapp.RequestHandler):
    """Renders the whats_on.js file."""

    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'
        # Make sure this page isn't cached, otherwise the server load balancing won't work.
        self.response.headers['Pragma'] = 'no-cache'
        self.response.headers['Cache-Control'] = 'no-cache'
        self.response.headers['Expires'] = '-1'

        current_time = int(time.time())
        self.response.out.write(r('templates/whats_on.js', locals()))


SECRET='tellnoone'

class RegisterHandler(webapp.RequestHandler):
    """Registers an encoding server into the application."""

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'

        secret = self.request.get('secret')
        if secret != SECRET:
            self.response.out.write('ERROR SECRET\n')
            return

        group = self.request.get('group')
        if group not in channels:
            self.response.out.write('ERROR GROUP\n')
            return

        ip = self.request.get('ip')
        clients = int(self.request.get('clients'))
        bitrate = int(self.request.get('bitrate'))

        s = models.Encoder(
                key_name='%s-%s' % (group, ip),
                group=group,
                ip=ip,
                clients=clients,
                bitrate=bitrate)
        s.put()
        self.response.out.write('OK\n')


class GroupsTemplate(webapp.RequestHandler):
    def get(self, template="groups"):
        # Get the currently active groups
        ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
        groups = set()
        for server in models.Encoder.all():
            if server.lastseen < ten_mins_ago:
                continue
            groups.add(server.group)

        global channels

        hashtag = " OR ".join(twitter)

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(r('templates/%s.html' % template, locals()))


class StatsHandler(webapp.RequestHandler):
    """Print out some stats about registered encoders."""

    def get(self):
        inactive_servers = []
        active_servers = []

        ten_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
        for server in models.Encoder.all():
            if server.lastseen < ten_mins_ago:
                inactive_servers.append(server)
            else:
                active_servers.append(server)

        active_servers = sorted(active_servers, cmp=lambda a, b: cmp((a.group, a.bitrate), (b.group, b.bitrate)))
        inactive_servers = sorted(inactive_servers, cmp=lambda a, b: cmp((a.group, a.bitrate), (b.group, b.bitrate)))

        self.response.headers['Content-Type'] = 'text/html'
        # Make sure this page isn't cached
        self.response.headers['Pragma'] = 'no-cache'
        self.response.headers['Cache-Control'] = 'no-cache'
        self.response.headers['Expires'] = '-1'

        self.response.out.write('<html>')
        self.response.out.write('   <head>')
        self.response.out.write('       <link rel="stylesheet" type="text/css" href="/static/css/stats.css">')
        self.response.out.write('   </head>')
        self.response.out.write('   <body>')
        self.response.out.write('      <h1>Active Servers</h1>')
        self.table(active_servers)
        self.response.out.write('      <h1>Non-Active Servers</h1>')
        self.table(inactive_servers)
        self.response.out.write('   </body>')
        self.response.out.write('</html>')

    def table(self, servers):
        self.response.out.write('       <table>')
        self.response.out.write('           <tr>')
        self.response.out.write('               <th>ip</th>')
        self.response.out.write('               <th>group</th>')
        self.response.out.write('               <th>clients</th>')
        self.response.out.write('               <th>bitrate (bits/s)</th>')
        self.response.out.write('               <th>bitrate (megabits/s)</th>')
        self.response.out.write('               <th>lastseen</th>')
        self.response.out.write('           </tr>')
        for server in servers:
            self.response.out.write('           <tr>')
            self.response.out.write('               <td>%s</td>' % server.ip)
            self.response.out.write('               <td>%s</td>' % server.group)
            self.response.out.write('               <td>%i</td>' % server.clients)
            self.response.out.write('               <td>%i b/s</td>' % server.bitrate)
            self.response.out.write('               <td>%.2f MB/s</td>' % (server.bitrate/1e6))
            self.response.out.write('               <td>%s</td>' % server.lastseen)
            self.response.out.write('           </tr>')
        self.response.out.write('       </table>')


class IPHandler(webapp.RequestHandler):
    """Print out the callers IP."""

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        # Make sure this page isn't cached
        self.response.headers['Pragma'] = 'no-cache'
        self.response.headers['Cache-Control'] = 'no-cache'
        self.response.headers['Expires'] = '-1'
        self.response.out.write(self.request.remote_addr)


class ScheduleProxy(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'
        # Make sure this page isn't cached, otherwise the server load balancing won't work.
        #self.response.headers['Pragma'] = 'no-cache'
        #self.response.headers['Cache-Control'] = 'no-cache'
        #self.response.headers['Expires'] = '-1'

        schedule = memcache.get('schedule')
        if not schedule:
            schedule = urlfetch.fetch('http://lca2012.linux.org.au/programme/schedule/json').content
            memcache.set('schedule', schedule, 120)
        self.response.out.write(schedule)
