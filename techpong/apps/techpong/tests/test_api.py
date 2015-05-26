"""
Test coverage for the JSON API
"""

from django.test import TestCase
from django.test import Client
from apps.techpong.models import *
import datetime

API_PREFIX = '/api/v1/'


class APITest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.player1 = self.company.player_set.create(
                name='player1', company=self.company, rank=1)
        self.player2 = self.company.player_set.create(
                name='player2', company=self.company, rank=2)
        self.player3 = self.company.player_set.create(
                name='player3', company=self.company, rank=3)
        self.company.save()

        self.match1 = self.company.match_set.create(
            winner = self.player1,
            loser = self.player2,
            played_time = datetime.datetime.now()
        )

        self.match2 = self.company.match_set.create(
            winner = self.player1,
            loser = self.player3,
            played_time = datetime.datetime.now()
        )

        self.match3 = self.company.match_set.create(
            winner = self.player2,
            loser = self.player3,
            played_time = datetime.datetime.now()
        )

        self.company2 = Company.objects.create(name="Test Company 2")
        self.player4 = self.company2.player_set.create(
                name='player4', company=self.company2, rank=1)
        self.player5 = self.company2.player_set.create(
                name='player5', company=self.company2, rank=2)

        self.company3 = Company.objects.create(name="Test Company 3")

        self.client = Client()

    def tearDown(self):
        pass

    def _api_call_get(self, endpoint, data={}, company=None):
        if company is None:
            company = self.company
        data['api_access_key'] = company.get_api_access_key()
        data['api_account_id'] = company.get_api_account_id()
        return self.client.get(
                API_PREFIX + endpoint,
                data
            )

    def _api_call_post(self, endpoint, data={}, company=None):
        if company is None:
            company = self.company
        data['api_access_key'] = company.get_api_access_key()
        data['api_account_id'] = company.get_api_account_id()
        return self.client.post(
                API_PREFIX + endpoint,
                data
            )

    def _api_content(self, response):
        return json.loads(response.content)

    def test_no_credentials(self):
        result = self.client.get(API_PREFIX + 'test')
        self.assertEqual(result.status_code, 400)

    def test_invalid_credentials(self):
        result = self.client.get(
                API_PREFIX + 'test',
                {
                    'api_account_id': self.company.get_api_account_id(),
                    'api_access_key': 'incorrect-access-key'
                }
            )
        self.assertEqual(result.status_code, 403)

    def test_require_access_key(self):
        result = self.client.get(
                API_PREFIX + 'test',
                {'api_account_id': self.company.get_api_account_id()}
            )
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content, 'Missing field api_access_key')

    def test_require_account_id(self):
        result = self.client.get(
                API_PREFIX + 'test',
                {'api_access_key': self.company.get_api_access_key()}
            )
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.content, 'Missing field api_account_id')

    def test_test_endpoint(self):
        r = self._api_call_get('test')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self._api_content(r)['foo'], 'bar')

    def test_test_require_get(self):
        r = self._api_call_post('test')
        self.assertEqual(r.status_code, 405)

    def test_get_players(self):
        r = self._api_call_get('get_players')
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)

        self.assertTrue('players' in content)
        self.assertEqual(len(content['players']), 3)

        for player in content['players']:
            self.assertTrue('id' in player)
            self.assertTrue('name' in player)
            self.assertTrue('rank' in player)
            self.assertTrue('rating' in player)

    def test_get_players_require_get(self):
        r = self._api_call_post('get_players')
        self.assertEqual(r.status_code, 405)

    def _validate_match(self, match, winner=None, loser=None):
        self.assertTrue('id' in match)
        self.assertTrue('played_time' in match)
        self.assertTrue('winner_id' in match)
        self.assertTrue('winner_name' in match)
        self.assertTrue('winner_rank_before' in match)
        self.assertTrue('winner_rank_after' in match)
        self.assertTrue('winner_rating_before' in match)
        self.assertTrue('winner_rating_after' in match)
        self.assertTrue('loser_name' in match)
        self.assertTrue('loser_rank_before' in match)
        self.assertTrue('loser_rank_after' in match)
        self.assertTrue('loser_rating_before' in match)
        self.assertTrue('loser_rating_after' in match)

        if winner:
            self.assertEqual(match['winner_id'], winner.id)
            self.assertEqual(match['winner_name'], winner.name)

        if loser:
            self.assertEqual(match['loser_id'], loser.id)
            self.assertEqual(match['loser_name'], loser.name)

    def test_get_recent_matches_for_company(self):
        r = self._api_call_get('get_recent_matches_for_company')
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)

        self.assertTrue('matches' in content)
        self.assertEqual(len(content['matches']), 3)

        # validate matches
        for match in content['matches']:
            self._validate_match(match)

    def test_get_recent_matches_for_company_require_get(self):
        r = self._api_call_post('get_recent_matches_for_company')
        self.assertEqual(r.status_code, 405)

    def test_get_recent_matches_for_player(self):
        r = self._api_call_get(
                'get_recent_matches_for_player',
                {'player_id': self.player1.id}
            )
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)

        self.assertTrue('matches' in content)
        self.assertEqual(len(content['matches']), 2)

        # player 1 has won all matches
        for match in content['matches']:
            self._validate_match(match, self.player1)

    def test_get_recent_matches_for_invalid_player(self):
        r = self._api_call_get(
                'get_recent_matches_for_player',
                {'player_id': 999}
            )
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)

        self.assertFalse(content['success'])

    def test_malformed_get_recent_matches_for_player(self):
        r = self._api_call_get( 'get_recent_matches_for_player')
        self.assertEqual(r.status_code, 400)

    def test_get_recent_matches_for_player_require_get(self):
        r = self._api_call_post('get_recent_matches_for_player')
        self.assertEqual(r.status_code, 405)

    def test_get_recent_matches_for_between_players(self):
        r = self._api_call_get(
                'get_recent_matches_between_players',
                {
                    'player1_id': self.player2.id,
                    'player2_id': self.player3.id
                }
            )
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)

        self.assertTrue('matches' in content)
        self.assertEqual(len(content['matches']), 1)

        for match in content['matches']:
            self._validate_match(match, self.player2, self.player3)

    def test_get_recent_matches_between_invalid_players(self):
        r = self._api_call_get(
                'get_recent_matches_between_players',
                {
                    'player1_id': 998,
                    'player2_id': 999
                }
            )
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)

        self.assertFalse(content['success'])

    def test_malformed_get_recent_matches_between_players(self):
        r = self._api_call_get( 'get_recent_matches_between_players')
        self.assertEqual(r.status_code, 400)

    def test_get_recent_matches_between_players_require_get(self):
        r = self._api_call_post('get_recent_matches_between_players')
        self.assertEqual(r.status_code, 405)

    def test_add_match(self):
        r = self._api_call_post(
                'add_match',
                {
                    'winner_id': self.player4.id,
                    'loser_id': self.player5.id
                },
                company = self.company2
            )
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)
        self.assertTrue('match_id' in content)
        match_id = content['match_id']

        # compare directly against db
        db_matches = Match.objects.filter(company=self.company2)
        self.assertEqual(len(db_matches), 1)

        # compare against get matches api result
        r = self._api_call_get(
                'get_recent_matches_for_company',
                company=self.company2
            )
        content = self._api_content(r)

        self.assertEqual(content['matches'][0]['id'], match_id)

    def test_add_match_invalid_players(self):
        r = self._api_call_post(
                'add_match',
                {
                    'winner_id': 998,
                    'loser_id': 999
                }
            )
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)
        self.assertFalse(content['success'])

    def test_add_match_malformed(self):
        r = self._api_call_post('add_match')
        self.assertEqual(r.status_code, 400)

    def test_add_match_requires_post(self):
        r = self._api_call_get('add_match')
        self.assertEqual(r.status_code, 405)

    def test_add_player(self):
        r = self._api_call_post(
                'add_player',
                {
                    'name': 'test player'
                },
                company = self.company3
            )
        self.assertEqual(r.status_code, 200)
        content = self._api_content(r)
        self.assertTrue('player_id' in content)
        player_id = content['player_id']

        # compare against get players api result
        r = self._api_call_get(
                'get_players',
                company=self.company3
            )
        content = self._api_content(r)
        self.assertEqual(content['players'][0]['id'], player_id)

    def test_add_player_duplicate_name(self):
        r = self._api_call_post(
                'add_player',
                {'name': 'duplicate'},
                company=self.company3
            )
        self.assertEqual(r.status_code, 200)

        r = self._api_call_post(
                'add_player',
                {'name': 'duplicate'},
                company=self.company3
            )
        content = self._api_content(r)
        self.assertFalse(content['success'])

    def test_add_player_malformed(self):
        r = self._api_call_post('add_player')
        self.assertEqual(r.status_code, 400)

    def test_add_player_requires_post(self):
        r = self._api_call_get('add_player')
        self.assertEqual(r.status_code, 405)
