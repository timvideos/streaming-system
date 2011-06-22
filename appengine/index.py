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

twitter = {'slug': 'sydlug'}

# IP Address which are considered "In Room"
LOCALIPS = [
 '^127\.',
 '^74\.125\.56',
]

class StaticTemplate(webapp.RequestHandler):
    """Handler which shows a map of how to get to slug."""
    def get(self, group):
        if not re.match('[a-z/]+', group):
            group = 'slug'

        if '/' in group:
            group, hashtag = group.split('/', 1)
        else:
            hashtag = group

        if hashtag in twitter:
            hashtag = twitter[hashtag]

        template = self.request.get('template', '')
        if not re.match('[a-z]+', template):
            template = 'index'

            # Is the request coming from the room?
            for ipregex in LOCALIPS:
                if re.match(ipregex, self.request.remote_addr):
                    template = 'inroom'

        html5str = self.request.get('flashonly', 'False')
        if html5str.lower()[0] in ('y', 't'):
            html5 = False
        else:
            html5 = True

        hdoffstr = self.request.get('hdoff', 'False')
        if hdoffstr.lower()[0] in ('y', 't'):
            hdoff = True
        else:
            hdoff = False

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(r('templates/%s.html' % template, locals()))
