from coffin.shortcuts import render, render_to_response, Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.core.context_processors import csrf
from apps.techpong.models import *
from apps.techpong.tools.view_tools import create_sparklines
import datetime


# public pages
def index(request):
    return render(request, 'techpong/index.html', dict(
        total_companies = Company.objects.count(),
        total_players = Player.objects.count(),
        total_matches = Match.objects.count(),
        total_rounds = Round.objects.count()
        ))

@login_required
def dashboard(request, company_name):

    try:
        company = Company.objects.filter(short_name = company_name).get()
    except ObjectDoesNotExist:
        return render(
            request,
            'techpong/error.html',
            dict(
                error_title="Company Not Found",
                error_message='Could not find Company "%s"'
            )
        )

    # check permission
    if not company.check_permission(request.user):
        return render(
            request,
            'techpong/error.html',
            dict(
                error_title="Permission Denied",
                error_message='You do not have permission to access this ladder. You may need to log in to a different account.'
            )
        )

    # get company info
    company_info = company.get_info()

    # go through each player and add sparkline graph info
    for player in company_info['players']:
        create_sparklines(player)

    # render the dashboard
    return render(request, 'techpong/dashboard.html', {
                        "csrf_token": csrf(request)['csrf_token'],
                        'company': company,
                        'info': company_info
                    })

@login_required
def player(request, company_name, player_id):

    try:
        company = Company.objects.filter(short_name = company_name).get()
    except ObjectDoesNotExist:
        # todo: show signup form
        raise Http404()

    # check permission
    if not company.check_permission(request.user):
        # todo: show permission denied
        raise Http404()

    # look for target player in the same company
    try:
        player = Player.objects.filter(company=company, id=player_id).get()
    except ObjectDoesNotExist:
        raise Http404()

    # process cached data
    cached_results = json.loads(player.cached_results or '[]')
    cached_ratings = json.loads(player.cached_rating_changes or '[]')
    cached_ranks = json.loads(player.cached_rank_changes or '[]')
    create_sparklines(player)

    # render the player screen
    return render(request, 'techpong/player.html', {
                        'player': player,
                        'cached_results': cached_results,
                        'cached_ratings': cached_ratings,
                        'cached_ranks': cached_ranks
                        })

@login_required
@user_passes_test(lambda user: user.is_staff)
def recache_matches(self):
    # replay all matches
    count = 0
    for company in Company.objects.all():
        count += 1
        company.recache_matches()

    return HttpResponse("Recached all matches for %d companies" % count)
