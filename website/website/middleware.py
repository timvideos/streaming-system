#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

from django.conf import settings


class SetHttpRealIp(object):
    def process_request(self, request):
        if not settings.DEBUG:
            assert 'HTTP_X_REAL_IP' in request.META
            return
        else:
            if request.GET.get('REMOTE_ADDR', None):
                request.META['HTTP_X_REAL_IP'] = request.GET['REMOTE_ADDR']
                return
            elif request.POST.get('REMOTE_ADDR', None):
                request.META['HTTP_X_REAL_IP'] = request.POST['REMOTE_ADDR']
                return
        request.META['HTTP_X_REAL_IP'] = request.META['REMOTE_ADDR']
        return
