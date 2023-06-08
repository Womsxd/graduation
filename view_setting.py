import base64
import json
from PyQt5.QtGui import QPixmap
import my_dialog
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import MessageBox
import setting
from ui_setting import Ui_ViewSetting
from request import http


class ViewSetting(QWidget, Ui_ViewSetting):
    otp_status = False

    def __init__(self):
        super(ViewSetting, self).__init__()
        self.setupUi(self)
        self.get_otp_status()
        self.button_edit_pwd.clicked.connect(self.change_password)
        self.switch_button_otpset.clicked.connect(self.otp_switch)

    def get_otp_status(self):
        resp = http.get(setting.USER_MY_INFO)
        data = resp.json()
        self.otp_status = bool(int(data["data"]["otp_status"]))
        self.switch_button_otpset.setChecked(bool(int(data["data"]["otp_status"])))

    def change_password(self):
        w = my_dialog.MessageBoxForChange_pwd("成绩管理系统", "请输入原密码与新密码", self)
        if w.exec():
            if w.line_edit_name.text() == "" or w.line_edit_password_new.text() == "" \
                    or w.line_edit_password_new2.text() == "":
                MessageBox("成绩管理系统", "原密码与新密码不能为空", self).exec()
            elif w.line_edit_password_new.text() == w.line_edit_password_new2.text():
                MessageBox("成绩管理系统", "新密码与确认不一致", self).exec()
            elif w.line_edit_name.text() == w.line_edit_password_new.text():
                MessageBox("成绩管理系统", "你输入的原密码与新密码相同", self).exec()
            else:
                resp = http.post(setting.USER_CHANGE_PWD,
                                 data={"old_pwd": w.line_edit_name.text(), "new_pwd": w.line_edit_password_new.text()})
                if resp.status_code != 200:
                    MessageBox("成绩管理系统", "接口请求错误", self).exec_()
                    return
                try:
                    data = resp.json()
                except json.decoder.JSONDecodeError:
                    MessageBox("成绩管理系统", "接口返回数据有误", self).exec_()
                    return
                if data["code"] == 10001:
                    MessageBox("成绩管理系统", "未登入，请重启软件", self).exec_()
                elif data["code"] == 10103:
                    MessageBox("成绩管理系统", "错误，请重试", self).exec_()
                else:
                    MessageBox("成绩管理系统", "密码修改成功！", self).exec_()

    def otp_switch(self):
        self.switch_button_otpset.setChecked(self.otp_status)
        if self.switch_button_otpset.isChecked():
            w = my_dialog.MessageBoxForAdd("关闭OTP", "请输入OTP动态密码来进行关闭\n如果丢失请联系管理员强制关闭", self)
            if w.exec():
                resp = http.post(setting.USER_OTP_DISABLE, data={"otp_code": w.get_input()})
                if resp.status_code != 200:
                    MessageBox("成绩管理系统", "接口请求错误", self).exec_()
                    return
                try:
                    data = resp.json()
                except json.decoder.JSONDecodeError:
                    MessageBox("成绩管理系统", "接口返回数据有误", self).exec_()
                    return
                if data["code"] == 10001:
                    MessageBox("成绩管理系统", "未登入，请重启软件", self).exec_()
                elif data["code"] == 10103:
                    MessageBox("成绩管理系统", "错误，请重试", self).exec_()
                elif data["code"] == 1002:
                    MessageBox("成绩管理系统", "OTP校验失败，请重新输入", self).exec_()
                elif data["code"] == 1003:
                    MessageBox("成绩管理系统", "你并没有开启OTP :(", self).exec_()
                else:
                    MessageBox("成绩管理系统", "OTP关闭成功！", self).exec_()
                    self.otp_status = False
                    self.switch_button_otpset.setChecked(False)
        else:
            otp_open = http.get(setting.USER_OTP_ENABLE).json()
            if otp_open["code"] == 1004:
                MessageBox("成绩管理系统", "你已开启OTP，请不要重复操作！", self).exec_()
                return
            w = my_dialog.MessageBoxForOTP("开启OTP", "请使用相关APP扫码，添加后输入app显示的6位数字", self)
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(otp_open["data"]["otp"]["qrcode"].split(",", 1)[1]))
            w.qrcode.setPixmap(pixmap)
            if w.exec():
                if w.get_input() != "":
                    code = w.get_input()
                    resp = http.post(setting.USER_OTP_VERIFY, data={"otp_code": code})
                    if resp.status_code != 200:
                        MessageBox("成绩管理系统", "接口请求错误", self).exec_()
                        return
                    try:
                        data = resp.json()
                    except json.decoder.JSONDecodeError:
                        MessageBox("成绩管理系统", "接口返回数据有误", self).exec_()
                        return
                    if data["code"] == 10001:
                        MessageBox("成绩管理系统", "未登入，请重启软件", self).exec_()
                    elif data["code"] == 10103:
                        MessageBox("成绩管理系统", "错误，请重试", self).exec_()
                    elif data["code"] == 1002:
                        MessageBox("成绩管理系统", "OTP校验失败，请重新输入", self).exec_()
                    elif data["code"] == 1003:
                        MessageBox("成绩管理系统", "你并没有开启OTP :(", self).exec_()
                    elif data["code"] == 1004:
                        MessageBox("成绩管理系统", "你已开启OTP，请不要重复操作！", self).exec_()
                    elif data["code"] == 1004:
                        MessageBox("成绩管理系统", "OTP开启超时，请重新开启", self).exec_()
                    else:
                        MessageBox("成绩管理系统", "OTP开启成功！", self).exec_()
                        self.switch_button_otpset.setChecked(True)
                        self.otp_status = True
