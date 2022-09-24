from .django_heroku import settings as dj_heroku_settings
from .dev import *

# Activate Django-Heroku.
dj_heroku_settings(locals())

DEBUG = False

# Overwrite what django_heroku tried to overwrite
STATIC_ROOT = BASE_DIR / 'dist' / 'static'

