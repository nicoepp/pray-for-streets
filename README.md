# The Prayer Walk

Front- and Backend for Abbotsford Neighbourhood Prayer Walk

## 1. Frontend
Assuming you use Yarn run the following to install all dependencies.
```shell
yarn install
```
To build the frontend run this:
```shell
yarn build
```

## 2. Backend
Assuming you have the latest Python and Pip installed run the following 
to install all dependencies.
```shell
pip install -r requirements.txt
```

Next run the migrate command to create your local database
```shell
python3 manage.py migrate
```

To be able to login to the CMS hosted at `/cms` and edit content on the site you need to create the first user
```shell
python3 manage.py createsuperuser
```

To have some street data preseeded from OSM into the database there is a Django command for that
```shell
python3 manage.py seed_streets_osm
```

_One of the dependencies installed with `pip` is Gunicorn (an application server which is widely used
in production), it should be available in your shell after the installation._

To run the backend server run:
```shell
gunicorn backend.wsgi
```
Now if you open http://localhost:8000 in the browser you should be able 
to navigate the hole website and also use the Sign Up Vue.js 
web application. Enjoy!


## Development
For doing development on the backend a slightly different setup might be more
convenient. Instead of gunicorn run `python3 manage.py runserver`. This runs
the Django development server which reloads automatically if 
some Python or HTML code has changed in the backend. Also, errors will be
shown with more helpful information. The downside to using the backend 
development server is that the Vue.js web application on the Sign Up and
Map page won't show up.

For doing development on the frontend you can run the backend first and then
run `yarn serve` and access the Vue.js web application part by opening
http://localhost:8080. This way your application gets recompiled and reloaded
in the browser whenever you make changes to your frontend code.

## Deploy to Heroku (Production)
For production this repo is configured to host the backend and frontend 
on Heroku. [Multiple builtpacks](https://devcenter.heroku.com/articles/using-multiple-buildpacks-for-an-app) 
have to be activated for the corresponding Heroku app. The Heroku CLI should 
list them in the following order:
```shell
$ heroku buildpacks
=== pray-for-streets Buildpack URLs
1. heroku/nodejs
2. heroku/python
```
