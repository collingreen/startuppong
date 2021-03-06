from coffin.conf.urls import *
from django.contrib.auth.views import login

urlpatterns = patterns('apps.techpong',

    url(r'^$', 'views.index', name='index'),
    url(r'^pingpong/dashboard/$', 'views.dashboard_redirect', name='dashboard_redirect'),
    url(r'^pingpong/(?P<company_name>\w+)/$', 'views.dashboard', name='dashboard'),
    url(r'^pingpong/(?P<company_name>\w+)/(?P<player_id>\d+)$', 'views.player', name='player'),

    url(r'^api/(?P<api_version>\w+)/docs/$', 'views.api_docs', name='api_docs'),
    url(r'^api/latest/docs/$', 'views.api_docs', name='api_docs'),

    url(r'^tools/recache_matches/$', 'views.recache_matches'),

    url(r'^login/$', login, name='login'),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', 'views.logout', name='logout'),
    url(r'^accounts/edit$', "views.account", name='account'),

    # ajax calls
    url(r'^pingpong/(?P<company_name>\w+)/ajax/add_match/$', 'ajax_views.add_match', name='ajax_add_match'),
    url(r'^pingpong/(?P<company_name>\w+)/ajax/delete_match/$', 'ajax_views.delete_match', name='ajax_delete_match'),
    url(r'^pingpong/(?P<company_name>\w+)/ajax/add_player/$', 'ajax_views.add_player', name='ajax_add_player'),
    url(r'^pingpong/(?P<company_name>\w+)/ajax/check_for_update/$', 'ajax_views.check_for_update', name='ajax_check_for_update'),
    url(r'^accounts/signup$', 'ajax_views.add_company', name='ajax_signup'),
    url(r'^accounts/reset_api_access_key$', "ajax_views.reset_api_access_key", name='ajax_reset_api_access_key'),
    url(r'^accounts/set_viewed_notifications$', "ajax_views.set_viewed_notifications", name='ajax_viewed_notifications'),
)
