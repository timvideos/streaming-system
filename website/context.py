#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf import settings as django_settings


def settings(request, *args, **kw):
    """Adds the django settings into the template context as 'SETTINGS'.

    The most useful one, DEBUG is also added into the context directly.
    """
    return {'SETTINGS': django_settings, 'DEBUG': django_settings.DEBUG}
