from coffin.conf.urls import *

urlpatterns = patterns('apps.techpong.api.api_views',
    url(r'^test$', 'test'),
    url(r'^get_players$', 'get_players'),
)
