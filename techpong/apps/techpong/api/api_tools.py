from coffin.shortcuts import HttpResponse
import json
import datetime
import time


def api_response(success=False, error=None, error_code=None, **kwargs):
    response = kwargs
    response['success'] = success
    if error or error_code:
        response['error'] = error
        response['error_code'] = error_code
    return HttpResponse(json.dumps(response))

def api_response_invalid(missing_field=None, invalid_field=None):
    message = "invalid request"
    if missing_field:
        message = 'Missing field %s' % missing_field
    if invalid_field:
        message = 'Invalid field %s' % invalid_field
    return HttpResponse(message, status=400)

def api_response_permission_denied(invalid_field=None):
    message = "invalid request"
    if missing_field:
        message = 'Missing field %s' % missing_field
    if invalid_field:
        message = 'Invalid field %s' % invalid_field
    return HttpResponse(message, status=400)

def api_timestamp(timestamp):
    return time.mktime(timestamp.timetuple())

def serialize_match(match):
    return dict(
        id=match.id,
        played_time=api_timestamp(match.played_time),
        winner_id=match.winner.id,
        winner_name=match.winner.name,
        winner_rank_before=match.winner_rank_before,
        winner_rank_after=match.winner_rank_after,
        winner_rating_before=match.winner_rating_before,
        winner_rating_after=match.winner_rating_after,
        loser_id=match.loser.id,
        loser_name=match.loser.name,
        loser_rank_before=match.loser_rank_before,
        loser_rank_after=match.loser_rank_after,
        loser_rating_before=match.loser_rating_before,
        loser_rating_after=match.loser_rating_after
    )
