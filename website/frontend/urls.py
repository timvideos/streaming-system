#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf.urls.defaults import patterns, include, url

from frontend import views
from . import feeds

urlpatterns = patterns('',
    # Site wide pages
    url(r'^$', views.index),
    url(r'^(monitor)$', views.index),
    url(r'^graphs$', views.overall_stats_graphs),

    # Per room things
    url(r'^', include(feeds.urls)),       # room/rss - Schedule as RSS
    url(r'^(.+)/json$', views.json_feed), # room/json - Schedule as json
    url(r'^(.+)$', views.group),          # room/ - Base page
)
