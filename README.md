Djeroku - Django + Heroku
=========================

Djeroku is the amalgamation of all the tips and tweaks I've gathered
while doing django development on heroku. If you have developed a few sites
and have them working on heroku, 95% of this won't be a surprise, since you
will have already solved all the same issues, most likely through
substantial quantities of your blood, sweat, and/or tears.

If you are just starting to play with django or you haven't designed a site
from the ground up with scalability in mind, Djeroku (or django-skel
or any of several other great options) is a great starting point so you are
set up correctly from the beginning. Django can do so many things that just
knowing where to start can be a giant barrier to entry.

Most importantly - if you find something wrong, misleading, dangerous, or
just stupid, send me an email at maintainer@djeroku.com

Djeroku's History (aka, what the hell is DLAB?)
=================

Djeroku began as the django-skel project by Randall Degges, which is a
fantastic django project skeleton that solves 90% of everything you'll ever
need. Before I found django-skel I had cobbled together my own similar
solutions, incorporating best practice suggestions (sometimes excellent,
sometimes terrible!) from various articles on the internet and implementing
many things the HARD way (ex: I cannot BELIEVE how long it took
me to start using fabric) and plenty of things the STUPID way (I won't even
share how I was originally switching between dev vs production settings).

Djeroku was born as a project (and originally called DLAB - Django Like a Boss)
when I took everything I had learned and
combined it with the django-skel project, throwing in my own personal
preferences on top (like Jinja2 templates and redis). Djeroku is now the
first thing I grab whenever I'm ready to start a new project of any size.
It covers everything I've ever needed so far - easy development,
easy deployment, caching, qeueing, correct static hosting (directly
in gunicorn or on S3), scheduled tasks, new relic monitoring,
useful logging, and sentry for figuring out what happened when it
all goes wrong.

Be aware: Djeroku is meant to do one thing. There is nothing tricky about
how it works so you can easily tweak and change things as you desire, but
the goal is to get a django webapp up and running as quickly as possible
with the end goal of deploying through heroku. You can, of course, do whatever
you want, but the tools are all geared toward that end and make that exact
process extremely easy.

Most importantly, there are a TON of things that are simply my preference -
take everything with a big grain of salt and *never* assume I know more
than you.


Why not just contribute to django-skel?
======================================
django-skel is excellent at coordinating the tools it uses. However, for some
tasks I prefer different solutions, and those don't always play nicely with
the existing setup (ex: jinja2 vs vanilla, django-pipeline vs compressor).
Instead of trying to change the django-skel setup to facilitate lots of options
(which would destroy the simplicity that makes django-skel great) and
simultaneously patching the abandoned compressor project, Djeroku is the same
kind of project with a slightly different toolset.


What Djeroku Uses - An Incomplete List
==============
- Virtualenv
- Pip
- Distribute
- Fabric -- for deployment and all the little bits associated with it
- Django 1.5
- jinja2 -- faster and more powerful template rendering (elif tags - need I say more?)
- Gunicon and GEvent -- lightweight webserver
- Celery, Kombu, and RabbitMQ -- proper queue/worker setup for real web apps
- django-pipeline + jsmin + cssmin - compression and versioning of your static files
- django-storages
- south - database migrations (so you don't go on a killing rampage when the time comes to update your deployed schema)
- gargoyle + nexus -- control features by user groups, implement A/B testing, etc
- memcache/redis - caching and faster sessions
- sqlite + postgres - quick and easy development db, full scale production db
- heroku newrelic - application monitoring
- heroku papertrail - exception tracking
- heroku scheduler - scheduled tasks without cron or requiring a celery worker
- heroku postgres backup - automatically manages your database backups

Djeroku deploys to heroku which handles EVERYTHING about the devops. You can run
everything above on heroku for free (for a small site), then scale up with a
few clicks to literally hundreds of web processes and queue workers. Heroku
charges by the second, so when you are finished with your 2 day
slashdot/reddit/whatever bombardment you can scale back down and only pay
for what you used. THIS IS BETTER THAN WHAT YOU WERE DOING BEFORE (probably).

Here is a nice primer, written by the heroku guys themselves, on the entire
'creating a site that actually scales' topic: http://12factor.net/
Note - not everyone agrees with the 'platform as a service' approach
so you should definitely do some research before diving in too deep.

What Djeroku Solves
================
- a sane way to switch between development and production environments
- keeping proper settings in environment variables, NOT in the code and repository
- setting up a proper deployment webserver with monitoring and logging
- setting up a proper deployment database using heroku's postgres
- setting up a working queue with scalable scheduler and worker processes
- setting up working memcache and/or redis connections
- working email settings for heroku deployment
- static file concatenation, compression, and versioning
- hosting static files from gunicorn or S3
- database migrations using south
- creating and setting everything up correctly on heroku
- deploying correctly every time on heroku


How It Works
============
Djeroku is really just a way to organize a bunch of tools that you might
need, the relevant settings so they work together, and some tools to make
deployment a breeze instead of a nightmare.

When you first create your project using django-admin you specify Djeroku as
the project template and django builds you out a new project layout.

The root contains the heroku procfile defining the necessary workers
(gunicorn web worker with newrelic monitoring, queue scheduler,
and queue worker), a default gunicorn config, a fabfile for setting up your
heroku apps correctly the first time, dev/production settings, and
dev/production requirements files.

The top level requirements.txt simply links to the production
requirements file in the reqs/ folder, which in turn extends the common
reqs/common.txt requirements. In the production environment heroku will find
the requirements.txt file and automatically install all your production
requirements.

On development, manually install all your dev requirements using
pip install -r reqs/dev.txt

Anything used on both development and production should go in common,
while environment specific libraries should be in their respective dev
(ex: debug tools) or prod (ex: css/js compressors) files.

Inside the project folder, the settings work the same way with common.py
holding all the overlapping settings and dev.py/prod.py overwriting as
necessary.

The libs folder is there for convenience so you can host external
tools and libraries that don't belong as part of a full app. Djeroku has a
module there with some simple tools that might come in handy (like a storages
extension to enable versioning/compressing AND uploading static files to S3).

All the apps that fit together to make your project go in their own folder
inside the apps folder. This keeps everything clean, but remember to
import apps.app_name.whatever.


Quick Start -- Updated 2013-08-18
===========

Install pip, setuptools, git, and virtualenv on your system
    sudo apt-get install pip, setuptools, git

On windows - http://www.pip-installer.org/en/latest/installing.html
Download latest ez_setup.py from setuptools pypi page

    python ez_setup.py
    downloaded https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py

    sudo pip install virtualenv

Create project directory
    mkdir PROJECT_NAME

Create a new virtualenv directory - if you don't understand why you
absolutely should use virtualenv for any size project, go read
the 'longer reading' section. I call my virtual environments venv - you can do whatever you like
    virtualenv PROJECT_NAME/venv

Source the virtualenv and install all the development requirements

    source PROJECT_NAME/venv/bin/activate
    (windows: PROJECT_NAME/venv/Scripts/activate.bat)

Install django 1.5.x -- notice the quotes

    pip install "django>=1.5,<1.6"

Create a new django project using Djeroku as the template

    python venv/Scripts/django-admin.py startproject --template=path/to/djeroku/git-or-zip-or-folder --extension=py,html PROJECT_NAME

    cd PROJECT_NAME
    pip install -r PROJECT_NAME/reqs/dev.txt

The django-skel docs have great advice here if the above command fails:
you are missing required libraries --
on ubuntu, installing the following solves it
- libevent-dev
- libpq-dev
- libmemcached-dev
- zlib1g-dev
- libssl-dev
- python-dev
- build-essential


----------------------
When you are ready to create your first app, use the django-admin command
again, this time with the djeroku-app template. If you forget the --extension
flag below, the default djeroku_app templates will not be copied
correctly. Not the end of the world, but you might as well get it right.

    cd PROJECT_NAME/PROJECT_NAME/apps
    python ../../../venv/Scripts/django-admin.py startapp --template=path/to/djeroku-app/git-or-zip-or-folder --extension=py,html APP_NAME

Open up settings/common.py and add your new app to the LOCAL_APPS tuple

    LOCAL_APPS = (
	    'apps.APP_NAME',
    )

Next, hook up the app urls in the project urls.py by adding this line as the
first item inside the urlpatters call (before the admin urls,
but either way should work)

    url(r'', include('apps.APP_NAME.urls')),

Test that it all went according to plan

    python manage.py syncdb
    python manage.py migrate
    python manage.py runserver

Open 127.0.0.1:8000 in your browser -- you should see the djeroku hello world page.


One Time Setup
--------------
At this point you can set up your apps on heroku. Navigate to the
directory with the fabfile, call the following command, and
answer the prompts. If something goes wrong,
you'll get a message and be prompted to continue or abort.

    fab heroku_setup

If everything goes smoothly, you'll have a production app, and an (almost)
identical staging app, both with their own versions of a bunch of useful
free heroku addons. Moreover, each will be set up to use your production
settings AND the staging app will have a heroku pipeline set up so,
when you're ready, you can push your working and tested project slug
from the staging server directly to production without having to mess
about with re-pushing anything.

You'll also have a new git repository in which you can track your code.
    git status


Now go write some code until you're ready to deploy! Check out the
static assets section to learn about javascript and css minification
and versioning. Check out the deployment section for getting your
app from development into staging and on to production



Static Assets
=============
This section covers two distinct but related ideas -- hosting your static
assets and concatenating, compressing, and versioned them for maximum
performance.

Djeroku comes out the box set up to serve your static assets through the
regular gunicorn web process. This alone can handle more traffic than most sites
ever see. When you're ready to scale, add an edge CDN like CDNSumo or Amazon
Cloudfront that will automatically query your server when needed for necessary
assets (instead of having to manually deploy them each time, duplicating your
effort and adding another drastic point of potential failure). If you really
want to get your assets on a different server, Djeroku has a storages mixin
that uses Boto and django-pipeline to get all the benefits of versioning and
compression while sending your statics out to an Amazon S3 bucket.

If you go this route, be sure to set all the necessary amazon keys -- see the
deployment section and look at the fabfile for more details.


To get the very best performance possible, however, there are several things
you can and should do with your static assets to speed up the client experience:

#### 1. Concatenation
Concatenation just means grouping everything you can into single files.

This is trivial for css, works pretty well for javascript, and requires a
bit of work for images. The fewer total files there are for the client's
browser to download the better (up to a point). This is especially useful
for some browsers (certain versions of IE) that limit the number of files
being downloaded in parallel. You'll probably need to wrap your javascript
in (function(){ ... })() calls, but you're doing that anyway, right?

#### 2. Compression
Human readable CSS and javascript can be compressed in various ways to
yield much smaller files, directly correlating to faster load times. As a
bonus, the compression process generally makes your javascript much harder
to read after the fact, adding a tiny tiny layer of difficulty for people to
steal your code (at least 2 seconds while they copy everything and open
jsbeautifier.org).

#### 3. Versioning
The first two items reduce the total load time of your assets by
making changes to allow the browsers to download it all faster. Versioning,
on the other hand, enables you to safely tell the client's browser to cache
your files forever so they won't even try downloading them the next time they
visit the page. Doing this correctly requires you to not only set the right
cache forever headers but requires you to change the filename
for each static file every time it changes (otherwise the browser would never
know you made changes, since it doesnt ever download them again). Perfoming
this manually is a huge amount of work and is very error prone with severe
consequences for doing it incorrectly.

All of these things, while great for end user performance, generally get in
the way of clean development and are often quite involved to deploy AND are
easy to mess up. Djeroku uses django-pipeline, django-storages, and optionally
boto to make all this easy -- you can keep all your files separated by
source/topic/whatever you like and it will all be magically
handled behind the scenes.

In your settings files there are two sections for coordinating this:

    PIPELINE_CSS = {
        'colors': {
            'source_filenames': (
              'css/core.css',
              'css/colors/*.css',
              'css/layers.css'
            ),
            'output_filename': 'css/colors.css',
            'extra_context': {
                'media': 'screen,projection',
            },
        },
    }

    PIPELINE_JS = {
        'stats': {
            'source_filenames': (
              'js/jquery.js',
              'js/d3.js',
              'js/collections/*.js',
              'js/application.js',
            ),
            'output_filename': 'js/stats.js',
        }
    }

Each of these is a dictionary that groups all the files you want to join up,
compress, and version in the source_filenames and uses the key as the
reference you will use in your templates. Read the pipeline docs for details
on all the other options you have to tweak how this works.
http://django-pipeline.readthedocs.org/en/latest/configuration.html

Now, in your templates, instead of referencing your css and javascript files
directly, use the compressed_css and compressed_js tags and reference your
groups defined above.

    {% compressed_css 'colors' %}

On development (when DEBUG is True), this will just generate the direct
links you would normally expect:

    <link type='text/css' rel='stylesheet' href='css/core.css' media='screen,projection'/>
    (similar link for every css file in the css/colors directory)
    <link type='text/css' rel='stylesheet' href='css/layers.css' media='screen,projection'/>

On production, however, django-pipeline will join all those files up,
compress them, and give them a unique version number based on a hash of their
contents. The template will have just one link pointing to that single optimized
file AND it has a unique name every time it changes, so it can be cached forever
by your users or a CDN and you won't ever run into your own stale and out of
date code. Magic.

django-pipelines has a LOT of powerful options; check out the docs when
you have time.


Deployment
==========

Deploying your app should come in two steps --
First, you should push to your staging app and make sure
everything works there (remember to syncdb and migrate
anything else). After you have thoroughly tested everything
on staging, you can then promote the 'slug' of your app
on to production (you can also just push directly
to production, but promoting it along the pipeline
is cleaner, safer, and faster).

The following line will push the head commit of your master branch to staging

    git push staging master

Heroku will take this and do all its crazy magic to compile it
into your application 'slug'. After a couple minutes, the command
will finish and you can go to your-staging-app-name.herokuapp.com
and see it. You'll probably need to run the following first:

    heroku run python manage.py syncdb
    heroku run python manage.py migrate
    heroku run python manage.py collectstatic --noinput

Promoting the working slug from staging to production is trivial.
Get in the habit of first checking the diff between the two

    heroku pipeline:diff

If all looks as expected, promote it

    heroku pipeline:promote

If something goes terribly wrong, you can always

    heroku pipeline:rollback








Longer Reading
==============

Virtualenv
----------
Virtualenv allows you to make a little self contained sandbox for each of
your projects, allowing each one to have its own installations of all the
libraries and tools. This sounds like wasted effort and space, but what it
ACTUALLY does is gives you precise control over what is being used (which
*CAN* and *WILL* differ between projects! Some tools REQUIRE different versions of
various 3rd party tools!). More importantly, this enables you as the developer
to sync up other developer environments with the same versions of everything
(a DAUNTING task manually, even if you DO remember to check every version
of everything) AND make sure your deployment environment EXACTLY matches
your development environment. I personally guarantee this will save you
at least 10 hours down the road at some point, trying to track down why
'everything works on your dev machine!' but production is throwing a fit.

tl;dr - use a virtualenv for every project and you won't regret it
