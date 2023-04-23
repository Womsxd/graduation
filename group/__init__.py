import functools
from database import models
from flask import abort, session


def check_permissions(group_id):
    def check(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            gid = models.User.query.filter_by(id=session["_uid"]).first().groupid
            need_group = models.Group.query.filter_by(id=gid).first()
            if group_check(need_group, group_id):
                return func(*args, **kwargs)
            return abort(404)

        return inner

    return check


def group_check(group: models.Group, need_id: int) -> bool:
    while group is not None:
        if group.id == need_id or int(group.inherit) == need_id:
            return True
        group = models.Group.query.filter_by(id=int(group.inherit)).first()
    return False
