API_SERVER = "http://127.0.0.1:5050"
# 登入接口
LOGIN = f'{API_SERVER}/auth/login'
LOGOUT = f'{API_SERVER}/auth/logout'
# 下载模板
DOWNLOAD_TEMP = f'{API_SERVER}/download/template/xls/download'
# 考试
EXAM = f"{API_SERVER}/exam"
# 成绩管理
INFO_ADD = f'{EXAM}/info/add'
INFO_EDIT = f'{EXAM}/info/edit'
INFO_DELETE = f'{EXAM}/info/delete'
INFO_LIST = f'{EXAM}/info/list'
INFO_QUERY = f'{EXAM}/info/query'
INFO_IMP_XLS = f'{EXAM}/info/import_xls'
# 考试轮次管理
SESSION_ADD = f'{EXAM}/session/add'
SESSION_EDIT = f'{EXAM}/session/edit'
SESSION_DELETE = f'{EXAM}/session/delete'
SESSION_LIST = f'{EXAM}/session/list'
SESSION_QUERY = f'{EXAM}/session/query'
SESSION_IMP_XLS = f'{EXAM}/session/import_xls'
# 学校接口
SCHOOL = f'{API_SERVER}/school'
# 学院
COLLEGE_ADD = f'{SCHOOL}/college/add'
COLLEGE_EDIT = f'{SCHOOL}/college/edit'
COLLEGE_DELETE = f'{SCHOOL}/college/delete'
COLLEGE_LIST = f'{SCHOOL}/college/list'
COLLEGE_QUERY = f'{SCHOOL}/college/query'
COLLEGE_IMP_XLS = f'{SCHOOL}/college/import_xls'
# 班级
CLASS_ADD = f'{SCHOOL}/class/add'
CLASS_EDIT = f'{SCHOOL}/class/edit'
CLASS_DELETE = f'{SCHOOL}/class/delete'
CLASS_GRADES = f'{SCHOOL}/class/grades'
CLASS_LIST = f'{SCHOOL}/class/list'
CLASS_QUERY = f'{SCHOOL}/class/query'
CLASS_IMP_XLS = f'{SCHOOL}/class/import_xls'
# 权限管理接口
GROUP_GET_MY_PERMISSIONS = f'{API_SERVER}/group/get_my_permissions'
GROUP_ADD = f'{API_SERVER}/group/add'
GROUP_EDIT = f'{API_SERVER}/group/edit'
GROUP_DELETE = f'{API_SERVER}/group/delete'
GROUP_LIST = f'{API_SERVER}/group/list'
GROUP_QUERY = f'{API_SERVER}/group/query'
GROUP_IMP_XLS = f'{API_SERVER}/group/import_xls'
# 学生管理
STUDENT_ADD = f'{API_SERVER}/student/add'
STUDENT_EDIT = f'{API_SERVER}/student/edit'
STUDENT_DELETE = f'{API_SERVER}/student/delete'
STUDENT_LIST = f'{API_SERVER}/student/list'
STUDENT_QUERY = f'{API_SERVER}/student/query'
STUDENT_IMP_XLS = f'{API_SERVER}/student/import_xls'
# 科目管理
SUBJECT_ADD = f'{API_SERVER}/subject/add'
SUBJECT_EDIT = f'{API_SERVER}/subject/edit'
SUBJECT_DELETE = f'{API_SERVER}/subject/delete'
SUBJECT_LIST = f'{API_SERVER}/subject/list'
SUBJECT_QUERY = f'{API_SERVER}/subject/query'
SUBJECT_IMP_XLS = f'{API_SERVER}/subject/import_xls'
# 用户
USER_API = f'{API_SERVER}/user'
USER_CHANGE_PWD = f'{USER_API}/change_password'
USER_MY_INFO = f'{USER_API}/get_my_info'
USER_ADD = f'{USER_API}/add'
USER_EDIT = f'{USER_API}/edit'
USER_DELETE = f'{USER_API}/delete'
USER_LIST = f'{USER_API}/list'
USER_QUERY = f'{USER_API}/query'
USER_IMP_XLS = f'{USER_API}/import_xls'
USER_OTP_ENABLE = f'{USER_API}/otp/enable'
USER_OTP_VERIFY = f'{USER_API}/otp/verify'
USER_OTP_DISABLE = f'{USER_API}/otp/disable'
