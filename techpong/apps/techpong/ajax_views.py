from coffin.shortcuts import render, render_to_response, Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.exceptions import ObjectDoesNotExist

from lib.djeroku.tools.view_tools import json_response, validate_required
from apps.techpong.models import *

import datetime

@login_required
def add_match(request, company_name):
    required_fields = {
        'winner': {
            'validation': lambda a: a.isdigit(), 'clean': lambda a: int(a)},
        'loser': {
            'validation': lambda a: a.isdigit(), 'clean': lambda a: int(a)}
    }
    validate_result = validate_required(request.POST, required_fields)
    if not validate_result[0]:
        return json_response(
                False, error_message="Invalid Field: %s " % str(validate_result[1]))
    clean = validate_result[1]
    winner_id, loser_id = clean['winner'], clean['loser']

    try:
        company = Company.objects.filter(short_name = company_name).get()
    except ObjectDoesNotExist:
        # todo: show signup form
        raise Http404()

    # get winner and loser players
    try:
        winner = company.player_set.get(pk=winner_id)
    except ObjectDoesNotExist:
        return json_response(False, error_message="Invalid Winner")

    try:
        loser = company.player_set.get(pk=loser_id)
    except ObjectDoesNotExist:
        return json_response(False, error_message="Invalid Loser")

    # check permission
    if not company.check_permission(request.user):
        # todo: show permission denied
        raise Http404()

    # look for points
    scores = {}
    for i in [1,2,3]:
        field = "game%dwinner" % i
        scores[field] = 0
        if field in request.POST:
            num = request.POST[field]
            try:
                num = int(num)
            except ValueError, TypeError:
                continue
            if num < 0 or num > 11:
                continue
        scores[field] = num

        field = "game%dloser" % i
        scores[field] = 0
        if field in request.POST:
            num = request.POST[field]
            try:
                num = int(num)
            except ValueError, TypeError:
                continue
            if num < 0 or num > 11:
                continue
        scores[field] = num
    # todo: validate scores on model

    # create a new match
    match = company.match_set.create(
        winner = winner,
        loser = loser,
        played_time = datetime.datetime.now()
    )

    match.round_set.create(
        round_number = 1,
        winner_score = scores["game1winner"],
        loser_score = scores["game1loser"]
    )

    match.round_set.create(
        round_number = 2,
        winner_score = scores["game2winner"],
        loser_score = scores["game2loser"]
    )

    if scores["game3winner"] > 0 and scores["game3loser"] > 0:
        match.round_set.create(
            round_number = 3,
            winner_score = scores["game3winner"],
            loser_score = scores["game3loser"]
        )

    # return success
    return json_response(True, match_id=match.id)

@login_required
def add_player(request, company_name):
    required_fields = {
        'name': {
            'validation': lambda a: a.replace(' ', '').isalnum() and len(a) > 0, 'clean': lambda a: a.strip()}
    }
    validate_result = validate_required(request.POST, required_fields)
    if not validate_result[0]:
        return json_response(
            False, error_message="Invalid Field: " + str(validate_result[1]))
    clean = validate_result[1]
    name = clean['name']

    try:
        company = Company.objects.filter(short_name = company_name).get()
    except ObjectDoesNotExist:
        # todo: show signup form
        raise Http404()

    # validate no other players with this name
    matching_players = company.player_set.filter(name = name).count()
    if matching_players > 0:
        return json_response(False, error_message="Player already exists with this name")

    # check permission
    if not company.check_permission(request.user):
        # todo: show permission denied
        raise Http404()

    # create a new player
    player = company.player_set.create(
                name = name,
                rank = company.player_set.count() + 1,
                rating = 500, # todo: company can specify the starting rating
            )

    # return success
    return json_response(True, player_id = player.id)
