import os
import django_heroku
from .gcloud_credentials import get_google_credentials

from .dev import *


# Activate Django-Heroku.
django_heroku.settings(locals())

DEBUG = False

# Overwrite what django_heroku tried to overwrite
STATIC_ROOT = BASE_DIR / 'dist' / 'static'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.environ.get('GOOGLE_STORAGE_BUCKET')
GS_CREDENTIALS = get_google_credentials(os.environ.get('GOOGLE_CREDENTIALS'))
