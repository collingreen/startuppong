from django.db import models, transaction
from django.db.models import Q, F
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.conf import settings

from lib.djeroku.tools.misc_tools import get_timestamp

import json
import random
import string
import elo

MATCH_RESULT_LIMIT = 50
CACHED_RATING_LIMIT = 50
CACHED_RANK_LIMIT = 50

DEFAULT_RATING = 500.0


class UserProfile(models.Model):
    """UserProfile model to add custom fields to the built in django auth User
    model"""
    user = models.ForeignKey(User)
    company = models.ForeignKey('Company', null=True, blank=True)
    last_viewed_notifications = models.DateTimeField(null=True, blank=True)

    def get_username(self): return self.user.username
    get_username.short_description = 'Username'

    def get_name(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)
    get_name.short_description = 'Name'

    def get_is_active(self): return self.user.is_active
    get_is_active.short_description = 'Active'

    def save(self, *args, **kwargs):
        super(UserProfile,self).save(*args, **kwargs)

        # force reload of profile object next time it is accessed
        if hasattr(self, '_user_instance'):
            self._user_instance._profile_instance = None

# creates the profile on the fly if necessary and caches it on the user object
# set default account values in the defaults dict as needed by your app
def user_get_profile(self):
    if hasattr(self,'_profile_instance') and self._profile_instance:
        return self._profile_instance
    profile, created = UserProfile.objects.get_or_create(user=self, defaults={})
    profile._user_instance = self
    self._profile_instance = profile
    return profile
User.get_profile = user_get_profile
User.profile = property(user_get_profile)

# saves the user profile when the user is saved
@receiver(post_save, sender=User)
def save_profile_with_user(sender, instance, created, **kwargs):
    instance.get_profile().save()


class Notification(models.Model):
    class Meta:
        ordering = ['-notification_time']
    notification_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __unicode__(self):
        name = self.title
        return name


class Company(models.Model):
    """A company (or group) of players that show up on the same ladder."""
    class Meta:
        verbose_name_plural = 'Companies'

    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)
    joined_time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100)
    banner_url = models.URLField(max_length=255, blank=True)
    logo_url = models.URLField(max_length=255, blank=True)
    recalculating = models.BooleanField(default=False)
    latest_change = models.DateTimeField(auto_now=True)

    show_rank = models.BooleanField(default=True)
    show_rating = models.BooleanField(default=True)
    order_by = models.CharField(max_length=50,
                choices=( ('rank', 'Rank'), ('rating', 'Rating')),
                default='rank'
            )

    api_account_id = models.CharField(max_length=64, blank=True)
    api_access_key = models.CharField(max_length=64, blank=True)

    def check_permission(self, user):
        return (user.is_staff
                or (user.profile.company and user.profile.company == self))

    def get_info(self):
        """Returns a bunch of info for rendering on the dashboard."""
        players = self.player_set
        if self.order_by == 'rank':
            players = players.order_by('rank')
        else:
            players = players.order_by('-rating')

        # if players have None scores, move to the bottom
        none_players = []
        players = list(players)
        for player in players:
            if ((self.order_by == 'rank' and player.rank is None)
                or (self.order_by == 'rating' and player.rating is None)):
                none_players.append(player)
                players.remove(player)
        players.extend(none_players)

        return dict(
                players = players,
                players_json = json.dumps([
                    {
                        'id': player.id,
                        'name': "%d %s" % (
                            player.rank or len(players), player.name)
                    }
                    for player in players]),
                num_matches = self.match_set.count(),
                num_rounds = Round.objects.filter(match__company = self).count(),
                recent_matches = (self.match_set
                    .order_by('-played_time')[:MATCH_RESULT_LIMIT]),
                api_account_id = self.get_api_account_id(),
                api_access_key = self.get_api_access_key()
                )

    @transaction.commit_on_success
    def update_player_rank(self, player, rank, match):
        """Moves the given player into the given rank. Updates all the
        players currently at or below that rank by moving them down one."""

        # if player isn't moving, do nothing
        if player.rank == rank:
            return

        # if player doesn't have a rank yet, make them last
        if player.rank is None:
            player.rank = self.player_set.count()

        # update all the players in the company at or below the target rank
        # but greater than the player's former rank
        ##(self.player_set
        ##    .filter(rank__isnull=False, rank__gte=rank, rank__lt=player.rank)
        ##    .update(rank=F('rank') + 1)
        ## )
        passed_players = (self.player_set
            .filter(rank__isnull=False, rank__gte=rank, rank__lt=player.rank))
        for p in passed_players:
            p.update_rank(p.rank + 1, match)

        # update target player
        player.update_rank(rank, match)

    def recache_matches(self):
        """
        Resets all players and replays every match.

        TODO: support performing in batches in task queue
        TODO: support starting from recent 'snapshot'
        """
        self.recalculating = True
        self.save()

        # give all the players a starting rank
        i = 1
        for player in self.player_set.order_by('id'):
            player.rank = i
            player.rating = DEFAULT_RATING
            player.cached_results = ''
            player.cached_rating_changes = ''
            player.cached_rank_changes = ''
            player.save()
            i += 1

        # get all the matches and replay them in order
        matches = self.match_set.order_by('played_time')
        for match in matches:
            match.update_company_ladder()

        self.recalculating = False
        self.save()

    def get_recent_matches(self, limit=None):
        """Returns a list of recent matches"""
        return (Match.objects
            .filter(company=self)
            .order_by('-played_time')[:limit or MATCH_RESULT_LIMIT]
        )
    def __unicode__(self):
        return self.name

    def get_api_account_id(self):
        """Return the api_account_id, generating it first if necessary."""
        if self.api_account_id in [None, '']:
            options = string.letters + string.digits
            self.api_account_id = ''.join([
                    random.choice(options)
                    for i in range(64)
                ])
            self.save()
        return self.api_account_id

    def get_api_access_key(self):
        """Return the api_access_key, generating it first if necessary."""
        if self.api_access_key in [None, '']:
            options = string.letters + string.digits
            self.api_access_key = ''.join([
                    random.choice(options)
                    for i in range(64)
                ])
            self.save()
        return self.api_access_key

    def reset_api_access_key(self):
        self.api_access_key = ''
        return self.get_api_access_key()


class Player(models.Model):
    """One player. All players are part of a company. Players are not the
    same as user accounts."""

    class Meta:
        ordering = ['rank']

    company = models.ForeignKey(Company)
    name = models.CharField(max_length=100)
    rating = models.FloatField(default=DEFAULT_RATING)
    rank = models.PositiveIntegerField(blank=True, null=True)
    cached_rating_changes = models.TextField(blank=True)
    cached_rank_changes = models.TextField(blank=True)
    cached_results = models.TextField(blank=True)

    def add_match(self, match):
        """
        Called on each participant after a match ends.
        """

        # update cache results with game result
        if self.cached_results:
            results = json.loads(self.cached_results)
        else:
            results = []

        winner = match.winner == self
        opponent = match.loser if winner else match.winner
        new_rating = match.winner_rating_after if winner else \
                match.loser_rating_after

        results.append({
            'winner': winner,
            'opponent_name': opponent.name,
            'played_time': str(match.played_time),
            'played_timestamp': get_timestamp(match.played_time)
        })
        self.cached_results = json.dumps(results[-CACHED_RATING_LIMIT:])

        # update player with new rating
        self.update_rating(new_rating, match)

        # save the player in the database
        self.save()

    def update_rating(self, new_rating, match):
        """Called to update the player's rating after a match."""
        self.rating = new_rating

        # update cached ratings with rating change
        if self.cached_rating_changes:
            rating_changes = json.loads(self.cached_rating_changes)
        else:
            rating_changes = []

        rating_changes.append({
            "rating": new_rating,
            "played_time": str(match.played_time),
            "played_timestamp": get_timestamp(match.played_time)
        })
        self.cached_rating_changes = json.dumps(
                rating_changes[-CACHED_RATING_LIMIT:])

    def recache_matches(self):
        """
        Reprocesses all the matches this user has been a part of
        and updates the results and ratings caches.
        NOTE: this will NOT correctly update ranks!
        """
        matches = (Match.objects
                    .filter(Q(winner = self) | Q(loser = self))
                    .order_by('-played_time'))[:CACHED_RATING_LIMIT]
        matches = list(matches)
        matches.reverse()

        for match in matches:
            self.add_match(match, include_rank=True)

        self.save()

    def update_rank(self, new_rank, match):
        """
        Called to update the player's rank. This can be caused
        by OTHER player's matches in a rank stealing ladder.
        """

        self.rank = new_rank

        # update cached ranks with rank change
        if self.cached_rank_changes:
            rank_changes = json.loads(self.cached_rank_changes)
        else:
            rank_changes = []

        rank_changes.append({
            "rank": new_rank,
            "played_time": str(match.played_time),
            "played_timestamp": get_timestamp(match.played_time)
        })
        self.cached_rank_changes = json.dumps(
                rank_changes[-CACHED_RANK_LIMIT:])
        self.save()

    def get_recent_matches(self, limit=None):
        """Returns a list of recent matches that included this
        player."""
        matches = (Match.objects
            .filter(Q(winner=self) | Q(loser=self))
            .order_by('-played_time'))
        return matches[:limit or MATCH_RESULT_LIMIT]

    def get_recent_matches_with_player(self, player, limit=None):
        """Returns a list of recent matches that included this
        player and the target player."""
        matches = (Match.objects
            .filter(
                Q(winner=self, loser=player) |
                Q(loser=self, winner=player)
            )
            .order_by('-played_time'))
        return matches[:limit or MATCH_RESULT_LIMIT]

    def __unicode__(self):
        if self.company.show_rank and self.company.show_rating:
            return '%s - Rank %s (%s)' % (
                    self.name, str(self.rank), str(self.rating))
        elif self.company.show_rank:
            return '%s - Rank %s' % (self.name, str(self.rank))
        elif self.company.show_rating:
            return '%s (%s)' % (self.name, str(self.rating))
        return self.name


class Match(models.Model):
    """A match between two players."""
    class Meta:
        verbose_name_plural = 'Matches'
        ordering = ['-played_time']

    company = models.ForeignKey(Company)
    played_time = models.DateTimeField()

    winner = models.ForeignKey(Player, related_name='match_winner')
    loser = models.ForeignKey(Player, related_name='match_loser')

    winner_rank_before = models.PositiveIntegerField(blank=True, null=True)
    winner_rank_after = models.PositiveIntegerField(blank=True, null=True)
    loser_rank_before = models.PositiveIntegerField(blank=True, null=True)
    loser_rank_after = models.PositiveIntegerField(blank=True, null=True)

    winner_rating_before = models.FloatField(blank=True, null=True)
    loser_rating_before = models.FloatField(blank=True, null=True)
    winner_rating_after = models.FloatField(blank=True, null=True)
    loser_rating_after = models.FloatField(blank=True, null=True)
    match_quality = models.FloatField(blank=True, null=True)

    def update_company_ladder(self):
        """
        Called when a match is created (or recached) to
        update the ladder and players.
        """

        # create rating objects
        w_rating = elo.Rating(self.winner.rating)
        l_rating = elo.Rating(self.loser.rating)

        # calculate the new ratings based on who won
        w_rating_after, l_rating_after = elo.rate_1vs1(w_rating, l_rating)

        # if neither player has a rank, set both ranks to the best available
        if self.winner.company == self.loser.company:
            if self.winner.rank is None and self.loser.rank is None:
                # get the highest rank number in the company
                highest_rank = \
                        self.winner.company.player_set.order_by('-rank')[0].rank
                if highest_rank is None:
                    highest_rank = 0
                self.winner.rank = highest_rank + 1
                self.loser.rank = self.winner.rank + 1

        # calculate the new ranks based on who won
        w_rank = self.winner.rank or \
                self.winner.company.player_set.count()
        l_rank = self.loser.rank or \
                self.loser.company.player_set.count()

        # if neither player had a rank, put the winner ahead of the loser
        if w_rank == l_rank:
            w_rank -= 1

        if w_rank < l_rank:
            w_rank_after, l_rank_after = w_rank, l_rank
        else:
            w_rank_after, l_rank_after = l_rank, l_rank + 1

        # update the match quality
        self.match_quality = elo.quality_1vs1(w_rating, l_rating)

        # save the player ratings
        self.winner_rating_before = w_rating
        self.winner_rating_after = w_rating_after
        self.loser_rating_before = l_rating
        self.loser_rating_after = l_rating_after

        # save the player ranks
        self.winner_rank_before = w_rank
        self.winner_rank_after = w_rank_after
        self.loser_rank_before = l_rank
        self.loser_rank_after = l_rank_after

        # update the players
        self.winner.add_match(self)
        self.loser.add_match(self)

        # update the company so new ranks can be calculated
        if w_rank != w_rank_after and self.winner.company == self.loser.company:
            self.winner.company.update_player_rank(
                    self.winner, w_rank_after, self)

        # save the match again
        self.save()

    def __unicode__(self):
        winner_name = self.winner.name
        if self.winner_rank_before:
            winner_name = "(%d) %s" % (self.winner_rank_before, winner_name)

        loser_name = self.loser.name
        if self.loser_rank_before:
            loser_name = "(%d) %s" % (self.loser_rank_before, loser_name)

        return "%s - %s defeated %s" % (
                    str(self.played_time),
                    winner_name,
                    loser_name
                )

@receiver(post_save, sender=Match)
def match_post_save(sender, instance, created, **kwargs):
    if created:
        instance.update_company_ladder()


class Round(models.Model):
    """One round in a match."""
    match = models.ForeignKey(Match)
    round_number = models.PositiveSmallIntegerField()

    winner = models.ForeignKey(
            Player, null=True, blank=True, related_name="round_winner")
    loser = models.ForeignKey(
            Player, null=True, blank=True, related_name="round_loser")

    def __unicode__(self):
        return "Match %d Round %d: Winner %s - Loser %s" % (
            self.match.id, self.round_number,
            str(self.winner), str(self.loser)
        )

