import django_heroku
from .gcloud_credentials import google_credentials_from_env

from .dev import *


# Activate Django-Heroku.
django_heroku.settings(locals())

DEBUG = False

# Overwrite what django_heroku tried to overwrite
STATIC_ROOT = BASE_DIR / 'dist' / 'static'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'prayer-walk-heroku'
GS_CREDENTIALS = google_credentials_from_env('GOOGLE_CREDENTIALS')
