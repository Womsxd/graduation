from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel
from qfluentwidgets import MessageBox, LineEdit, EditableComboBox, ComboBox, SwitchButton
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from request import http
import setting


class MessageBoxForLoginOTP(MessageBox):  # 对原始的进行改造，增加登入界面需要输入2fa验证码的需求

    def __init__(self, title, content, parent):
        super(MessageBoxForLoginOTP, self).__init__(title, content, parent)
        self.code_line_edit = LineEdit(parent)
        validator = QRegExpValidator(QRegExp("[0-9]{6}"), self.code_line_edit)
        self.code_line_edit.setValidator(validator)
        self.textLayout.addWidget(self.code_line_edit)

    def get_input(self):
        return self.code_line_edit.text()


class MessageBoxForAdd(MessageBox):
    def __init__(self, title, content, parent):
        super(MessageBoxForAdd, self).__init__(title, content, parent)

        self.label = QLabel("名称:", parent)
        self.textLayout.addWidget(self.label)

        self.line_edit_name = LineEdit(parent)
        self.textLayout.addWidget(self.line_edit_name)

    def get_input(self):
        return self.line_edit_name.text()


def get_all_data(api, data_id: str):
    temp = []
    i = 1
    while True:
        resp = http.get(api, params={"page": i})
        if resp.status_code != 200:
            break
        data = resp.json()
        if data["code"] == 10001:
            break
        elif data["code"] == 10103:
            break
        temp.extend(data["data"][data_id])
        if data["data"]["maximum"] == 1 or data["data"]["maximum"] == i:
            break
        i += 1
    return temp


class MessageBoxForClass(MessageBoxForAdd):
    def __init__(self, title, content, parent):
        super(MessageBoxForClass, self).__init__(title, content, parent)

        self.label = QLabel("年级:", parent)
        self.textLayout.addWidget(self.label)

        self.grade_combo_box = EditableComboBox(parent)
        self.textLayout.addWidget(self.grade_combo_box)

        self.label = QLabel("学院:", parent)
        self.textLayout.addWidget(self.label)

        self.college_combo_box = ComboBox(parent)
        self.textLayout.addWidget(self.college_combo_box)

    def load_server_data(self):
        self.grade_combo_box.addItems([str(i) for i in get_all_data(setting.CLASS_GRADES, "grades")])
        self.college_combo_box.addItems(
            [f"{i['id']}: {i['name']}" for i in get_all_data(setting.COLLEGE_LIST, "colleges")])


class MessageBoxForStudent(MessageBox):
    def __init__(self, title, content, parent):
        super(MessageBoxForStudent, self).__init__(title, content, parent)

        self.label = QLabel("学号:", parent)
        self.textLayout.addWidget(self.label)

        self.line_edit_sid = LineEdit(parent)
        self.textLayout.addWidget(self.line_edit_sid)

        self.label = QLabel("姓名:", parent)
        self.textLayout.addWidget(self.label)

        self.line_edit_name = LineEdit(parent)
        self.textLayout.addWidget(self.line_edit_name)

        self.label = QLabel("性别:", parent)
        self.textLayout.addWidget(self.label)

        self.sex_combo_box = ComboBox(parent)
        self.sex_combo_box.addItems(["男", "女"])
        self.textLayout.addWidget(self.sex_combo_box)

        self.label = QLabel("班级:", parent)
        self.textLayout.addWidget(self.label)

        self.class_combo_box = ComboBox(parent)
        self.textLayout.addWidget(self.class_combo_box)

    def load_server_data(self):
        self.class_combo_box.addItems(
            [f"{i['id']}: {i['name']}" for i in get_all_data(setting.CLASS_LIST, "classes")])


class MessageBoxForUser(MessageBoxForAdd):
    def __init__(self, title, content, parent):
        super(MessageBoxForUser, self).__init__(title, content, parent)
        self.parent = parent
        self.label.setText("用户名:")

        self.label2 = QLabel("密码:", parent)
        self.textLayout.addWidget(self.label2)

        self.line_edit_password = LineEdit(parent)
        self.line_edit_password.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.textLayout.addWidget(self.line_edit_password)

        self.label2 = QLabel("用户组:", parent)
        self.textLayout.addWidget(self.label2)

        self.groups_combo_box = ComboBox(parent)
        self.textLayout.addWidget(self.groups_combo_box)

        self.switch_otp = SwitchButton(parent)
        self.switch_otp.setOnText("已开启OTP")
        self.switch_otp.setOffText("已关闭OTP")

        self.switch_banned = SwitchButton(parent)
        self.switch_banned.setOnText("封禁中")
        self.switch_banned.setOffText("未封禁")

    def load_server_data(self):
        self.groups_combo_box.addItems(
            [f"{i['id']}: {i['name']}" for i in get_all_data(setting.GROUP_LIST, "groups")])

    def edit_add(self):
        self.label2 = QLabel("OTP状态:", self.parent)
        self.textLayout.addWidget(self.label2)

        self.textLayout.addWidget(self.switch_otp)

        self.label2 = QLabel("封禁状态:", self.parent)
        self.textLayout.addWidget(self.label2)

        self.textLayout.addWidget(self.switch_banned)


class MessageBoxForExamInfo(MessageBoxForAdd):
    def __init__(self, title, content, parent):
        super(MessageBoxForExamInfo, self).__init__(title, content, parent)
        self.parent = parent
        self.label.setText("学号")

        self.label2 = QLabel("考试:", parent)
        self.textLayout.addWidget(self.label2)

        self.session_combo_box = ComboBox(parent)
        self.textLayout.addWidget(self.session_combo_box)

        self.label2 = QLabel("科目:", parent)
        self.textLayout.addWidget(self.label2)

        self.subject_combo_box = ComboBox(parent)
        self.textLayout.addWidget(self.subject_combo_box)

        self.label2 = QLabel("分数:", parent)
        self.textLayout.addWidget(self.label2)

        self.line_edit_result = LineEdit(parent)
        self.textLayout.addWidget(self.line_edit_result)

    def load_server_data(self):
        self.session_combo_box.addItems(
            [f"{i['id']}: {i['name']}" for i in get_all_data(setting.SESSION_LIST, "sessions")])
        self.subject_combo_box.addItems(
            [f"{i['id']}: {i['name']}" for i in get_all_data(setting.SUBJECT_LIST, "subjects")])


class MessageBoxForChange_pwd(MessageBoxForAdd):
    def __init__(self, title, content, parent):
        super(MessageBoxForChange_pwd, self).__init__(title, content, parent)
        self.label.setText("原密码:")
        self.line_edit_name.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)

        self.label2 = QLabel("新密码:", parent)
        self.textLayout.addWidget(self.label2)

        self.line_edit_password_new = LineEdit(parent)
        self.line_edit_password_new.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.textLayout.addWidget(self.line_edit_password_new)

        self.label2 = QLabel("再次确认新密码:", parent)
        self.textLayout.addWidget(self.label2)

        self.line_edit_password_new2 = LineEdit(parent)
        self.line_edit_password_new2.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.textLayout.addWidget(self.line_edit_password_new2)


class MessageBoxForOTP(MessageBox):
    def __init__(self, title, content, parent):
        super(MessageBoxForOTP, self).__init__(title, content, parent)

        self.label = QLabel("OTP二维码:", parent)
        self.textLayout.addWidget(self.label)

        self.qrcode = QLabel(parent=parent)
        self.qrcode.setFixedSize(128, 128)
        self.qrcode.setMaximumSize(128, 128)
        self.qrcode.setMinimumSize(128, 128)
        self.qrcode.setScaledContents(True)
        self.textLayout.addWidget(self.qrcode)

        self.label = QLabel("OTP验证码:", parent)
        self.textLayout.addWidget(self.label)

        self.line_edit_name = LineEdit(parent)
        self.textLayout.addWidget(self.line_edit_name)

    def get_input(self):
        return self.line_edit_name.text()


class MessageForGroup(MessageBoxForAdd):
    def __init__(self, title, content, parent):
        super(MessageForGroup, self).__init__(title, content, parent)

        self.label = QLabel("权限(用 , 分割):", parent)
        self.textLayout.addWidget(self.label)

        self.line_edit_perms = LineEdit(parent)
        self.textLayout.addWidget(self.line_edit_perms)

        self.label = QLabel("继承的权限组(用 , 分割):", parent)
        self.textLayout.addWidget(self.label)

        self.line_edit_ins = LineEdit(parent)
        self.textLayout.addWidget(self.line_edit_ins)
