# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Paste'
        db.create_table('pastebin_paste', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=1000000)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('pastebin', ['Paste'])


    def backwards(self, orm):
        
        # Deleting model 'Paste'
        db.delete_table('pastebin_paste')


    models = {
        'pastebin.paste': {
            'Meta': {'object_name': 'Paste'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['pastebin']
