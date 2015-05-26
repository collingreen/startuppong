serve:
	python manage.py runserver 0.0.0.0:3000

test:
	python -Wall manage.py test techpong

testfast:
	python -Wall manage.py test techpong --failfast

static:
	python manage.py collectstatic --noinput

