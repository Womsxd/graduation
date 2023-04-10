import auth.utils
from database import models, db
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user


userf = Blueprint('userf', __name__)


@userf.route('/user/changepwd', methods=['post'])
@login_required
def changepwd():
    old_pwd = request.form.get("old_pwd")
    new_pwd = request.form.get("new_pwd")
    user = models.User.query.filter_by(csrf=current_user.get_id()).first()
    if not auth.utils.vailidate_password(user.password, old_pwd):
        return jsonify({'code': 1, "message": "Password Error"})
    user.password = auth.utils.get_password(new_pwd)
    user.csrf = None
    db.session.commit()
    return jsonify({'code': 0, "message": ""})
