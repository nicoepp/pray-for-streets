from flask import Flask
from whitenoise import WhiteNoise


app = Flask(__name__, static_folder='dist')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='dist/')


@app.route('/')
def hello():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()
