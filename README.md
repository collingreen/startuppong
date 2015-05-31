StartupPong
-----------

![StartupPong](http://startuppong.com/static/img/techpong_ladder_frame.png)

StartupPong helps you manage your pingpong (or any other head-to-head game) ladder! Track your rank and rating over time and track your entire match history. Turn on winner-takes-all ranking or ELO ratings or both!

You can use startuppong.com for free or clone this repo and host it yourself.

### API

StartupPong implements a simple JSON API. Log in and check out [the API docs](http://www.startuppong.com/api/latest/docs/) for up to date, working examples.

Current API Endpoints:
- get_players
- get_recent_matches_for_company
- get_recent_matches_for_player
- get_recent_matches_between_players
- add_match
- add_player

### API Adapters
- jQuery - The [API docs](http://www.startuppong.com/api/latest/docs) include runnable jQuery code for every endpoint
- [Rust Adapter](https://github.com/jwilm/startuppong-client-rs) by (jwilm)[https://github.com/jwilm]

Have another adapter? File an issue or submit a pull request to add yours here!


### Local Setup

Run locally/on your own server or use fabric to automatically set up your own heroku instance. Check out the djeroku docs for more details. Roughly, you should create a virtualenv and install the requirements using the following commands:

```
cd path-to-startup-pong-directory
virtualenv venv
. venv/bin/activate
pip install -r reqs/dev.py
```

You should go through the settings files and adjust them according to your preferences and credentials.


### Run Locally
```
python manage.py syncdb
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```
