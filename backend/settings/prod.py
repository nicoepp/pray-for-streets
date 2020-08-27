import django_heroku

from .dev import *


# Activate Django-Heroku.
django_heroku.settings(locals())

# Overwrite what django_heroku tried to overwrite
STATIC_ROOT = BASE_DIR / 'dist' / 'static'
