#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

"""Module contains the models of objects used in the application."""

import datetime
import time

from django.db import models



# These models make up the stats recording system.
class Name(models.Model):
    """Name of a field on stat dictionary."""
    name = models.CharField(max_length=255, db_index=True)

    def __repr__(self):
        return "%s(%s)" % (self.name, self.pk)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("name",),)


class Value(models.Model):
    """Value of a field on a stat dictionary."""
    name = models.ForeignKey('Name', db_index=True)
    value_str = models.TextField(blank=True, null=True, db_index=True)
    value_int = models.IntegerField(blank=True, null=True, db_index=True)
    value_float = models.FloatField(blank=True, null=True, db_index=True)

    class Meta:
        unique_together = (("name", "value_str", "value_int", "value_float"),)

    @staticmethod
    def value_dict(value):
        d = {}
        if isinstance(value, (str, unicode)):
            d['value_str'] = value
        elif isinstance(value, (int, long)):
            d['value_int'] = value
        elif isinstance(value, float):
            d['value_float'] = value
        else:
            raise SyntaxError("Unknown type for %s (%r)" % (type(value), value))
        return d

    def value_get(self):
        if self.value_str is not None:
            return self.value_str
        elif self.value_int is not None:
            return self.value_int
        elif self.value_float is not None:
            return self.value_float
        else:
            return None

    def value_set(self, value):
        for k, v in self.value_dict(value):
            setattr(self, k, v)

    value = property(value_get, value_set)

    def __unicode__(self):
        return "%s = %s" % (self.name, self.value)


class Stat(models.Model):
    """Some stats recorded from a client."""
    group = models.CharField(blank=False, max_length=10)
    created_on = models.DateTimeField(default=datetime.datetime.utcnow, db_index=True)
    created_by = models.TextField(db_index=True)
    values = models.ManyToManyField('Value')

    class Meta:
        abstract = True
        unique_together = (("group", "created_on", "created_by"),)

    def __unicode__(self):
        return "%s@%s" % (
            self.created_by, time.mktime(self.created_on.timetuple()))

    def from_dict(self, d, prefix=""):
        for key, item in d.items():
            if isinstance(item, dict):
                self.from_dict(item, key+".")
            else:
                self.values.add(
                    Value.objects.get_or_create(
                        name=Name.objects.get_or_create(
                            name="%s%s" % (prefix, key))[0],
                        **Value.value_dict(item))[0])


class ClientStat(Stat):
    pass


# These models make up the broadcasting reporting system.
class Encoder(models.Model):
    """A heavy duty instance which does encoding."""
    group = models.CharField(blank=False, max_length=10)
    ip = models.IPAddressField(blank=False)
    lastseen = models.DateTimeField(auto_now=True, blank=False)

    overall_bitrate = models.IntegerField(default=0)
    overall_clients = models.IntegerField(default=0)

    # Loop back is not included in the overall values
    loop_bitrate = models.IntegerField(blank=True)
    loop_clients = models.IntegerField(blank=True)

    # Keep these values in-sync with the encoder.xml config
    # -- HTML5's webm
    loop_webm_high_clients = models.IntegerField(blank=True)
    loop_webm_high_bitrate = models.IntegerField(blank=True)
    loop_webm_low_clients = models.IntegerField(blank=True)
    loop_webm_low_bitrate = models.IntegerField(blank=True)
    # -- H.264 flash
    loop_flv_high_clients = models.IntegerField(blank=True)
    loop_flv_high_bitrate = models.IntegerField(blank=True)
    loop_flv_low_clients = models.IntegerField(blank=True)
    loop_flv_low_bitrate = models.IntegerField(blank=True)
    # -- Audio only versions
    loop_ogg_clients = models.IntegerField(blank=True)
    loop_ogg_bitrate = models.IntegerField(blank=True)
    loop_aac_high_clients = models.IntegerField(blank=True)
    loop_aac_high_bitrate = models.IntegerField(blank=True)
    loop_mp3_high_clients = models.IntegerField(blank=True)
    loop_mp3_high_bitrate = models.IntegerField(blank=True)

    class Meta:
        unique_together = (("group", "ip"),)


class Collector(models.Model):
    """Amazon EC2 instance which sends data."""
    group = models.CharField(blank=False, max_length=10)
    ip = models.IPAddressField(blank=False)
    lastseen = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        unique_together = (("group", "ip"),)
