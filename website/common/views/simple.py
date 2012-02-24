#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.views.decorators.cache import never_cache
from django.views.generic.simple import redirect_to

@never_cache
def never_cache_redirect_to(*args, **kw):
    return redirect_to(*args, **kw)
