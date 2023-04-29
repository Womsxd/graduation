import functools
from database import models
from flask import abort, session
from flask_login import current_user


def check_permissions(permissions_node: str):
    def check(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            user = models.User.query.filter_by(id=session["_uid"]).first()
            if user is not None and current_user.get_id() == user.csrf:
                user_group = models.Group.query.filter_by(id=user.group_id).first()
                if permission_check(permissions_node, user_group):
                    return func(*args, **kwargs)
            return abort(404)

        return inner

    return check


def permission_check(need_permission: str, have_permission: models.Group) -> bool:
    if have_permission is None:
        return False
    if have_permission.permissions is not None and have_permission.permissions != "":
        permission = have_permission.permissions.split(",")
        if "*" in permission:  # 当用户有*权限的时候直接允许
            return True
        nodes = need_permission.split(".")
        prefix = ""
        for index, node in enumerate(nodes):
            if len(nodes) == 1 and node in have_permission:
                return True
            if not prefix:
                if f'{node}.*' in permission:
                    return True
                prefix = f'{node}'
            elif index == len(nodes) - 1:
                if f'{prefix}.{node}' in permission:
                    return True
            else:
                prefix = f'{prefix}.{node}'
                if f'{prefix}.*' in permission:
                    return True
    if have_permission.inherit is not None and have_permission.inherit != "":
        inherit = have_permission.inherit.split(",")
        for i in inherit:
            have = models.Group.query.filter_by(id=i).firsr()
            if have is None:
                continue
            if permission_check(need_permission, have):
                return True
    return False
