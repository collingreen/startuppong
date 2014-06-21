
Djeroku_app - A Django App Template for Djeroku Projects
=========================

Djeroku_app was written to be used inside a Djeroku project installation
but it does not require the Djeroku project template. It does, however,
expect the Djeroku layout of an apps/ folder with your app inside it. If
you don't do this, you'll need to change some paths to accomodate.


### Quick Start

Djeroku_app is a django app template so you pass it to django-admin when
creating your app for the first time. Navigate to the folder where
you want your app and run

    django-admin.py startapp --template=path/to/djeroku_app_folder_or_git_or_zip --extensions=py,html app_name

This will create all the folders and put your app\_name everywhere it belongs.
NOTE: You CANNOT just copy the folders into your project! Django app
templates are run through django's template renderer and Djeroku\_app REQUIRES
this. If you don't do this you'll have weird {{template_variables}} in your
code and nothing will work or be named correctly.

More info about adding a Djeroku_app to a Djeroku project is covered in the
Djeroku readme.

### Using Djeroku_app

Djeroku_app will create the basic files for your app with all the paths set.
You'll see the regular admin.py, models.py, tests.py, urls.py, and views.py.
You will also have a templates folder containing a folder for your app, a
templatetags folder for any tags you need to add, and a static folder for
all your static files.

You'll see some example templates that include some useful snippets, like all
the little apple icons, loading external libraries from a CDN using // while
staying protocol agnosting, a google analytics
block that only shows up when DEBUG is False, and using the compressed tags
from django-pipeline.

The default Djeroku\_app templates include a base template, an index with
one of the bootstrap default pages, and working 404 and 500 pages.

### HTML5 Boilerplate + Bootstrap

https://github.com/h5bp/html5-boilerplate

http://getbootstrap.com

The template code is a combination of bootstrap and html5-boilerplate.

PLEASE go look at the docs for both toolkits.

Especially important note about X-UA-Compatible
https://github.com/h5bp/html5-boilerplate/blob/master/doc/html.md#x-ua-compatible


### Favicons and other root level statics

These are a pain in a compiled slug environment like heroku.
By default they are in the root of the static folder
and the base template links to them with <link rel="shortcut icon" .../>
tags. This isn't 'correct' for older html (it is now, yay html5!),
but it works for all the real browsers. Look deeply into this
issue if you care.

Some info about touch icons:
http://mathiasbynens.be/notes/touch-icons

### Modernizr

http://modernizr.com/
