# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Endpoint.mp4_high_clients'
        db.add_column(u'tracker_endpoint', 'mp4_high_clients',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Endpoint.mp4_high_bitrate'
        db.add_column(u'tracker_endpoint', 'mp4_high_bitrate',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Endpoint.mp4_high_cbitrate'
        db.add_column(u'tracker_endpoint', 'mp4_high_cbitrate',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Endpoint.mp4_low_clients'
        db.add_column(u'tracker_endpoint', 'mp4_low_clients',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Endpoint.mp4_low_bitrate'
        db.add_column(u'tracker_endpoint', 'mp4_low_bitrate',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Endpoint.mp4_low_cbitrate'
        db.add_column(u'tracker_endpoint', 'mp4_low_cbitrate',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Endpoint.mp4_high_clients'
        db.delete_column(u'tracker_endpoint', 'mp4_high_clients')

        # Deleting field 'Endpoint.mp4_high_bitrate'
        db.delete_column(u'tracker_endpoint', 'mp4_high_bitrate')

        # Deleting field 'Endpoint.mp4_high_cbitrate'
        db.delete_column(u'tracker_endpoint', 'mp4_high_cbitrate')

        # Deleting field 'Endpoint.mp4_low_clients'
        db.delete_column(u'tracker_endpoint', 'mp4_low_clients')

        # Deleting field 'Endpoint.mp4_low_bitrate'
        db.delete_column(u'tracker_endpoint', 'mp4_low_bitrate')

        # Deleting field 'Endpoint.mp4_low_cbitrate'
        db.delete_column(u'tracker_endpoint', 'mp4_low_cbitrate')


    models = {
        u'tracker.clientname': {
            'Meta': {'object_name': 'ClientName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        u'tracker.clientnamesandvalues': {
            'Meta': {'unique_together': "(('name', 'value_str', 'value_int', 'value_float'),)", 'object_name': 'ClientNamesAndValues'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracker.ClientName']"}),
            'stat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracker.ClientStats']"}),
            'value_float': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'value_int': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'value_str': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'values'", 'null': 'True', 'to': u"orm['tracker.ClientStringValue']"})
        },
        u'tracker.clientstats': {
            'Meta': {'unique_together': "(('group', 'created_on', 'created_by'),)", 'object_name': 'ClientStats'},
            'created_by': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow', 'db_index': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_and_values': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tracker.ClientName']", 'through': u"orm['tracker.ClientNamesAndValues']", 'symmetrical': 'False'})
        },
        u'tracker.clientstringvalue': {
            'Meta': {'object_name': 'ClientStringValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        },
        u'tracker.endpoint': {
            'Meta': {'unique_together': "(('group', 'ip', 'lastseen'),)", 'object_name': 'Endpoint'},
            'aac_high_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'aac_high_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'aac_high_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flv_high_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flv_high_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flv_high_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flv_low_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flv_low_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flv_low_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'db_index': 'True'}),
            'lastseen': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'loop_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'loop_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp3_high_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp3_high_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp3_high_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp4_high_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp4_high_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp4_high_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp4_low_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp4_low_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp4_low_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ogg_high_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ogg_high_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ogg_high_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'overall_bitrate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'overall_cbitrate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'overall_clients': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'webm_high_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'webm_high_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'webm_high_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'webm_low_bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'webm_low_cbitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'webm_low_clients': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'tracker.flumotion': {
            'Meta': {'unique_together': "(('identifier', 'lastseen'),)", 'object_name': 'Flumotion'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'db_index': 'True'}),
            'lastseen': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'recorded_time': ('django.db.models.fields.FloatField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'})
        },
        u'tracker.servername': {
            'Meta': {'object_name': 'ServerName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        u'tracker.servernamesandvalues': {
            'Meta': {'unique_together': "(('name', 'value_str', 'value_int', 'value_float'),)", 'object_name': 'ServerNamesAndValues'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracker.ServerName']"}),
            'stat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracker.ServerStats']"}),
            'value_float': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'value_int': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'value_str': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'values'", 'null': 'True', 'to': u"orm['tracker.ServerStringValue']"})
        },
        u'tracker.serverstats': {
            'Meta': {'unique_together': "(('group', 'created_on', 'created_by'),)", 'object_name': 'ServerStats'},
            'created_by': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow', 'db_index': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_and_values': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tracker.ServerName']", 'through': u"orm['tracker.ServerNamesAndValues']", 'symmetrical': 'False'})
        },
        u'tracker.serverstringvalue': {
            'Meta': {'object_name': 'ServerStringValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['tracker']