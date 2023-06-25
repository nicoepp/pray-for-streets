FROM node:16 as build

WORKDIR /app

COPY . ./

RUN yarn install
RUN --mount=type=secret,id=VUE_APP_RECAPTCHA_SITE_KEY \
    VUE_APP_RECAPTCHA_SITE_KEY="$(cat /run/secrets/VUE_APP_RECAPTCHA_SITE_KEY)" yarn build

RUN rm -rf node_modules

FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

WORKDIR /app
# COPY . ./

COPY --from=build /app ./

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN apt-get clean

RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE backend.settings.build
RUN python manage.py collectstatic --noinput

RUN python manage.py migrate

# Turn on swap to be able to have 2 gunicorn workers on a 256mb memory machine
# From: https://www.joseferben.com/posts/django-on-flyio/
RUN fallocate -l 512M /swapfile & chmod 0600 /swapfile & mkswap /swapfile & echo 10 > /proc/sys/vm/swappiness
RUN swapon /swapfile

CMD exec gunicorn backend.wsgi --bind 0.0.0.0:8000 --max-requests=120 --log-file=- --log-level=info

