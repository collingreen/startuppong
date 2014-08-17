"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from apps.techpong.models import *
import datetime

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

PLAYER1_NAME = "Player 1"
PLAYER1_RANK = 3
PLAYER2_NAME = "Player 2"
PLAYER2_RANK = 2
PLAYER3_NAME = "Player 3"
PLAYER3_RANK = 1

class RankTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.player1 = self.company.player_set.create(
                name=PLAYER1_NAME, company=self.company, rank=PLAYER1_RANK)
        self.player2 = self.company.player_set.create(
                name=PLAYER2_NAME, company=self.company, rank=PLAYER2_RANK)
        self.player3 = self.company.player_set.create(
                name=PLAYER3_NAME, company=self.company, rank=PLAYER3_RANK)
        self.company.save()

    def tearDown(self):
        pass

    def test_default_rank_none(self):
        p = Player.objects.create(name='fake', company=self.company)
        self.assertEqual(p.rank, None)

    def test_order_by_rank_by_default(self):
        players = Player.objects.all()
        last_rank = 0
        for player in players:
            self.assertTrue( player.rank >= last_rank)
            last_rank = player.rank

    def test_order_by_rating(self):
        """Tests that get_info returns players ordered
        by rank if show_rank is True"""
        self.company.show_rank = True
        players = self.company.get_info()['players']
        last_rank = None
        for player in players:
            if last_rank is None:
                last_rank = player.rank
            self.assertTrue(player.rank >= last_rank)
            last_rank = player.rank

    def test_order_by_rating(self):
        self.company.show_rank = False
        players = self.company.get_info()['players']
        last_rating = None
        for player in players:
            if last_rating is None:
                last_rating = player.rating
            self.assertTrue(player.rating <= last_rating)
            last_rating = player.rating

    def test_passing(self):
        """Tests a player going from last to first."""
        # get players ordered by rank
        players = self.company.get_info()['players']
        old_ranks = dict([(p.name, p.rank) for p in players])

        # let last pass first
        last = players[len(players)-1]
        match = Match(
                company=self.company,
                played_time=datetime.datetime.now(),
                winner=last,
                loser=players[0]
                )
        self.company.update_player_rank(last, 1, match)

        # get players again
        players = Player.objects.all()
        players_by_name = dict([(p.name, p.rank) for p in players])

        # last should now be first
        players_by_name[last.name] = 1

        # verify everyone else moved down
        for player in players:
            if player.name != last.name:
                self.assertEqual(
                        old_ranks[player.name] + 1,
                        players_by_name[player.name],
                        msg="Expected %s rank %d, got rank %d" % (
                            player.name,
                            old_ranks[player.name] + 1,
                            players_by_name[player.name])
                    )

    def test_passing_from_middle(self):
        """Tests a player passing only some of the other players."""
        # get players ordered by rank
        players = self.company.get_info()['players']
        old_ranks = dict([(p.name, p.rank) for p in players])

        # require at least 3 test players
        self.assertTrue(
                len(old_ranks) >= 3, msg="Test requires at least 3 players")

        # let second place pass first
        first = players[0]
        second = players[1]
        match = Match(
                company=self.company,
                played_time=datetime.datetime.now(),
                winner=second,
                loser=first
                )
        match.save()
        self.company.update_player_rank(second, 1, match)

        # get players again
        players = Player.objects.all()
        players_by_name = dict([(p.name, p.rank) for p in players])

        # second should now be first
        players_by_name[second.name] = 1

        # first should now be second
        players_by_name[first.name] = 2

        # verify everyone else did /not/ move
        for player in players:
            if player.name not in [first.name, second.name]:
                self.assertEqual(
                        old_ranks[player.name],
                        players_by_name[player.name],
                        msg="Expected %s rank %d, got rank %d" % (
                            player.name,
                            old_ranks[player.name],
                            players_by_name[player.name])
                    )

    def test_display_name_from_company_setting(self):
        """Test that changing the company show_rating and show_rank
        settings correctly determine how players are displayed."""
        RANK, RATING = 2, 1000
        self.player1.rank = RANK
        self.player1.rating = RATING

        self.company.show_rating = True
        self.company.show_rank = True
        self.assertEqual(
                unicode(self.player1),
                u"%s - Rank %s (%s)" % (
                    self.player1.name, self.player1.rank, self.player1.rating)
                )

        self.company.show_rating = False
        self.assertEqual(
                unicode(self.player1),
                u"%s - Rank %s" % (
                    self.player1.name, self.player1.rank)
                )

        self.company.show_rating = True
        self.company.show_rank = False
        self.assertEqual(
                unicode(self.player1),
                u"%s (%s)" % (
                    self.player1.name, self.player1.rating)
                )

        self.company.show_rating = False
        self.assertEqual(
                unicode(self.player1),
                u"%s" % (self.player1.name)
                )

#    def test_match_results():
#        pass
#
#    def test_cached_ranks():
#        pass
#
#    def test_cached_ratings():
#        pass
#
#    def test_notification():
#        pass
#
