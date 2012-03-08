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
        views.CONFIG = views.CONFIG.__class__({
            'config': {
                'secret': 's',
            },
            'default' : {
            },
            'a': {},
        })

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

    def test_encoder_register_good(self):
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

        encoders = models.Encoder.objects.all()
        self.assertEqual(1, len(encoders))
        self.assertEqual(1, encoders[0].overall_bitrate)
        self.assertEqual(2, encoders[0].overall_clients)

    def test_encoder_register_good_extended(self):
        factory = RequestFactory()
        request = factory.post(
            '/encoder/register',
            {'group': 'a', 'secret': 's', 'data': """
{
    "overall_bitrate": 1,
    "overall_clients": 2,
    "loop_bitrate": 3,
    "loop_clients": 4,
    "webm_high_bitrate": 5,
    "webm_high_clients": 6,
    "webm_low_bitrate": 7,
    "webm_low_clients": 8,
    "flv_high_bitrate": 9,
    "flv_high_clients": 10,
    "flv_low_bitrate": 11,
    "flv_low_clients": 12,
    "ogg_high_bitrate": 13,
    "ogg_high_clients": 14,
    "aac_high_bitrate": 15,
    "aac_high_clients": 16,
    "mp3_high_bitrate": 17,
    "mp3_high_clients": 18
}
"""})
        response = views.encoder_register(request)
        self.assertPlainText(response, "OK")

        encoders = models.Encoder.objects.all()
        self.assertEqual(1, len(encoders))
        self.assertEqual(1, encoders[0].overall_bitrate)
        self.assertEqual(2, encoders[0].overall_clients)
        self.assertEqual(3, encoders[0].loop_bitrate)
        self.assertEqual(4, encoders[0].loop_clients)
        self.assertEqual(5, encoders[0].webm_high_bitrate)
        self.assertEqual(6, encoders[0].webm_high_clients)
        self.assertEqual(7, encoders[0].webm_low_bitrate)
        self.assertEqual(8, encoders[0].webm_low_clients)
