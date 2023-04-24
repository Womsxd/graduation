import base64
import qrcode
import hashlib
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash


class SexMap:  # 简单，方便，拓展性强的快速性别映射工具类 支持美利坚现状((
    gender_list = {1: "男", 2: "女"}

    @staticmethod
    def to_string(sex_id: int) -> str:
        return SexMap.gender_list.get(sex_id, "男")

    @staticmethod
    def to_number(sex: str) -> int:
        return next((k for k, v in SexMap.gender_list.items() if v == sex), 1)


def sha256(text):
    sha = hashlib.sha256()
    sha.update(text.encode("utf-8"))
    return sha.hexdigest()


def get_b64_qrcode(text: str) -> str:
    out = BytesIO()
    img = qrcode.make(data=text, error_correction=qrcode.constants.ERROR_CORRECT_L)
    img.save(out, 'PNG')
    return u"data:image/png;base64," + base64.b64encode(out.getvalue()).decode('ascii')


def get_password(password):
    return generate_password_hash(password, "pbkdf2:sha512")


def validate_password(save_password, password):
    return check_password_hash(save_password, password)
