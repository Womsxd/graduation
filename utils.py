import hashlib


def sha256(text):
    sha = hashlib.sha256()
    sha.update(text.encode("utf-8"))
    return sha.hexdigest()
