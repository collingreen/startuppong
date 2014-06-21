serve:
	python manage.py runserver 0.0.0.0:3000

test:
	python manage.py test techpong

static:
	python manage.py collectstatic --noinput

