import os
import yaml
from database import db
from gevent import pywsgi
from auth import login_manager
from auth import auth as auth_blueprint
from exam import exam as exam_blueprint
from user import userf as user_blueprint
from flask import Flask, render_template
from school import school as school_blueprint
from group.api import groups as groups_blueprint
from student import student as student_blueprint
from subject import subject as subject_blueprint
from download import download as download_blueprint

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class FlaskConfig(object):
    DEBUG = True
    SECRET_KEY = config['cookie']['secret']
    REMEMBER_COOKIE_DURATION = 2592000000  # 设置Cookie最长有效期一个月
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000  # 限制最大上传大小为16M
    db = config["database"]
    if db["engine"] == "sqlite":
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'./{db["sqlite_file"]}')
        if os.name != "nt":
            db_path = f"/{db_path}"
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        SQLALCHEMY_DATABASE_URI = f'{db["type"]}://{db["username"]}:{db["password"]}@{db["host"]}/{db["dbname"]}'


app = Flask(__name__)
app.config.from_object(FlaskConfig)
db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(auth_blueprint)
app.register_blueprint(exam_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(groups_blueprint)
app.register_blueprint(school_blueprint)
app.register_blueprint(student_blueprint)
app.register_blueprint(subject_blueprint)
app.register_blueprint(download_blueprint)


@app.errorhandler(404)
def error_404(error):
    return render_template("404.html"), 404


if __name__ == '__main__':
    server = pywsgi.WSGIServer((config['base']['host'], int(config['base']['port'])), app)
    print(f"App Running on: http://{config['base']['host']}:{int(config['base']['port'])}")
    server.serve_forever()
