#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf.urls.defaults import patterns, include, url

from tracker import views

urlpatterns = patterns('',
    # Endpoints which the frontend uses to find streaming servers we are
    # tracking.
    url(r'^streams.js$', views.streams),
    url(r'^(.*)/stream.js$', views.stream),


    # Endpoints which report details about running flumotion servers in the
    # pipeline.
    url(r'^flumotion/log$', views.flumotion_logging), # Log the status
    url(r'^flumotion/stats$', views.flumotion_stats), # View the status

    # Endpoints for registering streaming to client servers and recording their
    # information.
    url(r'^endpoint/register$', views.endpoint_register),
    url(r'^endpoint/logs$', views.endpoint_logs),
    url(r'^endpoint/stats$', views.endpoint_stats),

    # Endpoints for graphing.
    url(r'^graphs$', views.overall_stats_graphs),
    url(r'^overall-stats.json$', views.overall_stats_json),

    # FIXME: This endpoint should probably be a different app?
    # Endpoint for logging client stats about a given stream
    url(r'^(.*)/log$', views.client_stats),
   )
