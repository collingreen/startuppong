from coffin.shortcuts import render, render_to_response, Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from lib.djeroku.tools.view_tools import json_response, validate_required
from apps.techpong.models import *

import datetime
import time

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

    # create a new match
    match = company.match_set.create(
        winner = winner,
        loser = loser,
        played_time = datetime.datetime.now()
    )

    # save round info if available
    # todo: validate on model
    round_winners = {}
    winning_rounds = 0
    for i in [1,2,3]:
        field = "game%dwinner" % i
        if field in request.POST:
            round_winner_id = request.POST[field]
            try:
                round_winner_id = int(round_winner_id)
            except ValueError, TypeError:
                continue

            if round_winner_id == winner_id:
                round_winner = winner
                round_loser = loser
                winning_rounds += 1
            else:
                round_winner = loser
                round_loser = winner

        round_winners[i] = dict(
                winner = round_winner,
                loser = round_loser
            )

    # if proper number of rounds won by match winner, create round objects
    if winning_rounds == 2:
        for i in [1,2,3]:
            match.round_set.create(
                round_number = i,
                winner = round_winners[i]['winner'],
                loser = round_winners[i]['loser']
            )

    # save company to update the last changed time
    company.save()

    # return success
    return json_response(True, match_id=match.id)

@login_required
def delete_match(request, company_name):
    required_fields = {
        'match_id': {
            'validation': lambda a: a.isdigit(), 'clean': lambda a: int(a)}
    }
    validate_result = validate_required(request.POST, required_fields)
    if not validate_result[0]:
        return json_response(
                False, error_message="Invalid Field: %s " % str(validate_result[1].keys()[0]))
    clean = validate_result[1]
    match_id = clean['match_id']

    try:
        company = Company.objects.filter(short_name = company_name).get()
    except ObjectDoesNotExist:
        # todo: show signup form
        raise Http404()

    # get match
    try:
        match = company.match_set.get(pk=match_id)
    except ObjectDoesNotExist:
        return json_response(False, error_message="Invalid Match")

    # check permission
    if not company.check_permission(request.user):
        # todo: show permission denied
        raise Http404()

    # delete the match
    match.delete()

    # recalculate everything to fix the user caches
    company.recache_matches()

    # return success
    return json_response(True)

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

    # save company to update the last changed time
    company.save()

    # return success
    return json_response(True, player_id = player.id)

def add_company(request):
    required_fields = {
        'company_name': {
            'validation': lambda a: len(a.strip()) >= 3,
            'clean': lambda a: a.strip()},
        'password': {
            'validation': lambda a: len(a.strip()) >= 3,
            'clean': lambda a: a.strip()},
        'email': {
            'validation': lambda a: len(a.strip()) >= 3 and a.find('@') > -1,
            'clean': lambda a: a.strip()
        }
    }
    validate_result = validate_required(request.POST, required_fields)
    if not validate_result[0]:
        # get one field out of validation response
        field_name = validate_result[1].keys()[0]
        return json_response(
                False,
                error_message="Invalid Field: %s" % (field_name.title())
            )
    clean = validate_result[1]

    company_name = clean['company_name']
    password = clean['password']
    email = clean['email']

    # check if company with the same name already exists
    if Company.objects.filter(short_name = company_name).exists():
        return json_response(
                False, error_message="A company with that name already exists.")

    # create company
    company = Company.objects.create(short_name=company_name, name=company_name)

    # create user account
    user = User.objects.create_user(company_name, email, password)
    user.profile.company = company
    user.save()

    # log the user account in
    user = authenticate(username=company_name, password=password)
    login(request, user)

    # return success
    return json_response(
            True,
            redirect = reverse(
                "account"
            )
        )

@login_required
def check_for_update(request, company_name):
    try:
        company = Company.objects.filter(short_name = company_name).get()
    except ObjectDoesNotExist:
        # todo: show signup form
        raise Http404()

    # check permission
    if not company.check_permission(request.user):
        return json_response(False, {
            "error_message": "Permission Denied"
        })

    # return the company's latest_change
    timestamp = time.mktime(company.latest_change.timetuple())
    return json_response(True,
        latest_change = timestamp
    );
