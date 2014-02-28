# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Spreaded'
        db.create_table('spread_spreaded', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='!!', max_length=10)),
            ('user', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('spread', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('spreaded', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('spread', ['Spreaded'])


    def backwards(self, orm):
        # Deleting model 'Spreaded'
        db.delete_table('spread_spreaded')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'spread.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 26, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 26, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_event': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'@@'", 'max_length': '50'}),
            'rsvp_status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 26, 0, 0)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.eventspread': {
            'Meta': {'object_name': 'EventSpread'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'@$'", 'max_length': '10'}),
            'spread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Spreadable']"}),
            'spreaded': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Event']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.image': {
            'Meta': {'object_name': 'Image'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'!%'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'!#'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.playable': {
            'Meta': {'object_name': 'Playable'},
            'category': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 26, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'})
        },
        'spread.playablefan': {
            'Meta': {'object_name': 'PlayableFan'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Playable']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.playablepurchased': {
            'Meta': {'object_name': 'PlayablePurchased'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'$>'", 'max_length': '10'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'video'", 'to': "orm['spread.Playable']"})
        },
        'spread.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 26, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'play': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Playable']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.spreadable': {
            'Meta': {'object_name': 'Spreadable'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'spreaded': ('django.db.models.fields.CharField', [], {'default': "'efforia'", 'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.spreadablespread': {
            'Meta': {'object_name': 'SpreadableSpread'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'@!'", 'max_length': '10'}),
            'spread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Spreadable']"}),
            'spreaded': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Spreadable']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"})
        },
        'spread.spreaded': {
            'Meta': {'object_name': 'Spreaded'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'!!'", 'max_length': '10'}),
            'spread': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'spreaded': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'user': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['spread']