"""
Useful middlewares.
"""

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class SslOnlyMiddleware(object):
"""
This is taken directly from rdegges django-sslify project with an extra
header check to support heroku (HTTP_X_FORWARDED_PROTO).
"""
    def process_request(self, request):
        if getattr(settings, 'DISABLE_SSL', False):
            return None

        if not settings.DEBUG \
                and not request.is_secure() \
                and not request.META.get('HTTP_X_FORWARDED_PROTO', '') == 'https':
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://')
            return HttpResponsePermanentRedirect(secure_url)
