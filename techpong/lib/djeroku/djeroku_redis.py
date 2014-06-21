"""
djeroku_redis.py
Collin Green


Was originally created as a covenient way to transparently
use any of the redis addons from heroku (or localhost, or anything else),
based on memcacheify by RDegges.

However, github user dirn had already created the same thing, but better, for
the cache settings part.

In that light, this library has been renamed to djeroku_redis and is now
solely for getting a redis connection directly. dirn's django-heroku-redisify
should be used for setting up django to use redis as a cache.

Memcacheify by RDegges
https://github.com/rdegges/django-heroku-memcacheify

Redisify by dirn
https://github.com/dirn/django-heroku-redisify/blob/develop/redisify.py


Supports:
    MyRedis - https://addons.heroku.com/myredis
    OpenRedis - https://addons.heroku.com/openredis
    RedisCloud - https://addons.heroku.com/rediscloud
    RedisGreen - https://addons.heroku.com/redisgreen
    RedisToGo - https://addons.heroku.com/redistogo


TODO:
    test each heroku provider
    test manual override
"""

from os import environ
from django.conf import settings
import urlparse
import redis

REDIS_PROVIDERS = {
    'MyRedis':      {'config_url': 'MYREDIS_URL'},
    'OpenRedis':    {'config_url': 'OPENREDIS_URL'},
    'RedisToGo':    {'config_url': 'REDISTOGO_URL'},
    'RedisCloud':   {'config_url': 'REDISCLOUD_URL'},
    'RedisGreen':   {'config_url': 'REDISGREEN_URL'},
}

def redis_setup(fail_silently=False):
    """Automagic setup of redis addons on heroku. Sets REDIS_SERVER_URL,
    in your environment and provides a helper function to get a redis
    connection. Makes setting up redis a one line affair and makes it
    trivial to switch redis providers. If REDIS_SERVER_URL is already
    set in your environment, this is used instead, giving you full
    control (if you desire).

    Technically this is already called by redis_connection, so you
    do not need to call this directly. However, in the interest of
    being explicit, you could call redis_setup() from your settings
    file.
    """

    # default to manually set REDIS_SERVER_URL
    if environ.get('REDIS_SERVER_URL'):
        return True

    # if REDIS_SERVER_URL in settings, try that (good for specifying on development)
    elif hasattr(settings, 'REDIS_SERVER_URL'):
        environ['REDIS_SERVER_URL'] = settings.REDIS_SERVER_URL
        return True

    # look for each provider's setting in the environment
    for provider, provider_info in REDIS_PROVIDERS.iteritems():
        connection_string = environ.get(provider_info['config_url'])
        if connection_string:
            environ['REDIS_SERVER_URL'] = connection_string
            return True

    # didnt find one, raise exception
    if not fail_silently:
        raise Exception("Could not find redis provider. Please manually set REDIS_SERVER_URL in your settings or environment")

def redis_connection(db=0):
    """Returns a connection to your redis server.

    Usage:
        r = redis_connection()

        # any redis call now -- example: ping the server
        r.ping()
    """

    # if was not set up yet, try it now
    redis_url = environ.get('REDIS_SERVER_URL')
    if redis_url is None:
        redis_setup()
        redis_url = environ.get('REDIS_SERVER_URL')

    # http://redis-py.readthedocs.org/en/latest/
    # try parsing the url for port and password
    parsed = urlparse.urlparse(redis_url)

    # if no hostname, assume url is raw
    if parsed.hostname is None:
        return redis.Redis(redis_url, db=db)

    # otherwise, try to auto-config from redis
    return redis.from_url(redis_url, db=db)