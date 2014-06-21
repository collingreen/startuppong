"""
fabfile.py

Fabric file for setting up a fully functional staging+production
enviornment on heroku.

1. Creates a staging and a production app, adds all the necessary settings, and
    provisions a list of free addons.
2. Creates a pipeline from staging to production.
3. Creates a git repository and sets up remotes.


Set everything up:
    fab heroku_setup

Deploy to Staging:
    git push staging master

Promote Staging slug to Production:
    heroku pipeline:promote

Deploy directly to Production:
    git push production master

"""

from fabric.contrib.console import confirm, prompt
from fabric.api import abort, env, local, settings, task

########## GLOBALS
env.run = 'heroku run python manage.py'
HEROKU_ADDONS = (
    'cloudamqp:lemur',
    'heroku-postgresql:dev',
    'scheduler:standard',
    'redistogo:nano',
    'memcachier:dev',
    'newrelic:stark',
    'pgbackups:auto-month',
    'sentry:developer',
    'mandrill:starter',
    'papertrail:choklad'
)
HEROKU_CONFIGS = (
    'DJANGO_SETTINGS_MODULE=techpong.settings.prod',
    #'AWS_ACCESS_KEY_ID=xxx',
    #'AWS_SECRET_ACCESS_KEY=xxx',
    #'AWS_STORAGE_BUCKET_NAME=xxx',
)
########## END GLOBALS

########## HELPERS
def cont(cmd, message):
    """Given a command, ``cmd``, and a message, ``message``, allow a user to
    either continue or break execution if errors occur while executing ``cmd``.

    :param str cmd: The command to execute on the local system.
    :param str message: The message to display to the user on failure.

    .. note::
        ``message`` should be phrased in the form of a question, as if ``cmd``'s
        execution fails, we'll ask the user to press 'y' or 'n' to continue or
        cancel execution, respectively.

    Usage::

        cont('heroku run ...', "Couldn't complete %s. Continue anyway?" % cmd)
    """
    with settings(warn_only=True):
        result = local(cmd, capture=True)

    if message and result.failed:
        print result.stderr
        if not confirm(message):
		  abort('Stopped execution per user request.')

@task
def generate_secret_key(key_length=64):
    """Simple convenience function to randomly generate a 64 character key
    you can stick in your settings/environment"""
    import string, random
    options = string.digits + string.letters + ".,!@#$%^&*()-_+={}"
    print ''.join([random.choice(options) for i in range(key_length)])

########## END HELPERS



########## HEROKU MANAGEMENT
@task
def heroku_setup():
    """Set up everything you need on heroku. Creates a production app
    (remote: production) and an identical staging app (remote: staging) and
    does the following:

        - Create new Heroku applications.
        - Install all ``HEROKU_ADDONS``.
        - Set all ``HEROKU_CONFIGS``.
        - Initialize New Relic's monitoring add-on.

    https://devcenter.heroku.com/articles/multiple-environments

    NOTE: the production app will have ENVIRONMENT_TYPE=production while staging
    will have ENVIRONMENT_TYPE=staging if the code needs to know which environment
    it is running in (for example, so staging can use a non-production db follower)
    """
    app_name = prompt('What name should this heroku app use?', default='techpong')
    staging_name = '%s-staging' % app_name

    staging_remote = 'staging'
    production_remote = 'production'

    # create the apps on heroku
    cont('heroku apps:create %s --remote %s --addons %s' %
            (staging_name, staging_remote, ','.join(HEROKU_ADDONS)),
            "Failed to create the staging app on heroku. Continue anyway?")
    cont('heroku apps:create %s --remote %s --addons %s' %
            (app_name, production_remote, ','.join(HEROKU_ADDONS)),
            "Failed to create the production app on heroku. Continue anyway?")

    # set configs
    for config in HEROKU_CONFIGS:
        cont('heroku config:set %s --app=%s' % (config, staging_name),
            "Failed to set %s on Staging. Continue anyway?" % config)
        cont('heroku config:set %s --app=%s' % (config, app_name),
            "Failed to set %s on Production. Continue anyway?" % config)

    # set debug
    cont('heroku config:set DEBUG=True --app=%s' % staging_name,
        "Failed to set DEBUG on Staging. Continue anyway?")
    cont('heroku config:set DEBUG=False --app=%s' % app_name,
        "Failed to set DEBUG on Production. Continue anyway?")

    # set environment type
    cont('heroku config:set ENVIRONMENT_TYPE=staging --app=%s' % staging_name,
        "Failed to set ENVIRONMENT_TYPE on Staging. Continue anyway?")
    cont('heroku config:set ENVIRONMENT_TYPE=production --app=%s' % app_name,
        "Failed to set ENVIRONMENT_TYPE on Production. Continue anyway?")

##    # this is a buildpack that includes npm (the node package manager) which
##    # makes it easy to include things like coffeescript or less compilers
##    # set buildpack
##    cont('heroku config:set BUILDPACK_URL=git://github.com/galuszkak/heroku-buildpack-django.git --app %s' % staging_name,
##         "Failed to set BUILDPACK_URL. Continue anyway without npm_requirements?")
##    cont('heroku config:set BUILDPACK_URL=git://github.com/galuszkak/heroku-buildpack-django.git --app %s' % app_name,
##         "Failed to set BUILDPACK_URL. Continue anyway without npm_requirements?")

    # set user-env-compile or versioned static assets won't work!
    cont( 'heroku labs:enable user-env-compile --app=%s' % staging_name,
            "Failed to set user-env-compile on Staging. This will block versioned static assets. Continue anyway?")
    cont( 'heroku labs:enable user-env-compile --app=%s' % app_name,
            "Failed to set user-env-compile on Production. This will block versioned static assets. Continue anyway?")

    # create a pipeline from staging to production
    cont( 'heroku labs:enable pipelines',
            "Failed to enable Pipelines. Continue anyway?")
    cont( 'heroku plugins:install git://github.com/heroku/heroku-pipeline.git',
            "Failed to install pipelines plugin. Continue anyway?")
    cont( 'heroku pipeline:add -a %s %s' % (staging_name, app_name),
            "Failed to create pipeline from Staging to Production. Continue anyway?")

    # start newrelic
    cont( ('%(run)s newrelic-admin validate-config - stdout --app=' % env) + staging_name,
            "Failed to initialize New Relic on Staging. Continue anyway?")
    cont( ('%(run)s newrelic-admin validate-config - stdout --app=' % env) + app_name,
            "Failed to initialize New Relic on Production. Continue anyway?")

    # set git to default to staging
    local('git init')
    local('git config heroku.remote staging')
########## END HEROKU MANAGEMENT
