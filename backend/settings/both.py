from .dev import *

# Run Django's development server* and see JS apps** at the same time
#
# The only downside from the development perspective is that the server won't pick up changes made in CSS files,
# but the server will still reload Python changes automatically.
# For CSS changes you need to run collecstatic again
#
# To use this run:
# yarn build
# python manage.py collectstatic
# export DJANGO_SETTINGS_MODULE=backend.settings.both
# python mange.py runserver
#
# * manage.py runserver
# ** JS apps compiled by yarn

INSTALLED_APPS = [app for app in INSTALLED_APPS if not app == 'django.contrib.staticfiles']

SERVE_YARN_FILES = True
