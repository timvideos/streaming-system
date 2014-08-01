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
    name = models.CharField(max_length=255, db_index=True, unique=True)

    def __repr__(self):
        return "%s(%s)" % (self.name, self.pk)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class StringValue(models.Model):
    """A string value of a field on the stat dictionary."""
    value = models.TextField(db_index=True, unique=True)

    class Meta:
        abstract = True


class NamesAndValues(models.Model):
    """Value of a field on a stat dictionary."""
    # stat = models.ForeignKey('$(name)sStat', db_index=True) # Defined in subclass
    # name = models.ForeignKey('$(name)sName', db_index=True) # Defined in subclass

    # Numbers are stored locally because the cost of a reference is more then
    # just storing the number.
    value_int = models.IntegerField(blank=True, null=True, db_index=True)
    value_float = models.FloatField(blank=True, null=True, db_index=True)
    # Strings are stored in another table because they are often expensive.
    #value_str = models.ForeignKey('ValueString', blank=True, null=True, db_index=True, related_name="values") # Defined in subclass

    class Meta:
        abstract = True
        unique_together = (("name", "value_str", "value_int", "value_float"),)

    @classmethod
    def value_dict(cls, value):
        d = {}
        if isinstance(value, (str, unicode)):
            d['value_str'] = cls.StringValueModel.objects.get_or_create(value=value)[0]
        elif isinstance(value, (int, long)):
            d['value_int'] = value
        elif isinstance(value, float):
            d['value_float'] = value
        else:
            raise SyntaxError("Unknown type for %s (%r)" % (type(value), value))
        return d

    def value_get(self):
        if self.value_str is not None:
            return self.value_str.value
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
        return "%s[%s] = %s" % (self.stat, self.name, self.value)


class Stats(models.Model):
    """Some stats recorded from a client."""
    group = models.CharField(blank=False, max_length=10)
    created_on = models.DateTimeField(default=datetime.datetime.utcnow, db_index=True)
    created_by = models.TextField(db_index=True)
    # name_and_values = models.ManyToManyField('$(name)sName', through='$(name)sNamesAndValues') # Defined in subclass

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
                nav = self.NamesAndValuesModel.objects.get_or_create(
                    stat=self,
                    name=self.NameModel.objects.get_or_create(
                        name="%s%s" % (prefix, key))[0],
                    **self.NamesAndValuesModel.value_dict(item))[0]

STATS_TABLES = """
class %(name)sName(Name):
    class Meta(Name.Meta):
        pass

class %(name)sStringValue(StringValue):
    class Meta(StringValue.Meta):
        pass

class %(name)sNamesAndValues(NamesAndValues):
    NameModel = %(name)sName
    StringValueModel = %(name)sStringValue

    stat = models.ForeignKey('%(name)sStats', db_index=True)
    name = models.ForeignKey('%(name)sName', db_index=True) # Defined in subclass

    value_str = models.ForeignKey('%(name)sStringValue', blank=True, null=True, db_index=True, related_name="values")

    class Meta(NamesAndValues.Meta):
        pass

class %(name)sStats(Stats):
    NameModel = %(name)sName
    NamesAndValuesModel = %(name)sNamesAndValues

    name_and_values = models.ManyToManyField('%(name)sName', through='%(name)sNamesAndValues')

    class Meta(Stats.Meta):
        pass
"""

exec(STATS_TABLES % {'name': 'Client'})
exec(STATS_TABLES % {'name': 'Server'})

class Endpoint(models.Model):
    """
    An endpoint server is one which is sending data to end users. It might be
    an encoder in smaller setups, or in more advanced systems an amplifier.

    Endpoints are registered for a given group. They should only be serving a
    single group. They report stats and logs about the end users that are
    connected to them.

    Endpoints need to continously re-register on the sever otherwise they are
    considered dead.

    The IP address of the endpoint will be sent to end users. Make sure it's
    public!
    """
    group = models.CharField(blank=False, max_length=10, db_index=True)
    ip = models.IPAddressField(blank=False, db_index=True)
    lastseen = models.DateTimeField(auto_now=True, blank=False, db_index=True)

    overall_bitrate = models.IntegerField(default=0)
    overall_cbitrate = models.IntegerField(default=0)
    overall_clients = models.IntegerField(default=0)

    # Loop back is not included in the overall values
    loop_bitrate = models.IntegerField(blank=True, null=True)
    loop_clients = models.IntegerField(blank=True, null=True)

    # Keep these values in-sync with the encoder.xml config
    # -- HTML5's webm
    webm_high_clients = models.IntegerField(blank=True, null=True)
    webm_high_bitrate = models.IntegerField(blank=True, null=True)
    webm_high_cbitrate = models.IntegerField(blank=True, null=True)
    webm_low_clients = models.IntegerField(blank=True, null=True)
    webm_low_bitrate = models.IntegerField(blank=True, null=True)
    webm_low_cbitrate = models.IntegerField(blank=True, null=True)
    # -- H.264 mp4
    mp4_high_clients = models.IntegerField(blank=True, null=True)
    mp4_high_bitrate = models.IntegerField(blank=True, null=True)
    mp4_high_cbitrate = models.IntegerField(blank=True, null=True)
    mp4_low_clients = models.IntegerField(blank=True, null=True)
    mp4_low_bitrate = models.IntegerField(blank=True, null=True)
    mp4_low_cbitrate = models.IntegerField(blank=True, null=True)
    # -- H.264 flash
    flv_high_clients = models.IntegerField(blank=True, null=True)
    flv_high_bitrate = models.IntegerField(blank=True, null=True)
    flv_high_cbitrate = models.IntegerField(blank=True, null=True)
    flv_low_clients = models.IntegerField(blank=True, null=True)
    flv_low_bitrate = models.IntegerField(blank=True, null=True)
    flv_low_cbitrate = models.IntegerField(blank=True, null=True)
    # -- Audio only versions
    ogg_high_clients = models.IntegerField(blank=True, null=True)
    ogg_high_bitrate = models.IntegerField(blank=True, null=True)
    ogg_high_cbitrate = models.IntegerField(blank=True, null=True)
    aac_high_clients = models.IntegerField(blank=True, null=True)
    aac_high_bitrate = models.IntegerField(blank=True, null=True)
    aac_high_cbitrate = models.IntegerField(blank=True, null=True)
    mp3_high_clients = models.IntegerField(blank=True, null=True)
    mp3_high_bitrate = models.IntegerField(blank=True, null=True)
    mp3_high_cbitrate = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (("group", "ip", "lastseen"),)

    @classmethod
    def active(cls, group=None, delta=datetime.timedelta(minutes=1)):
        """Get the currently active encoders.

        Args:
            group: Group to get active servers for. Defaults to all groups.
            delta: A time delta describing how long ago the encoder must have
                   registered to be considered active. Defaults to 1 minute
                   ago.

        Returns:
            A real list of Endpoint objects.
        """
        # Get all the active streaming severs for this channel
        lastseen_after = datetime.datetime.now() - delta
        q = cls.objects.order_by('group', 'ip', '-lastseen'
            ).filter(lastseen__gte=lastseen_after
            )
        if group:
            q = q.filter(group__exact=group)


        distinct_support = True
        try:
            qd = q.distinct('group', 'ip')
            return list(qd)
        except NotImplementedError, e:
            distinct_endpoints = {}
            for endpoint in q:
                key = (endpoint.group, endpoint.ip)

                if key not in distinct_endpoints:
                    distinct_endpoints[key] = endpoint

            return list(distinct_endpoints.values())


class Flumotion(models.Model):
    """A flumotion instance.

    A flumotion instance somewhere in the video processing pipeline. The
    instances should update their information regularly.

    Most setups will have three flumotion types per group they are serving.
    They are:
        * collect - The flumotion instance doing the "on the ground" capture
                    and transmitting a high quality version to the encoding
                    server.
        * encoder - Heavy duty server which has a flumotion instance doing the
                    conversion from the high quality version from the collect
                    instance to the versions needed by clients.
        * amplifer - A light weight instance which acts as an simple TCP
                     amplifier. Used when the number of clients is more then
                     can be handled by the network card in the encoder.
    """
    identifier = models.CharField(blank=False, max_length=255, db_index=True)
    type = models.CharField(blank=True, max_length=255, db_index=True)

    group = models.CharField(blank=False, max_length=10, db_index=True)
    ip = models.IPAddressField(blank=False, db_index=True)
    lastseen = models.DateTimeField(auto_now=True, blank=False, db_index=True)

    recorded_time = models.FloatField(blank=False)
    data = models.TextField(blank=False)

    class Meta:
        unique_together = (("identifier", "lastseen"),)
