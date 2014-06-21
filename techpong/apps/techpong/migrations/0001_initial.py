# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'techpong_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['techpong.Company'], null=True, blank=True)),
        ))
        db.send_create_signal(u'techpong', ['UserProfile'])

        # Adding model 'Company'
        db.create_table(u'techpong_company', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('joined_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('image_url', self.gf('django.db.models.fields.URLField')(max_length=255)),
        ))
        db.send_create_signal(u'techpong', ['Company'])

        # Adding model 'Player'
        db.create_table(u'techpong_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['techpong.Company'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('rating', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal(u'techpong', ['Player'])

        # Adding model 'Match'
        db.create_table(u'techpong_match', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['techpong.Company'])),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_winner', to=orm['techpong.Player'])),
            ('loser', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_loser', to=orm['techpong.Player'])),
            ('winner_rating_before', self.gf('django.db.models.fields.FloatField')()),
            ('loser_rating_before', self.gf('django.db.models.fields.FloatField')()),
            ('winner_rating_after', self.gf('django.db.models.fields.FloatField')()),
            ('loser_rating_after', self.gf('django.db.models.fields.FloatField')()),
            ('played_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'techpong', ['Match'])

        # Adding model 'Round'
        db.create_table(u'techpong_round', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['techpong.Match'])),
            ('round_number', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('player1_score', self.gf('django.db.models.fields.IntegerField')()),
            ('player2_score', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'techpong', ['Round'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table(u'techpong_userprofile')

        # Deleting model 'Company'
        db.delete_table(u'techpong_company')

        # Deleting model 'Player'
        db.delete_table(u'techpong_player')

        # Deleting model 'Match'
        db.delete_table(u'techpong_match')

        # Deleting model 'Round'
        db.delete_table(u'techpong_round')


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
        u'techpong.company': {
            'Meta': {'object_name': 'Company'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'joined_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'techpong.match': {
            'Meta': {'ordering': "['-played_time']", 'object_name': 'Match'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Company']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_loser'", 'to': u"orm['techpong.Player']"}),
            'loser_rating_after': ('django.db.models.fields.FloatField', [], {}),
            'loser_rating_before': ('django.db.models.fields.FloatField', [], {}),
            'played_time': ('django.db.models.fields.DateTimeField', [], {}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_winner'", 'to': u"orm['techpong.Player']"}),
            'winner_rating_after': ('django.db.models.fields.FloatField', [], {}),
            'winner_rating_before': ('django.db.models.fields.FloatField', [], {})
        },
        u'techpong.player': {
            'Meta': {'object_name': 'Player'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Company']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'techpong.round': {
            'Meta': {'object_name': 'Round'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Match']"}),
            'player1_score': ('django.db.models.fields.IntegerField', [], {}),
            'player2_score': ('django.db.models.fields.IntegerField', [], {}),
            'round_number': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'techpong.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Company']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['techpong']