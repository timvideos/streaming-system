# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClientName'
        db.create_table(u'tracker_clientname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'tracker', ['ClientName'])

        # Adding model 'ClientStringValue'
        db.create_table(u'tracker_clientstringvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'tracker', ['ClientStringValue'])

        # Adding model 'ClientNamesAndValues'
        db.create_table(u'tracker_clientnamesandvalues', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value_int', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('value_float', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('stat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracker.ClientStats'])),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracker.ClientName'])),
            ('value_str', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='values', null=True, to=orm['tracker.ClientStringValue'])),
        ))
        db.send_create_signal(u'tracker', ['ClientNamesAndValues'])

        # Adding unique constraint on 'ClientNamesAndValues', fields ['name', 'value_str', 'value_int', 'value_float']
        db.create_unique(u'tracker_clientnamesandvalues', ['name_id', 'value_str_id', 'value_int', 'value_float'])

        # Adding model 'ClientStats'
        db.create_table(u'tracker_clientstats', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow, db_index=True)),
            ('created_by', self.gf('django.db.models.fields.TextField')(db_index=True)),
        ))
        db.send_create_signal(u'tracker', ['ClientStats'])

        # Adding unique constraint on 'ClientStats', fields ['group', 'created_on', 'created_by']
        db.create_unique(u'tracker_clientstats', ['group', 'created_on', 'created_by'])

        # Adding model 'ServerName'
        db.create_table(u'tracker_servername', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'tracker', ['ServerName'])

        # Adding model 'ServerStringValue'
        db.create_table(u'tracker_serverstringvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'tracker', ['ServerStringValue'])

        # Adding model 'ServerNamesAndValues'
        db.create_table(u'tracker_servernamesandvalues', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value_int', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('value_float', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('stat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracker.ServerStats'])),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracker.ServerName'])),
            ('value_str', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='values', null=True, to=orm['tracker.ServerStringValue'])),
        ))
        db.send_create_signal(u'tracker', ['ServerNamesAndValues'])

        # Adding unique constraint on 'ServerNamesAndValues', fields ['name', 'value_str', 'value_int', 'value_float']
        db.create_unique(u'tracker_servernamesandvalues', ['name_id', 'value_str_id', 'value_int', 'value_float'])

        # Adding model 'ServerStats'
        db.create_table(u'tracker_serverstats', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow, db_index=True)),
            ('created_by', self.gf('django.db.models.fields.TextField')(db_index=True)),
        ))
        db.send_create_signal(u'tracker', ['ServerStats'])

        # Adding unique constraint on 'ServerStats', fields ['group', 'created_on', 'created_by']
        db.create_unique(u'tracker_serverstats', ['group', 'created_on', 'created_by'])

        # Adding model 'Endpoint'
        db.create_table(u'tracker_endpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, db_index=True)),
            ('lastseen', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('overall_bitrate', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('overall_cbitrate', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('overall_clients', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('loop_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('loop_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('webm_high_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('webm_high_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('webm_high_cbitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('webm_low_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('webm_low_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('webm_low_cbitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('flv_high_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('flv_high_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('flv_high_cbitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('flv_low_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('flv_low_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('flv_low_cbitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ogg_high_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ogg_high_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ogg_high_cbitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('aac_high_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('aac_high_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('aac_high_cbitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('mp3_high_clients', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('mp3_high_bitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('mp3_high_cbitrate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tracker', ['Endpoint'])

        # Adding unique constraint on 'Endpoint', fields ['group', 'ip', 'lastseen']
        db.create_unique(u'tracker_endpoint', ['group', 'ip', 'lastseen'])

        # Adding model 'Flumotion'
        db.create_table(u'tracker_flumotion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, db_index=True)),
            ('lastseen', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('recorded_time', self.gf('django.db.models.fields.FloatField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'tracker', ['Flumotion'])

        # Adding unique constraint on 'Flumotion', fields ['identifier', 'lastseen']
        db.create_unique(u'tracker_flumotion', ['identifier', 'lastseen'])


    def backwards(self, orm):
        # Removing unique constraint on 'Flumotion', fields ['identifier', 'lastseen']
        db.delete_unique(u'tracker_flumotion', ['identifier', 'lastseen'])

        # Removing unique constraint on 'Endpoint', fields ['group', 'ip', 'lastseen']
        db.delete_unique(u'tracker_endpoint', ['group', 'ip', 'lastseen'])

        # Removing unique constraint on 'ServerStats', fields ['group', 'created_on', 'created_by']
        db.delete_unique(u'tracker_serverstats', ['group', 'created_on', 'created_by'])

        # Removing unique constraint on 'ServerNamesAndValues', fields ['name', 'value_str', 'value_int', 'value_float']
        db.delete_unique(u'tracker_servernamesandvalues', ['name_id', 'value_str_id', 'value_int', 'value_float'])

        # Removing unique constraint on 'ClientStats', fields ['group', 'created_on', 'created_by']
        db.delete_unique(u'tracker_clientstats', ['group', 'created_on', 'created_by'])

        # Removing unique constraint on 'ClientNamesAndValues', fields ['name', 'value_str', 'value_int', 'value_float']
        db.delete_unique(u'tracker_clientnamesandvalues', ['name_id', 'value_str_id', 'value_int', 'value_float'])

        # Deleting model 'ClientName'
        db.delete_table(u'tracker_clientname')

        # Deleting model 'ClientStringValue'
        db.delete_table(u'tracker_clientstringvalue')

        # Deleting model 'ClientNamesAndValues'
        db.delete_table(u'tracker_clientnamesandvalues')

        # Deleting model 'ClientStats'
        db.delete_table(u'tracker_clientstats')

        # Deleting model 'ServerName'
        db.delete_table(u'tracker_servername')

        # Deleting model 'ServerStringValue'
        db.delete_table(u'tracker_serverstringvalue')

        # Deleting model 'ServerNamesAndValues'
        db.delete_table(u'tracker_servernamesandvalues')

        # Deleting model 'ServerStats'
        db.delete_table(u'tracker_serverstats')

        # Deleting model 'Endpoint'
        db.delete_table(u'tracker_endpoint')

        # Deleting model 'Flumotion'
        db.delete_table(u'tracker_flumotion')


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