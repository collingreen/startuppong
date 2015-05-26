from django.conf.urls import *
from apps.techpong.api import api_views

urlpatterns = [
    url(r'^test$', api_views.test),
    url(r'^get_players$', api_views.get_players),
    url(r'^get_recent_matches_for_company$', api_views.get_recent_matches_for_company),
    url(r'^get_recent_matches_for_player$', api_views.get_recent_matches_for_player),
    url(r'^get_recent_matches_between_players$', api_views.get_recent_matches_between_players),

    url(r'^add_match$', api_views.add_match),
    url(r'^add_player$', api_views.add_player)
]
