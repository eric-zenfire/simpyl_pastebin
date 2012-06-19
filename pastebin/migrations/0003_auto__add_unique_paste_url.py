# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'Paste', fields ['url']
        db.create_unique('pastebin_paste', ['url'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Paste', fields ['url']
        db.delete_unique('pastebin_paste', ['url'])


    models = {
        'pastebin.paste': {
            'Meta': {'object_name': 'Paste'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'untitled'", 'max_length': '64'}),
            'tsms': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'user_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64'})
        }
    }

    complete_apps = ['pastebin']
