import functools
from flask import abort
from database import models
from flask_login import current_user


def check_permissions(group_id):
    def check(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            gid = models.User.query.filter_by(csrf=current_user.get_id()).first().groupid
            need_group = models.Group.query.filter_by(id=gid).first()
            if gcheck(need_group, group_id):
                return func(*args, **kwargs)
            return abort(404)

        return inner

    return check


def gcheck(group: models.Group, need_id: int) -> bool:
    while group is not None:
        if group.id == need_id or int(group.inherit) == need_id:
            return True
        group = models.Group.query.filter_by(id=int(group.inherit)).first()
    return False

