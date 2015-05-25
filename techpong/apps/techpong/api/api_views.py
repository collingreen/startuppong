from coffin.shortcuts import HttpResponse

from apps.techpong.models import *
from apps.techpong.api.api_decorators import api_get, api_post, api_endpoint
from apps.techpong.api.api_tools import api_response


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
