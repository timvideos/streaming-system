#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Module contains the models of objects used in the application."""

import config
config.setup()

from google.appengine.ext import db

class Encoder(db.Model):
    """Amazon EC2 instance which does encoding."""
    group = db.StringProperty(required=True)
    ip = db.StringProperty(required=True)
    bitrate = db.IntegerProperty(default=0)
    clients = db.IntegerProperty(default=0)
    lastseen = db.DateTimeProperty(auto_now=True, required=True)


class Collector(db.Model):
    """Amazon EC2 instance which sends data."""
    group = db.StringProperty(required=True)
    ip = db.StringProperty(required=True)
    lastseen = db.DateTimeProperty(auto_now=True, required=True)
