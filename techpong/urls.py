from django.contrib import admin
from django.conf.urls import *

# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()


# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = [
    url(r'', include('apps.techpong.urls')),
    url(r'api/v1/', include('apps.techpong.api.api_urls')),

    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls))
]
