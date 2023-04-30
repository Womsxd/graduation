import functools
from database import models
from flask import abort, session
from flask_login import current_user


def check_permissions(permission: str):
    def check(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if session.get("_uid") is None:  # 判断_uid是否存在
                return abort(404)
            user = models.User.query.filter_by(id=session["_uid"]).first()  # 获取用户对象
            if user is not None and current_user.get_id() == user.csrf:
                user_group = models.Group.query.filter_by(id=user.group_id).first()
                if permission_check(permission, user_group):
                    return func(*args, **kwargs)
            return abort(404)
        return inner

    return check


def permission_check(need_permission: str, user_permission: models.Group) -> bool:
    if user_permission is None:
        return False
    if user_permission.permissions:
        permission_split = user_permission.permissions.split(",")
        if "*" in permission_split:  # 当用户有*权限的时候直接允许
            return True
        if need_permission in permission_split:  # 直接判断是否在权限组里面，是的话直接返回true
            return True
        nodes = need_permission.split(".")  # 根据.做切割
        node_prefix = ""
        for index, node in enumerate(nodes[:-1]):
            if not node_prefix:
                if f'{node}.*' in permission_split:
                    return True
                node_prefix = node
            else:
                node_prefix = f'{node_prefix}.{node}'
                if f'{node_prefix}.*' in permission_split:
                    return True
    if user_permission.inherit:
        for i in user_permission.inherit.split(","):
            next_group = models.Group.query.filter_by(id=i).firsr()
            if permission_check(need_permission, next_group):
                return True
    return False
