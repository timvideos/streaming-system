#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Default handler."""

import config
config.setup()

# AppEngine imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# Import the actual handlers
import index

application = webapp.WSGIApplication(
  [('/(.*)/streams.js', index.StreamsTemplate),
   ('/whats_on.js', index.WhatsOnTemplate),
   ('/schedule.js', index.ScheduleProxy),
   ('/register', index.RegisterHandler),
   ('/stats', index.StatsHandler),
   ('/(.+)', index.StaticTemplate),
   ('/', index.GroupsTemplate),
   ],
  debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
