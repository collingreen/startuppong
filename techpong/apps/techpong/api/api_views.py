from django.shortcuts import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from apps.techpong.models import *
from apps.techpong.api.api_decorators import api_get, api_post, api_endpoint
from apps.techpong.api.api_tools import api_response, api_response_invalid
from apps.techpong.api.api_tools import serialize_match

import datetime

@api_get
@api_endpoint
def test(request):
    return api_response(success=True, foo='bar')

@api_get
@api_endpoint
def get_players(request):
    info = request.api_info['company'].get_info()
    players = [dict(
        id=p.id,
        name=p.name,
        rank=p.rank,
        rating=p.rating
        ) for p in info['players']]
    return api_response(success=True, players=players)

@api_get
@api_endpoint
def get_recent_matches_for_company(request):
    company = request.api_info['company']
    matches = [serialize_match(m) for m in company.get_recent_matches()]
    return api_response(success=True, matches=matches)

@api_get
@api_endpoint
def get_recent_matches_for_player(request):
    company = request.api_info['company']

    # require player_id
    if 'player_id' not in request.GET or \
            request.GET['player_id'] == '':
        return api_response_invalid(missing_field='player_id')

    # validate player id
    try:
        player_id = int(request.GET['player_id'])
    except TypeError:
        return api_response_invalid(invalid_field='player_id')
    except ValueError:
        return api_response_invalid(invalid_field='player_id')

    # find player
    try:
        player = Player.objects.get(pk=player_id)
    except ObjectDoesNotExist:
        return api_response(
            success=False,
            error='player not found',
            error_code='player_not_found'
            )

    # confirm player is in company
    if not player.company.id == company.id:
        return api_response(
            success=False,
            error='permission denied',
            error_code='permission denied'
            )

    # return matches
    matches = [serialize_match(m) for m in player.get_recent_matches()]
    return api_response(success=True, matches=matches)

@api_get
@api_endpoint
def get_recent_matches_between_players(request):
    company = request.api_info['company']

    # require player1_id and player2_id
    if 'player1_id' not in request.GET or \
            request.GET['player1_id'] == '':
        return api_response_invalid(missing_field='player1_id')
    elif 'player2_id' not in request.GET or \
            request.GET['player2_id'] == '':
        return api_response_invalid(missing_field='player2_id')

    # validate player ids
    try:
        player1_id = int(request.GET['player1_id'])
    except TypeError:
        return api_response_invalid(invalid_field='player1_id')
    except ValueError:
        return api_response_invalid(invalid_field='player1_id')
    try:
        player2_id = int(request.GET['player2_id'])
    except TypeError:
        return api_response_invalid(invalid_field='player2_id')
    except ValueError:
        return api_response_invalid(invalid_field='player2_id')

    # find players
    try:
        player1 = Player.objects.get(pk=player1_id)
    except ObjectDoesNotExist:
        return api_response(
            success=False,
            error='player1 not found',
            error_code='player_not_found'
            )
    try:
        player2 = Player.objects.get(pk=player2_id)
    except ObjectDoesNotExist:
        return api_response(
            success=False,
            error='player2 not found',
            error_code='player_not_found'
            )

    # confirm players are in company
    if not player1.company.id == company.id or \
            not player2.company.id == company.id:
        return api_response(
            success=False,
            error='permission denied',
            error_code='permission denied'
            )

    # return matches
    matches = [
            serialize_match(m)
            for m in player1.get_recent_matches_with_player(player2)]
    return api_response(success=True, matches=matches)

@api_post
@api_endpoint
def add_match(request):
    company = request.api_info['company']

    # require winner_id and loser_id
    if 'winner_id' not in request.POST or \
            request.POST['winner_id'] == '':
        return api_response_invalid(missing_field='winner_id')
    elif 'loser_id' not in request.POST or \
            request.POST['loser_id'] == '':
        return api_response_invalid(missing_field='loser_id')

    # validate player ids
    try:
        winner_id = int(request.POST['winner_id'])
    except TypeError:
        return api_response_invalid(invalid_field='winner_id')
    except ValueError:
        return api_response_invalid(invalid_field='winner_id')
    try:
        loser_id = int(request.POST['loser_id'])
    except TypeError:
        return api_response_invalid(invalid_field='loser_id')
    except ValueError:
        return api_response_invalid(invalid_field='loser_id')

    # find players
    try:
        winner = Player.objects.get(pk=winner_id)
    except ObjectDoesNotExist:
        return api_response(
            success=False,
            error='winner not found',
            error_code='player_not_found'
            )
    try:
        loser = Player.objects.get(pk=loser_id)
    except ObjectDoesNotExist:
        return api_response(
            success=False,
            error='loser not found',
            error_code='player_not_found'
            )

    # confirm players are in company
    if not winner.company.id == company.id or \
            not loser.company.id == company.id:
        return api_response(
            success=False,
            error='permission denied',
            error_code='permission denied'
            )

    # create new match
    match = company.match_set.create(
        winner = winner,
        loser = loser,
        played_time = datetime.datetime.now()
    )

    # save company to update the last changed time
    company.save()

    return api_response(success=True, match_id=match.id)

@api_post
@api_endpoint
def add_player(request):
    company = request.api_info['company']

    # require name
    if 'name' not in request.POST or \
            request.POST['name'] == '':
        return api_response_invalid(missing_field='name')
    name = request.POST['name']

    # check for duplicates
    existing_count = Player.objects.filter(
            name=name,
            company=company
        ).count()

    if existing_count > 0:
        return api_response(
            success=False,
            error='duplicate player name',
            error_code='player_already_exists'
            )

    # create a new player
    player = company.player_set.create(
        name = name,
        rank = company.player_set.count() + 1,
        rating = 500, # todo: company can specify the starting rating
    )

    # save company to update the last changed time
    company.save()

    return api_response(success=True, player_id=player.id)
