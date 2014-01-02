#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf.urls.defaults import patterns, include, url

from frontend import views
from . import feeds

urlpatterns = patterns('',
    url(r'^(monitor)$', views.index),
    url(r'^', include(feeds.urls)),
    url(r'^(.+)/json$', views.json_feed),
    url(r'^(.+)$', views.group),
    url(r'^$', views.index),
   )
