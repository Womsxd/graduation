# 正常就返回这个
OK = {'code': 0, 'message': ''}

# OTP 相关返回
NEED_OTP = {'code': 1001, 'message': 'otp verification is required'}
OTP_VERIFY_ERROR = {'code': 1002, 'message': 'The OTP check fails. Procedure'}
OTP_NEED_OPEN = {'code': 1003, 'message': 'Please enable otp'}
OTP_OPEN = {'code': 1003, 'message': 'The otp is enabled. Procedure'}
OTP_TIME_OUT = {'code': 1004, 'message': 'otp activation timed out'}

# 登入相关
NO_LOGIN = {'code': 10001, 'message': 'NoLogin'}
PASSWORD_ERROR = {'code': 10002, 'message': 'Password Error'}  # 这里只能给user里面修改密码使用
AUTH_ERROR = {'code': 10002, 'message': 'Account/Password Error'}
ACCOUNT_BANNED = {'code': 10003, 'message': "Account is Banned"}

# 通用
DATA_NONE = {'code': 10101, 'message': 'Data equal to None'}
NOT_FOUND = {'code': 10102, 'message': 'Data is not Found'}
DATABASE_ERROR = {'code': 10103, 'message': 'Database operation error'}
DOT_EXIST = {'code': 10104, 'message': 'data does not exist'}
NOT_DELETE = {'code': 10105, 'message': 'Disable modifying/deleting default entries'}

# 添加/修改时使用
DOT_CHANGE_OWN_PASSWORD = {'code': 10201, 'message': 'Do not change your own password'}
NO_ADMIN = {'code': 10202, 'message': 'There will be no administrator'}
DUPLICATE = {'code': 10203, 'message': 'Duplicate content'}
NOT_BAN_SELF = {'code': 10204, 'message': 'Do not banned your self'}
NOT_DISABLE_OTP = {'code': 10205, 'message': 'Do not disable otp on here'}

# XLS导入相关
NOT_XLS_FILE = {'code': 10301, 'message': 'This is not an xls/xlsx file'}
XLS_NAME_ERROR = {'code': 10302, 'message': 'The xls/xlsx file table name is incorrect'}
XLS_TITLE_ERROR = {'code': 10303, 'message': 'The xls/xlsx file table title name is incorrect'}
XLS_IMPORT_EMPTY = {'coed': 10304, 'message': 'The import content is empty'}
