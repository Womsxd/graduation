import hashlib
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash


class SexEnum(Enum):
    #  定义 枚举类 快速的把数字映射到对应性别 同时可为阿美莉卡的超多种性别做快速扩充(((
    MALE = "男"
    FEMALE = "女"


def sha256(text):
    sha = hashlib.sha256()
    sha.update(text.encode("utf-8"))
    return sha.hexdigest()


def get_password(password):
    return generate_password_hash(password, "pbkdf2:sha512")


def validate_password(save_password, password):
    return check_password_hash(save_password, password)
