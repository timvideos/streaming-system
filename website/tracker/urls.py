#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf.urls.defaults import patterns, include, url

from tracker import views

urlpatterns = patterns('',
    url(r'^flumotion/log$', views.flumotion_logging),
    url(r'^flumotion/stats$', views.flumotion_stats),
    url(r'^encoder/register$', views.encoder_register),
    url(r'^encoder/logs$', views.encoder_logs),
    url(r'^(.*)/stats$', views.client_stats),
    url(r'^(.*)/streams.js$', views.streams),
    url(r'^stats$', views.stats),
   )
