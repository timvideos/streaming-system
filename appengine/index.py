#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Simple pages."""

# Python imports
import os

# AppEngine Imports
from google.appengine.ext import webapp

# Our App imports
from utils.render import render as r


class StaticTemplate(webapp.RequestHandler):
    """Handler which shows a map of how to get to slug."""
    def get(self, filename='index'):
        template = 'templates/%s.html' % filename
        if os.path.exists(template):
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(r(template, {}))
        else:
            self.redirect('/')
