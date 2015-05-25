from coffin.shortcuts import HttpResponse

from apps.techpong.models import *
from apps.techpong.api.api_decorators import api_get, api_post, api_endpoint
from apps.techpong.api.api_tools import api_response, api_response_invalid
from apps.techpong.api.api_tools import serialize_match


@api_endpoint
def test(request):
    return api_response(success=True, foo='bar')

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

@api_endpoint
def get_recent_matches_for_company(request):
    company = request.api_info['company']
    matches = [serialize_match(m) for m in company.get_recent_matches()]
    return api_response(success=True, matches=matches)

@api_endpoint
def get_recent_matches_for_player(request):
    company = request.api_info['company']

    # require player_id
    if 'player_id' not in request.REQUEST or \
            request.REQUEST['player_id'] == '':
        return api_response_invalid(missing_field='player_id')

    # validate player id
    try:
        player_id = int(request.REQUEST['player_id'])
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

@api_endpoint
def get_recent_matches_between_players(request):
    company = request.api_info['company']

    # require player1_id and player2_id
    if 'player1_id' not in request.REQUEST or \
            request.REQUEST['player1_id'] == '':
        return api_response_invalid(missing_field='player1_id')
    elif 'player2_id' not in request.REQUEST or \
            request.REQUEST['player2_id'] == '':
        return api_response_invalid(missing_field='player2_id')

    # validate player ids
    try:
        player1_id = int(request.REQUEST['player1_id'])
    except TypeError:
        return api_response_invalid(invalid_field='player1_id')
    except ValueError:
        return api_response_invalid(invalid_field='player1_id')
    try:
        player2_id = int(request.REQUEST['player2_id'])
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
