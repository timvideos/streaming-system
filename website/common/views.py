#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView

class NeverCacheRedirectView(RedirectView):
    permanent = False

    @never_cache
    def get(self, request, *args, **kwargs):
        return RedirectView.get(self, request, *args, **kwargs)
