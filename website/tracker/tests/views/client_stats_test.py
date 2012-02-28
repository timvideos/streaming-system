#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import simplejson
import datetime

from django.test import TestCase
from django.test.client import RequestFactory

from tracker import views, models


class ClientStatsHelpersTest(TestCase):

    def test_generate_salt(self):
        previous_salts = []
        for i in range(0, 1000):
            new_salt = views.generate_salt()
            self.assertTrue(new_salt not in previous_salts)
            previous_salts.append(new_salt)

    def test_user_key(self):
        factory = RequestFactory()
        request = factory.post('/clientstats', {})
        request.META['HTTP_USER_AGENT'] = 'Testing'
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        keya = views.user_key(request)
        keyb = views.user_key(request)
        self.assertNotEqual(
            keya, keyb,
            'user_key should generate *different* keys for same input when not'
            ' given a salt.')

        keya = views.user_key(request, salt='abc123')
        keyb = views.user_key(request, salt='abc123')
        self.assertEqual(
            keya, keyb,
            'user_key should generate thhe *same* keys for same input when'
            ' a salt is given.')

class ClientStatsTest(TestCase):
    maxDiff = None

    NOW = datetime.datetime.strptime(
        "2012/02/27 13:11:23", "%Y/%m/%d %H:%M:%S")
    DATA = {
        'stat01': {
            'stat02': 'str',
            'stat03': u'str',
            'stat04': 1,
            'stat05': 1L,
            'stat06': 1.0,
            },
        'stat07': 'str',
        'stat08': u'str',
        'stat09': 1,
        'stat10': 1L,
        'stat11': 1.0,
        }

    def assertJSON(self, response):
        self.assertEqual(response['Content-Type'], 'application/javascript')
        return simplejson.loads(response.content)

    def assertErrorCode(self, content):
        # This should be a error, hence between 0 and 1024
        self.assertGreater(content['code'], 0)
        self.assertLess(content['code'], 1024)

    def assertWarningCode(self, content):
        # This should be a warning, hence greater than 1024
        self.assertGreater(content['code'], 1024)

    def assertRetry(self, content):
        # We want the client to request again right away
        self.assertEqual(content['next'], 0)

    def assertCookie(self, response, cookie_name, cookie_value):
        pass

    def setUp(self):
        views.CONFIG = {'config': {}, 'a': {}}

    def test_client_common_error_on_get(self):
        factory = RequestFactory()
        request = factory.get('/clientstats')
        response, group, key = views.client_common(request, 'a')
        self.assertNotEqual(response, None)
        #self.assertRedirects(response, '/', status_code=301)

    def test_client_common_error_on_missing_cookie(self):
        factory = RequestFactory()
        request = factory.post('/clientstats', {})
        request.META['HTTP_USER_AGENT'] = 'Testing'
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        response, group, key = views.client_common(request, 'a')
        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

        content = simplejson.loads(response.content)
        self.assertWarningCode(content)
        self.assertRetry(content)
        self.assertCookie(response, 'user', 'key')

    def test_client_common_error_on_broken_cookie(self):
        factory = RequestFactory()
        request = factory.post('/clientstats', {})
        request.META['HTTP_USER_AGENT'] = 'Testing'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.COOKIES['user'] = views.user_key(request, salt='abc123')

        # Change this header so the user_key shouldn't match anymore
        request.META['HTTP_USER_AGENT'] = 'Testing Modified'

        response, group, key = views.client_common(request, 'a')
        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

        content = self.assertJSON(response)
        self.assertWarningCode(content)
        self.assertRetry(content)
        self.assertCookie(response, 'user', '')

    def test_client_success(self):
        factory = RequestFactory()
        request = factory.post('/clientstats/a', {'data': simplejson.dumps({})})
        request.META['HTTP_USER_AGENT'] = 'Testing'
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        user = views.user_key(request, salt='abc123')
        request.COOKIES['user'] = user

        response = views.client_stats(request, 'a', _now=self.NOW)

        content = self.assertJSON(response)
        # Should be a success
        self.assertEqual(content['code'], 0)
        # Give us more stats at a later stage
        self.assertGreater(content['next'], 0)

        # Assert some stuff is in the database
        stats = models.ClientStats.objects.get(created_by=user, created_on=self.NOW)
        # FIXME: This changes everytime the list of default saved values changes.
        self.assertListEqual(
            ['ip', 'user-agent'],
            list(str(x) for x in stats.name_and_values.all()))
