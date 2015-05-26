from django.shortcuts import render, render_to_response, Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as auth_logout
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.template.context_processors import csrf
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from apps.techpong.models import *
from apps.techpong.tools.view_tools import create_sparklines
import datetime
import math

# controls how far the ratings graph extends past the min and max
RATINGS_GRAPH_RANGE_MULTIPLIER = .1

# public pages
def index(request):
    return render(request, 'techpong/index.html', dict(
        total_companies = Company.objects.count(),
        total_players = Player.objects.count(),
        total_matches = Match.objects.count(),
        total_rounds = Round.objects.count()
        ))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(
            reverse('index')
        )

@login_required
def dashboard_redirect(request):
    if request.user.profile.company:
        return HttpResponseRedirect(
                reverse(
                    "dashboard",
                    kwargs = {
                        'company_name': request.user.profile.company.short_name
                    }
                )
            )
    raise Http404()

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
                error_message='Could not find Company "%s"' % company_name
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

    # check if company is currently recalculating
    if company.recalculating:
        return render(request, 'techpong/recalculating.html', {
            'company': company
        })

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

    # check if company is currently recalculating
    if company.recalculating:
        return render(request, 'techpong/recalculating.html', {
            'company': company
        })

    # process cached data
    cached_results = json.loads(player.cached_results or '[]')
    cached_ratings = json.loads(player.cached_rating_changes or '[]')
    cached_ranks = json.loads(player.cached_rank_changes or '[]')
    create_sparklines(player)

    # ratings graphs
    ymin, ymax = None, None
    for rating_info in cached_ratings:
        rating = rating_info['rating']
        if rating < ymin or ymin is None:
            ymin = rating
        if rating > ymax or ymax is None:
            ymax = rating

    if ymin is None:
        ymin = 0
    if ymax is None:
        ymax = 500
    ratings_spread = ymax - ymin
    graph_offset = RATINGS_GRAPH_RANGE_MULTIPLIER * ratings_spread

    graph_min = max(0, 10 * round((ymin - graph_offset) / 10))
    graph_max = 10 * math.ceil((ymax + graph_offset) / 10)

    # render the player screen
    return render(request, 'techpong/player.html', {
                        'player': player,
                        'company': company,
                        'cached_results': cached_results,
                        'cached_ratings': cached_ratings,
                        'cached_ranks': cached_ranks,
                        'ymin': graph_min,
                        'ymax': graph_max
                        })

@login_required
def account(request):
    if not request.user.is_active:
        return render(
            request,
            'techpong/error.html',
            dict(
                error_title="Account Inactive",
                error_message="Your account is currently inactive. Please contact an administrator."
            )
        )
    # create form from company model
    company_form_class = modelform_factory(Company, fields=(
        'name', 'location',
        'show_rank', 'show_rating', 'order_by')
    )

    # handle post
    if request.method == 'POST':
        company_form = company_form_class(
                request.POST, instance=request.user.profile.company)
        if company_form.is_valid():
            company_form.save()
    else:
        company_form = company_form_class(instance=request.user.profile.company)

    # render account page
    return render(request, 'techpong/account.html', {
        'form': company_form,
        'company': request.user.profile.company,
        'player': request.user,
        'api_account_id': request.user.profile.company.get_api_account_id(),
        'api_access_key': request.user.profile.company.get_api_access_key()
    })

@login_required
@user_passes_test(lambda user: user.is_staff)
def recache_matches(request):
    # replay all matches
    count = 0
    for company in Company.objects.all():
        count += 1
        company.recache_matches()

    return HttpResponse("Recached all matches for %d companies" % count)

@login_required
def api_docs(request, api_version='latest'):
    # TODO: implement, then enforce api version :D
    # TODO: get api prefix from url config
    api_version = 1
    api_version_url_path = 'v1'

    company = request.user.profile.company
    players = company.player_set.all()
    player1, player2 = None, None
    if len(players) > 0:
        player1 = players[0]
    if len(players) > 1:
        player2 = players[1]

    raw_new_player_name = 'new_player'
    new_player_name = raw_new_player_name
    count = 1
    while Player.objects.filter(
            name=new_player_name,
            company=company).count() > 0:
        count += 1
        new_player_name = raw_new_player_name + str(count)

    return render(request, 'techpong/docs.html', dict(
        api_version=api_version,
        api_prefix='/api/%s/' % api_version_url_path,
        api_account_id=request.user.profile.company.get_api_account_id(),
        api_access_key=request.user.profile.company.get_api_access_key(),

        players=players,
        player1=player1,
        player2=player2,
        new_player_name=new_player_name
        ))
