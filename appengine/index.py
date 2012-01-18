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

# AppEngine Imports
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import urlfetch

# Our App imports
import models
from utils.render import render as r

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(['config.ini'])
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


class StaticTemplate(webapp.RequestHandler):
    """Renders the HTML templates."""

    def get(self, group):
        group = check_group(group)
        if not group:
            self.redirect('/')
            return

        channel = CONFIG.get('groups', group)
        justintv = CONFIG.get('justintv', group)

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

        try:
            hashtag = CONFIG.get('twitter', group)
        except ConfigParser.NoOptionError, e:
            hashtag = CONFIG.get('twitter', 'default')

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(r('templates/%s.html' % template, locals()))


class StreamsTemplate(webapp.RequestHandler):
    """Renders the streams.js file."""

    def get(self, group):
        self.response.headers['Content-Type'] = 'text/javascript'
        nocache(self.response.headers)

        group = check_group(group)
        if not group:
            self.out.write("window.src = '/';\n");
            return

        channel = CONFIG.get('groups', group)

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
            self.response.out.write("window.src = '/';\n");
            return
        else:
            # Choose the least loaded server
            server = sorted(active_servers, cmp=lambda a, b: cmp(a.bitrate, b.bitrate))[0].ip

        # Make sure this page isn't cached, otherwise the server load balancing won't work.
        self.response.out.write(r('templates/streams.js', locals()))


class WhatsOnTemplate(webapp.RequestHandler):
    """Renders the whats_on.js file."""

    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'
        nocache(self.response.headers)

        current_time = int(time.time())
        self.response.out.write(r('templates/whats_on.js', locals()))


class RegisterHandler(webapp.RequestHandler):
    """Registers an encoding server into the application."""

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        nocache(self.response.headers)

        secret = self.request.get('secret')
        if secret != CONFIG.get('config', 'secret'):
            self.response.out.write('ERROR SECRET\n')
            return

        group = self.request.get('group')
        if group not in GROUPS:
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

        hashtag = CONFIG.get('twitter', 'default')

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
        nocache(self.response.headers)

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
        nocache(self.response.headers)
        self.response.out.write(self.request.remote_addr)


class ScheduleProxy(webapp.RequestHandler):
    """Get the json schedule from LCA and put it in our domain so we can AJAX it."""

    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'

        schedule = memcache.get('schedule')
        if not schedule:
            schedule = urlfetch.fetch('http://lca2012.linux.org.au/programme/schedule/json').content
            memcache.set('schedule', schedule, 120)
        self.response.out.write(schedule)
