#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Simple pages."""

# Python imports
import os
import logging
import re

# AppEngine Imports
from google.appengine.ext import webapp

# Our App imports
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
]

class StaticTemplate(webapp.RequestHandler):
    """Handler which shows a map of how to get to slug."""
    def get(self, group):
        if not re.match('[a-z/]+', group):
            group = 'caro'

        if group in channels:
            channel = channels[group]
        else:
            channel = 'caro'

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
