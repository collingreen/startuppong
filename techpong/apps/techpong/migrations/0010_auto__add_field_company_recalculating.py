# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Company.recalculating'
        db.add_column(u'techpong_company', 'recalculating',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Company.recalculating'
        db.delete_column(u'techpong_company', 'recalculating')


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
            'banner_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'joined_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order_by': ('django.db.models.fields.CharField', [], {'default': "'rank'", 'max_length': '50'}),
            'recalculating': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'show_rank': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_rating': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'techpong.match': {
            'Meta': {'ordering': "['-played_time']", 'object_name': 'Match'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Company']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_loser'", 'to': u"orm['techpong.Player']"}),
            'loser_rank_after': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'loser_rank_before': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'loser_rating_after': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'loser_rating_before': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'match_quality': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'played_time': ('django.db.models.fields.DateTimeField', [], {}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_winner'", 'to': u"orm['techpong.Player']"}),
            'winner_rank_after': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'winner_rank_before': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'winner_rating_after': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'winner_rating_before': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'techpong.player': {
            'Meta': {'ordering': "['rank']", 'object_name': 'Player'},
            'cached_rank_changes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cached_rating_changes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cached_results': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Company']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '500.0'})
        },
        u'techpong.round': {
            'Meta': {'object_name': 'Round'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loser': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'round_loser'", 'null': 'True', 'to': u"orm['techpong.Player']"}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Match']"}),
            'round_number': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'round_winner'", 'null': 'True', 'to': u"orm['techpong.Player']"})
        },
        u'techpong.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['techpong.Company']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['techpong']