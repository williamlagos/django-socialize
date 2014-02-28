# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'EventSpread.event'
        db.delete_column('spread_eventspread', 'event_id')

        # Adding field 'EventSpread.spreaded'
        db.add_column('spread_eventspread', 'spreaded', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='+', to=orm['spread.Event']), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'EventSpread.event'
        db.add_column('spread_eventspread', 'event', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='+', to=orm['spread.Event']), keep_default=False)

        # Deleting field 'EventSpread.spreaded'
        db.delete_column('spread_eventspread', 'spreaded_id')


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
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.date(2012, 6, 20)', 'auto_now_add': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.date(2012, 6, 20)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_event': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'rsvp_status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.date(2012, 6, 20)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'spread.eventspread': {
            'Meta': {'object_name': 'EventSpread'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Spreadable']"}),
            'spreaded': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Event']"})
        },
        'spread.spreadable': {
            'Meta': {'object_name': 'Spreadable'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'spreaded': ('django.db.models.fields.CharField', [], {'default': "'efforia'", 'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'spread.spreadablespread': {
            'Meta': {'object_name': 'SpreadableSpread'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Spreadable']"}),
            'spreaded': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['spread.Spreadable']"})
        }
    }

    complete_apps = ['spread']
