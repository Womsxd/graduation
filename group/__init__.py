import functools
from flask import abort
from database import models
from flask_login import current_user


def check_permissions(group_id):
    def check(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            user = models.User.query.filter_by(csrf=current_user.get_id()).first()
            group = models.Group.query.filter_by(id=user.groupid).first()
            if gcheck(group, group_id):
                return func(*args, **kwargs)
            return abort(404)

        return inner

    return check


def gcheck(group: models.Group, need_id: int):
    if group is None:
        return False
    # print(group.id, group.inherit, need_id)
    if group.id == need_id:
        return True
    if group.inherit is None:
        return False
    if int(group.inherit) == need_id:
        return True
    return gcheck(models.Group.query.filter_by(id=int(group.inherit)).first(), need_id)
