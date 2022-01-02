import os
import django_heroku
from .gcloud_credentials import get_google_credentials
from .sentry import init as sentry_init

from .dev import *

sentry_init()

# Activate Django-Heroku.
django_heroku.settings(locals())

DEBUG = False

# Overwrite what django_heroku tried to overwrite
STATIC_ROOT = BASE_DIR / 'dist' / 'static'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.environ.get('GOOGLE_STORAGE_BUCKET')
GS_CREDENTIALS = get_google_credentials(os.environ.get('GOOGLE_CREDENTIALS'))

sk = os.environ.get('SECRET_KEY', None)

if not sk:
    raise Exception('Please provide a SECRET_KEY env var! You can use Django\'s '
                    'get_random_secret_key() function to generate one.')
SECRET_KEY = sk
