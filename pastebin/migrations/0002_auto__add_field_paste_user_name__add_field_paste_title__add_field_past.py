# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Paste.user_name'
        db.add_column('pastebin_paste', 'user_name', self.gf('django.db.models.fields.CharField')(default='', max_length=64), keep_default=False)

        # Adding field 'Paste.title'
        db.add_column('pastebin_paste', 'title', self.gf('django.db.models.fields.CharField')(default='untitled', max_length=64), keep_default=False)

        # Adding field 'Paste.tsms'
        db.add_column('pastebin_paste', 'tsms', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Paste.user_name'
        db.delete_column('pastebin_paste', 'user_name')

        # Deleting field 'Paste.title'
        db.delete_column('pastebin_paste', 'title')

        # Deleting field 'Paste.tsms'
        db.delete_column('pastebin_paste', 'tsms')


    models = {
        'pastebin.paste': {
            'Meta': {'object_name': 'Paste'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'untitled'", 'max_length': '64'}),
            'tsms': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64'})
        }
    }

    complete_apps = ['pastebin']
