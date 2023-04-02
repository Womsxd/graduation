import yaml
import functools
from flask import Flask, request, session

app = Flask(__name__)
with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
app.secret_key = config['cookie']['secret']


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
    app = Flask(__name__)
    app.run(host=config['host'], port=config['port'], debug=False)
