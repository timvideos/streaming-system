#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import simplejson
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.test.client import RequestFactory

from tracker import views, models


class EncoderRegisterTest(TestCase):
    maxDiff = None

    def setUp(self):
        views.CONFIG = {
            'config': {
                'secret': 's',
            },
            'a': {},
        }

    def assertPlainText(self, response, text):
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertTrue(
            response.content.startswith(text),
            "%s != %s" % (text, response.content))

    def test_encoder_common_invalid_group(self):
        factory = RequestFactory()
        request = factory.post(
            '/encoder/register',
            {'group': 'b', 'secret': 's'})
        response, group, ip = views.encoder_common(request)
        self.assertNotEqual(response, None)

    def test_encoder_common_invalid_secret(self):
        factory = RequestFactory()
        request = factory.post(
            '/encoder/register',
            {'group': 'a', 'secret': 'b'})
        response, group, ip = views.encoder_common(request)
        self.assertNotEqual(response, None)

    def test_encoder_register_bad_json(self):
        factory = RequestFactory()
        request = factory.post(
            '/encoder/register',
            {'group': 'a', 'secret': 's', 'data': '{'})

        response = views.encoder_register(request)
        self.assertPlainText(response, "ERROR")

    def test_encoder_register_bad_data_ip(self):
        factory = RequestFactory()
        request = factory.post(
            '/encoder/register',
            {'group': 'a', 'secret': 's', 'data': """{"ip": "10.1.1.1"}"""})

        response = views.encoder_register(request)
        self.assertPlainText(response, "ERROR Assert")

    def test_encoder_register_bad_data_group(self):
        factory = RequestFactory()
        request = factory.post(
            '/encoder/register',
            {'group': 'a', 'secret': 's', 'data': """{"group": "a"}"""})

        response = views.encoder_register(request)
        self.assertPlainText(response, "ERROR Assert")

    def test_encoder_register_bad_data_group(self):
        factory = RequestFactory()
        request = factory.post(
            '/encoder/register',
            {'group': 'a', 'secret': 's', 'data': """
{
    "overall_bitrate": 1,
    "overall_clients": 2
}
"""})
        response = views.encoder_register(request)
        self.assertPlainText(response, "OK")
