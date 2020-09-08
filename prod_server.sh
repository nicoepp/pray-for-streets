yarn build
python3 manage.py collectstatic --noinput
gunicorn backend.wsgi
