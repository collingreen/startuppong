from coffin.conf.urls import *

urlpatterns = patterns('apps.techpong.api.api_views',
    url(r'^test$', 'test'),
    url(r'^get_players$', 'get_players'),
    url(r'^get_recent_matches_for_company$', 'get_recent_matches_for_company'),
    url(r'^get_recent_matches_for_player$', 'get_recent_matches_for_player'),
    url(r'^get_recent_matches_between_players$', 'get_recent_matches_between_players'),

    url(r'^add_match$', 'add_match'),
)
