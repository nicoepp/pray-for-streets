import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


def init():
    dsn = os.environ.get('SENTRY_DSN', None)

    if not dsn:
        raise Exception("Please set SENTRY_DSN env var")

    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.05,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )
