"""
Production settings and globals.

Debug OFF

Djeroku Defaults:
    SMTP Email -- Requires EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT
    postgresify for heroku postgres configuration
    memcachify for heroku memcache configuration
    redisify for heroku redis cache configuration
    amqplib for queue management -- RABBITMQ_URL or CLOUDAMQP_URL -- look at celery config section about workers/connections
    django-pipeline + storages
        -- optionally with s3boto -- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
    HTML Compression from pipeline


What you need to set in your heroku environment (heroku config:set key=value):

    Your production environment SECRET_KEY (created and set by the fabric script)

    Email:
        Defaults to mandril, which is already set up when added to your app

        There is also a commented version that uses your gmail address.
        For more control, you can set any of the following keys in your
        environment:
        EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT

    If you enable S3 storages, set the following keys with your amazon info:
        AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME

"""

from os import environ

# automagically configures your database to use whatever heroku postgres
# credentials are in your environment (automatically put there by heroku)
from postgresify import postgresify

# automagically sets up whatever memcache heroku addon you have as the cache
# https://github.com/rdegges/django-heroku-memcacheify
from memcacheify import memcacheify

# use redisify instead of memcacheify if you prefer
# https://github.com/dirn/django-heroku-redisify
#from redisify import redisif

from common import *


########## ALLOWED HOSTS
# https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [] # you MUST add your domain names here, check the link for details
########## END ALLOWED HOSTS

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls

EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.mandrillapp.com')
EMAIL_HOST_PASSWORD = environ.get('MANDRILL_APIKEY', '')
EMAIL_HOST_USER = environ.get('MANDRILL_USERNAME', '')
EMAIL_PORT = environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True

# use this to channel your emails through a gmail powered account instead
#EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')
#EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@gmail.com')
#EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')
#EMAIL_PORT = environ.get('EMAIL_PORT', 587)
#EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES = postgresify()

SOUTH_DATABASE_ADAPTERS = {
    'default': 'south.db.postgresql_psycopg2'
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = memcacheify()
#CACHES = redisify()
########## END CACHE CONFIGURATION


########## CELERY CONFIGURATION
# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-transport
BROKER_TRANSPORT = 'amqplib'

# Set this number to the amount of allowed concurrent connections on your AMQP
# provider, divided by the amount of active workers you have.
#
# For example, if you have the 'Little Lemur' CloudAMQP plan (their free tier),
# they allow 3 concurrent connections. So if you run a single worker, you'd
# want this number to be 3. If you had 3 workers running, you'd lower this
# number to 1, since 3 workers each maintaining one open connection = 3
# connections total.
#
# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-pool-limit
BROKER_POOL_LIMIT = 3

# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-connection-max-retries
BROKER_CONNECTION_MAX_RETRIES = 0

# See: http://docs.celeryproject.org/en/latest/configuration.html#broker-url
BROKER_URL = environ.get('RABBITMQ_URL') or environ.get('CLOUDAMQP_URL')

# See: http://docs.celeryproject.org/en/latest/configuration.html#celery-result-backend
CELERY_RESULT_BACKEND = 'amqp'
########## END CELERY CONFIGURATION


########## STORAGE CONFIGURATION
# See: http://django-storages.readthedocs.org/en/latest/index.html
INSTALLED_APPS += (
    'storages',
)

# See: http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html#settings
#STATICFILES_STORAGE = DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE = 'pipeline.storage.PipelineCachedStorage'
#STATICFILES_STORAGE = DEFAULT_FILE_STORAGE = 'lib.djeroku.storages.S3CachedPipelineStorage'

# See: http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html#settings
#AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN

# See: http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html#settings
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_AUTO_CREATE_BUCKET = True
AWS_QUERYSTRING_AUTH = False

# AWS cache settings, don't change unless you know what you're doing:
AWS_EXPIREY = 60 * 60 * 24 * 7
AWS_HEADERS = {
    'Cache-Control': 'max-age=%d, s-maxage=%d, must-revalidate' % (AWS_EXPIREY,
        AWS_EXPIREY)
}

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url

# use something like this if using boto (check your bucket/cloudfront settings)
# STATIC_URL = '//%s.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
########## END STORAGE CONFIGURATION

########## PIPELINE CONFIGURATION

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.cssmin.CssminCompressor'

########## END PIPELINE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = environ.get('SECRET_KEY', SECRET_KEY)
########## END SECRET CONFIGURATION

########## ADDITIONAL MIDDLEWARE
MIDDLEWARE_CLASSES += (
   'pipeline.middleware.MinifyHTMLMiddleware',
   )
########## END ADDITIONAL MIDDLEWARE
