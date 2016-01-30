#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime

from django.test import TestCase

from tracker import models


class StatsTest(TestCase):
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

    def test_from_dict(self):
        s = models.ClientStats(
            group="",
            created_by="127.0.0.1",
            created_on=self.NOW)
        s.save()
        s.from_dict(self.DATA)

        self.assertListEqual(
            list(str(x) for x in models.ClientName.objects.all().order_by('name')), [
                "stat01.stat02",
                "stat01.stat03",
                "stat01.stat04",
                "stat01.stat05",
                "stat01.stat06",
                "stat07",
                "stat08",
                "stat09",
                "stat10",
                "stat11",
            ])

        self.assertListEqual(
            list(str(x) for x in s.clientnamesandvalues_set.all()), [
                '127.0.0.1@1330308683.0[stat01.stat02] = str',
                '127.0.0.1@1330308683.0[stat01.stat03] = str',
                '127.0.0.1@1330308683.0[stat01.stat04] = 1',
                '127.0.0.1@1330308683.0[stat01.stat05] = 1',
                '127.0.0.1@1330308683.0[stat01.stat06] = 1.0',
                '127.0.0.1@1330308683.0[stat07] = str',
                '127.0.0.1@1330308683.0[stat08] = str',
                '127.0.0.1@1330308683.0[stat09] = 1',
                '127.0.0.1@1330308683.0[stat11] = 1.0',
                '127.0.0.1@1330308683.0[stat10] = 1',
            ])

    def test_unique_strings(self):
        s = models.ClientStats(
            group="",
            created_by="127.0.0.1",
            created_on=self.NOW)
        s.save()
        s.from_dict(self.DATA)
        self.assertEqual(models.ClientName.objects.all().count(), 10)
        self.assertEqual(models.ClientNamesAndValues.objects.all().count(), 10)
        self.assertEqual(models.ClientStringValue.objects.all().count(), 1)

        s = models.ClientStats(
            group="",
            created_by="127.0.0.2",
            created_on=self.NOW)
        s.save()
        s.from_dict(self.DATA)

        self.assertEqual(models.ClientName.objects.all().count(), 10)
        self.assertEqual(models.ClientNamesAndValues.objects.all().count(), 20)
        self.assertEqual(models.ClientStringValue.objects.all().count(), 1)

        updated_data = dict(**self.DATA)
        updated_data['stat10'] = 'Hello!'
        s = models.ClientStats(
            group="",
            created_by="127.0.0.3",
            created_on=self.NOW)
        s.save()
        s.from_dict(updated_data)

        self.assertEqual(models.ClientName.objects.all().count(), 10)
        self.assertEqual(models.ClientNamesAndValues.objects.all().count(), 30)
        self.assertEqual(models.ClientStringValue.objects.all().count(), 2)

        updated_data = dict(**self.DATA)
        updated_data['stat12'] = 'Hello!'
        s = models.ClientStats(
            group="",
            created_by="127.0.0.4",
            created_on=self.NOW)
        s.save()
        s.from_dict(updated_data)

        self.assertEqual(models.ClientName.objects.all().count(), 11)
        self.assertEqual(models.ClientNamesAndValues.objects.all().count(), 41)
        self.assertEqual(models.ClientStringValue.objects.all().count(), 2)
