#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf.urls.defaults import patterns, include, url

from website.frontend import views

urlpatterns = patterns('',
    url(r'^whats_on.js$', views.whats_on),
    url(r'^schedule.js$', views.schedule),
    url(r'^register$', views.register),
    url(r'^stats$', views.stats),
    url(r'^(monitor)$', views.groups),
    url(r'^ip$', views.ip),
    url(r'^(.*)/streams.js$', views.streams),
    url(r'^(.+)$', views.base),
    url(r'^$', views.groups),
   )
