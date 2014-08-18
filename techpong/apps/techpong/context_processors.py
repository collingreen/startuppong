
import os

def google_analytics_key(request):
    return {'google_analytics_key': os.environ.get('google_analytics_key')}
