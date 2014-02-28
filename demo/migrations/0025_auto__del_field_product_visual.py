# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Product.visual'
        db.delete_column(u'spread_product', 'visual')


    def backwards(self, orm):
        # Adding field 'Product.visual'
        db.add_column(u'spread_product', 'visual',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150),
                      keep_default=False)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'efforia.sellable': {
            'Meta': {'object_name': 'Sellable'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 20, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'$$'", 'max_length': '100'}),
            'sellid': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150'})
        },
        u'spread.image': {
            'Meta': {'object_name': 'Image'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '140'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'!%'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"})
        },
        u'spread.playable': {
            'Meta': {'object_name': 'Playable'},
            'category': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 20, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'})
        },
        u'spread.product': {
            'Meta': {'object_name': 'Product', '_ormbases': [u'efforia.Sellable']},
            'category': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'sellable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['efforia.Sellable']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'spread.spreadable': {
            'Meta': {'object_name': 'Spreadable'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'spreaded': ('django.db.models.fields.CharField', [], {'default': "'efforia'", 'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"})
        },
        u'spread.spreaded': {
            'Meta': {'object_name': 'Spreaded'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'!!'", 'max_length': '10'}),
            'spread': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'spreaded': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['spread']