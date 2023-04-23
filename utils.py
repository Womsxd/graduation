import hashlib
from werkzeug.security import generate_password_hash, check_password_hash


def sha256(text):
    sha = hashlib.sha256()
    sha.update(text.encode("utf-8"))
    return sha.hexdigest()


def get_password(password):
    return generate_password_hash(password, "pbkdf2:sha512")


def validate_password(save_password, password):
    return check_password_hash(save_password, password)
