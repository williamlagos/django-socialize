# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'PlayablePurchased'
        db.delete_table(u'spread_playablepurchased')

        # Deleting model 'Schedule'
        db.delete_table(u'spread_schedule')

        # Deleting model 'Page'
        db.delete_table(u'spread_page')

        # Deleting model 'Event'
        db.delete_table(u'spread_event')

        # Adding model 'Cart'
        db.create_table(u'spread_cart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='++', max_length=2)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['spread.Product'])),
        ))
        db.send_create_signal(u'spread', ['Cart'])

        # Adding model 'Deliverable'
        db.create_table(u'spread_deliverable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['spread.Product'])),
            ('buyer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('code', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
            ('mail_code', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
            ('height', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('length', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('width', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('receiver', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 5, 2, 0, 0), auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'spread', ['Deliverable'])

        # Adding model 'Product'
        db.create_table(u'spread_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=150)),
            ('seller', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('category', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('credit', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('visual', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 5, 2, 0, 0), auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'spread', ['Product'])


    def backwards(self, orm):
        # Adding model 'PlayablePurchased'
        db.create_table(u'spread_playablepurchased', (
            ('name', self.gf('django.db.models.fields.CharField')(default='$>', max_length=10)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner', to=orm['auth.User'])),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(related_name='video', to=orm['spread.Playable'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('spread', ['PlayablePurchased'])

        # Adding model 'Schedule'
        db.create_table(u'spread_schedule', (
            ('play', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['spread.Playable'])),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 3, 19, 0, 0), auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('spread', ['Schedule'])

        # Adding model 'Page'
        db.create_table(u'spread_page', (
            ('name', self.gf('django.db.models.fields.CharField')(default='!#', max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')(default='')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('spread', ['Page'])

        # Adding model 'Event'
        db.create_table(u'spread_event', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 3, 19, 0, 0))),
            ('name', self.gf('django.db.models.fields.CharField')(default='@@', max_length=50)),
            ('rsvp_status', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 3, 19, 0, 0), auto_now_add=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 3, 19, 0, 0))),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_event', self.gf('django.db.models.fields.CharField')(default='', max_length=15)),
            ('location', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
        ))
        db.send_create_signal('spread', ['Event'])

        # Deleting model 'Cart'
        db.delete_table(u'spread_cart')

        # Deleting model 'Deliverable'
        db.delete_table(u'spread_deliverable')

        # Deleting model 'Product'
        db.delete_table(u'spread_product')


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
        u'spread.cart': {
            'Meta': {'object_name': 'Cart'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'++'", 'max_length': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['spread.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"})
        },
        u'spread.deliverable': {
            'Meta': {'object_name': 'Deliverable'},
            'buyer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 2, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'mail_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['spread.Product']"}),
            'receiver': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '1'})
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
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 2, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'})
        },
        u'spread.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 2, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150'}),
            'seller': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'})
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