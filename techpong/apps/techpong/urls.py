from coffin.conf.urls import *
from django.contrib.auth.views import login, logout

urlpatterns = patterns('apps.techpong',

    url(r'^$', 'views.index', name='index'),
    url(r'^pingpong/(?P<company_name>\w+)/$', 'views.dashboard', name='dashboard'),
    url(r'^pingpong/(?P<company_name>\w+)/(?P<player_id>\d+)$', 'views.player', name='player'),

    url(r'^tools/recache_matches/$', 'views.recache_matches'),

    url(r'^login/$', login, name='login'),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, name='logout'),

    # ajax calls
    url(r'^pingpong/(?P<company_name>\w+)/ajax/add_match/$', 'ajax_views.add_match', name='ajax_add_match'),
    url(r'^pingpong/(?P<company_name>\w+)/ajax/add_player/$', 'ajax_views.add_player', name='ajax_add_player')
)
