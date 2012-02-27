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

        s = models.ClientStat(
            group="",
            created_by="127.0.0.1",
            created_on=self.NOW)
        s.save()
        s.from_dict(self.DATA)

        self.assertListEqual(
            list(str(x) for x in models.Name.objects.all().order_by('name')), [
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
            list(str(x) for x in s.values.order_by(
                'name', 'value_str', 'value_int', 'value_float')), [
            'stat01.stat02 = str',
            'stat01.stat03 = str',
            'stat01.stat04 = 1',
            'stat01.stat05 = 1',
            'stat01.stat06 = 1.0',
            'stat07 = str',
            'stat08 = str',
            'stat09 = 1',
            'stat11 = 1.0',
            'stat10 = 1',
            ])

    def test_unique_values(self):
        s = models.ClientStat(
            group="",
            created_by="127.0.0.1",
            created_on=self.NOW)
        s.save()
        s.from_dict(self.DATA)
        self.assertEqual(models.Value.objects.all().count(), 10)

        s = models.ClientStat(
            group="",
            created_by="127.0.0.2",
            created_on=self.NOW)
        s.save()
        s.from_dict(self.DATA)

        self.assertEqual(models.Value.objects.all().count(), 10)

        updated_data = dict(**self.DATA)
        updated_data['stat10'] = 'Hello!'
        s = models.ClientStat(
            group="",
            created_by="127.0.0.3",
            created_on=self.NOW)
        s.save()
        s.from_dict(updated_data)

        self.assertEqual(models.Value.objects.all().count(), 11)
