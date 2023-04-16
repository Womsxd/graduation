from werkzeug.security import generate_password_hash, check_password_hash


def get_password(password):
    return generate_password_hash(password, "pbkdf2:sha512")


def vailidate_password(save_password, password):
    return check_password_hash(save_password, password)
