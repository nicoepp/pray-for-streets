# Pray for Streets

Front- and Backend for Abbotsford Neighbourhood Prayer Walk

## Backend
Assuming you have the latest Python and Pip installed run the following 
to install all dependencies.
```shell
pip install -r requirements.txt
```
One of these dependencies is Gunicorn (an application server) it should be
available in your shell after the install. 

To run the backend server:
```shell
gunicorn backend.wsgi
```

## Frontend
Assuming you use Yarn run the following to install all dependencies.
```shell
yarn install
```
To run the frontend development server (which is also configured to connect to the backend) run:
```shell
yarn serve
```

