import urllib, hashlib

#from django import template
from coffin import template
register = template.Library()

@register.filter
def gravatar_url(email, size=32):
    """Filter for linking to a gravatar image.
    Example:
        <img src="{{user.email|gravatar_url()}}"/>
    # https://en.gravatar.com/site/implement/images/python/
    # construct the url
    """
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'s':str(size)})

    return gravatar_url
