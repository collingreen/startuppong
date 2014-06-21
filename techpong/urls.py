from django.contrib import admin
from coffin.conf.urls import *
import nexus

# sets up the default nexus site by detecting all nexus_modules.py files
nexus.autodiscover()


# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()


# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    url(r'', include('apps.techpong.urls')),

    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url('^nexus/', include(nexus.site.urls)),
)
