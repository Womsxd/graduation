import os
import yaml
from database import db
from flask import Flask
from auth import login_manager
from auth import auth as auth_blueprint
from user import userf as user_blueprint
from school import school as school_blueprint


from group import check_permissions
from flask_login import login_required

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class FlaskConfig(object):
    DEBUG = True
    SECRET_KEY = config['cookie']['secret']
    REMEMBER_COOKIE_DURATION = 2592000000  # 设置Cookie最长有效期一个月
    db = config["database"]
    if db["type"] == "sqlite":
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'./{db["sqlite_file"]}')
        if os.name != "nt":
            db_path = f"/{db_path}"
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        SQLALCHEMY_DATABASE_URI = f'{db["type"]}://{db["username"]}:{db["password"]}@{db["host"]}/{db["dbname"]}'


app = Flask(__name__)
app.config.from_object(FlaskConfig)
login_manager.init_app(app)
app.register_blueprint(auth_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(school_blueprint)
db.init_app(app)


@app.route("/ping")
@login_required
@check_permissions(1)
def ping():
    return "Pong"


if __name__ == '__main__':
    from gevent import pywsgi

    server = pywsgi.WSGIServer((config['base']['host'], int(config['base']['port'])), app)
    print(f"App Running on: http:{config['base']['host']}:{int(config['base']['port'])}")
    server.serve_forever()
