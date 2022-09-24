FROM node:16 as build

WORKDIR /app

COPY . ./

RUN yarn install
RUN yarn build

RUN rm -rf node_modules

FROM python:3.10

ENV PYTHONUNBUFFERED True

WORKDIR /app
# COPY . ./

COPY --from=build /app ./

RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE backend.settings.build
RUN python manage.py collectstatic --noinput

# RUN python manage.py migrate


CMD exec gunicorn backend.wsgi --bind 0.0.0.0:8000 --max-requests=120 --log-file=- --log-level=info

