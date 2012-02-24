#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf.urls.defaults import patterns, include, url

from frontend import views

urlpatterns = patterns('',
    url(r'^(monitor)$', views.index),
    url(r'^(.+)$', views.group),
    url(r'^$', views.index),
   )
