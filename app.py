import yaml
import functools
from flask import Flask, request, session

app = Flask(__name__)
with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class FlaskConfig(object):
    DEBUG = False
    SECRET_KEY = config['cookie']['secret']
    db = config["database"]
    if db["type"] == "sqlite":
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db["sqlite_file"]}'
    else:
        SQLALCHEMY_DATABASE_URI = f'{db["type"]}://{db["username"]}:{db["password"]}@{db["host"]}/{db["dbname"]}'


app.config.from_object(FlaskConfig)


def auth(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if session.get('account'):
            ret = func(*args, **kwargs)
            return ret
        return "No Login"

    return inner


@app.route('/auth/login', methods=['post'])
def login():
    account = request.form.get('account')
    password = request.form.get('password')
    if account != "" and password == account[-4:]:
        session['account'] = account
        return "pass"
    return 'Error'


@app.route('/')
@auth
def index():
    return "Index"


if __name__ == '__main__':
    from gevent import pywsgi

    server = pywsgi.WSGIServer((config['base']['host'], int(config['base']['port'])), app)
    server.serve_forever()
