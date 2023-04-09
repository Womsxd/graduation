import os
import yaml
from flask import Flask
from database import db
from auth import auth as auth_blueprint
from auth import login_manager

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class FlaskConfig(object):
    DEBUG = True
    SECRET_KEY = config['cookie']['secret']
    REMEMBER_COOKIE_DURATION = 2592000000
    db = config["database"]
    if db["type"] == "sqlite":
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'./{db["sqlite_file"]}')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        SQLALCHEMY_DATABASE_URI = f'{db["type"]}://{db["username"]}:{db["password"]}@{db["host"]}/{db["dbname"]}'


app = Flask(__name__)
app.config.from_object(FlaskConfig)
login_manager.init_app(app)
app.register_blueprint(auth_blueprint)
db.init_app(app)





if __name__ == '__main__':
    from gevent import pywsgi
    server = pywsgi.WSGIServer((config['base']['host'], int(config['base']['port'])), app)
    print(f"App Running on: http:{config['base']['host']}:{int(config['base']['port'])}")
    server.serve_forever()
