#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Module contains the models of objects used in the application."""

from django.db import models


class Encoder(models.Model):
    """Amazon EC2 instance which does encoding."""
    group = models.CharField(blank=False, max_length=10)
    ip = models.IPAddressField(blank=False)
    bitrate = models.IntegerField(default=0)
    clients = models.IntegerField(default=0)
    lastseen = models.DateTimeField(auto_now=True, blank=False)


class Collector(models.Model):
    """Amazon EC2 instance which sends data."""
    group = models.CharField(blank=False, max_length=10)
    ip = models.IPAddressField(blank=False)
    lastseen = models.DateTimeField(auto_now=True, blank=False)
