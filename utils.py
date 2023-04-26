import xlrd
import base64
import qrcode
import hashlib
import openpyxl
from io import BytesIO
from database import db
from werkzeug.security import generate_password_hash, check_password_hash


class SexMap:  # 简单，方便，拓展性强的快速性别映射工具类 支持美利坚现状((
    gender_list = {1: "男", 2: "女"}

    @staticmethod
    def to_string(sex_id: int) -> str:
        return SexMap.gender_list.get(sex_id, "男")

    @staticmethod
    def to_number(sex: str) -> int:
        return next((k for k, v in SexMap.gender_list.items() if v == sex), 1)


def check_record_existence(model_class, id: int or None = None, sid: str or None = None):
    if sid is not None:
        query = db.session.query(model_class).filter_by(sid=id)
    else:
        query = db.session.query(model_class).filter_by(id=id)
    return db.session.query(query.exists()).scalar()  # 存在返回True，不存在返回False


def sha256(text):
    sha = hashlib.sha256()
    sha.update(text.encode("utf-8"))
    return sha.hexdigest()


def get_b64_qrcode(text: str) -> str:
    out = BytesIO()
    img = qrcode.make(data=text, error_correction=qrcode.constants.ERROR_CORRECT_L)
    img.save(out, 'PNG')
    return u"data:image/png;base64," + base64.b64encode(out.getvalue()).decode('ascii')


def load_xls_file(file: bytes, table_name: str):
    """
    一个比较通用的xls or xlsx 文件处理函数，不依赖文件拓展名，通过bytes类型的文件头来进行判断xls，再通过特定文件来判断是xlsx还是其他文件

    :param file: bytes形式的文件
    :param table_name: 表名称
    :return: 读取到的内容列表
    """
    if file.__class__ is not bytes:
        return None
    if file[:4] == b'\xd0\xcf\x11\xe0':  # xls文件头，之后可以通过try来防止上传文件文件
        try:
            xsl = xlrd.open_workbook(file_contents=file)
            sheet = xsl.sheet_by_name(table_name)
            return [sheet.row_values(rowx) for rowx in range(sheet.nrows)]
        except xlrd.biffh.XLRDError:  # 防止加载错误文件
            return None
        except ValueError:  # 处理表名错误
            return []
    elif file[:4] == b'\x50\x4b\x03\x04' and '[Content_Types].xml'.encode("utf-8") in file and \
            'xl/workbook.xml'.encode("utf-8") in file:
        try:
            xls = openpyxl.load_workbook(filename=BytesIO(file), read_only=True, data_only=True)
            sheet = xls[table_name]
            return [list(row) for row in sheet.values]
        except openpyxl.utils.exceptions.InvalidFileException:
            return None
        except KeyError:  # 处理表名错误
            return []
    else:
        return None


def get_password(password):
    return generate_password_hash(password, "pbkdf2:sha512")


def validate_password(save_password, password):
    return check_password_hash(save_password, password)
