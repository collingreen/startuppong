# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=100)),
                ('joined_time', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(max_length=100)),
                ('banner_url', models.URLField(max_length=255, blank=True)),
                ('logo_url', models.URLField(max_length=255, blank=True)),
                ('recalculating', models.BooleanField(default=False)),
                ('latest_change', models.DateTimeField(auto_now=True)),
                ('show_rank', models.BooleanField(default=True)),
                ('show_rating', models.BooleanField(default=True)),
                ('order_by', models.CharField(default=b'rank', max_length=50, choices=[(b'rank', b'Rank'), (b'rating', b'Rating')])),
                ('api_account_id', models.CharField(max_length=64, blank=True)),
                ('api_access_key', models.CharField(max_length=64, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('played_time', models.DateTimeField()),
                ('winner_rank_before', models.PositiveIntegerField(null=True, blank=True)),
                ('winner_rank_after', models.PositiveIntegerField(null=True, blank=True)),
                ('loser_rank_before', models.PositiveIntegerField(null=True, blank=True)),
                ('loser_rank_after', models.PositiveIntegerField(null=True, blank=True)),
                ('winner_rating_before', models.FloatField(null=True, blank=True)),
                ('loser_rating_before', models.FloatField(null=True, blank=True)),
                ('winner_rating_after', models.FloatField(null=True, blank=True)),
                ('loser_rating_after', models.FloatField(null=True, blank=True)),
                ('match_quality', models.FloatField(null=True, blank=True)),
                ('company', models.ForeignKey(to='techpong.Company')),
            ],
            options={
                'ordering': ['-played_time'],
                'verbose_name_plural': 'Matches',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('rating', models.FloatField(default=500.0)),
                ('rank', models.PositiveIntegerField(null=True, blank=True)),
                ('cached_rating_changes', models.TextField(blank=True)),
                ('cached_rank_changes', models.TextField(blank=True)),
                ('cached_results', models.TextField(blank=True)),
                ('company', models.ForeignKey(to='techpong.Company')),
            ],
            options={
                'ordering': ['rank'],
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('round_number', models.PositiveSmallIntegerField()),
                ('loser', models.ForeignKey(related_name='round_loser', blank=True, to='techpong.Player', null=True)),
                ('match', models.ForeignKey(to='techpong.Match')),
                ('winner', models.ForeignKey(related_name='round_winner', blank=True, to='techpong.Player', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.ForeignKey(blank=True, to='techpong.Company', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='loser',
            field=models.ForeignKey(related_name='match_loser', to='techpong.Player'),
        ),
        migrations.AddField(
            model_name='match',
            name='winner',
            field=models.ForeignKey(related_name='match_winner', to='techpong.Player'),
        ),
    ]
