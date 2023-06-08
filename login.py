import sys
import json
import main
import setting
import threading
import my_globals
from request import http
from ui_login import Ui_Form
from PyQt5.QtWidgets import QApplication
from my_dialog import MessageBoxForLoginOTP
from qframelesswindow import FramelessDialog
from PyQt5.QtCore import Qt, QLocale, pyqtSignal
from qfluentwidgets import setThemeColor, MessageBox, StateToolTip, FluentTranslator


class LoginWindow(FramelessDialog, Ui_Form):
    request_finished = pyqtSignal(bool, dict)

    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUi(self)
        setThemeColor('#28afe9')

        self.titleBar.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.username_line.setClearButtonEnabled(True)

        self.login_button.clicked.connect(self.login_button_event)

        self.request_finished.connect(self.login_back)

    def login_button_event(self):
        if self.username_line.text() == "" or self.password_line.text() == "":
            MessageBox("Login", "账号/密码不能为空", self).exec_()
            return
        self.disable_button()
        self.tips = StateToolTip("请求数据中", "请稍后", self)
        self.tips.move(430, 430)
        self.tips.show()
        self.login_event(self.username_line.text(), self.password_line.text())
        #thread = threading.Thread(target=self.login_event, args=(self.username_line.text(), self.password_line.text()))
        #thread.start()

    def disable_button(self, a: bool = False):
        self.username_line.setEnabled(a)
        self.password_line.setEnabled(a)
        self.login_button.setEnabled(a)

    def login_event(self, username: str, password: str, otp: str = ""):
        data = {"username": username, "password": password}
        if otp != "" and len(otp) == 6:
            data["otp_code"] = otp
        try:
            resp = http.post(setting.LOGIN, data=data)
            response_data = resp.json()
        except json.decoder.JSONDecodeError:
            self.request_finished.emit(False, {})
        except Exception as e:
            print(f"Exception occurred: {e}")
            self.request_finished.emit(True, {})
        else:
            ret_code = response_data.get("code")
            if ret_code is None:
                self.request_finished.emit(False, {})
            elif ret_code == 1001 and not otp:
                w = MessageBoxForLoginOTP("Login", "请输入2FA动态密码", self)
                if w.exec_():
                    otp = w.get_input()
                    if len(otp) == 6:
                        return self.login_event(username, password, otp)
            self.request_finished.emit(False, response_data)

    def login_back(self, timeout: bool = False, resp_data: dict = None):  # 登入回调
        self.tips.setState(True)
        self.tips = None
        if timeout:
            MessageBox("Login", "无法访问服务器", self).exec_()
        else:
            if resp_data == {}:
                MessageBox("Login", "服务器请求失败\n请重试或联系管理员解决", self).exec_()
            else:
                ret_code = resp_data["code"]
                if ret_code == 0:
                    my_globals.user_name = self.username_line.text()
                    w = main.MainWindow()
                    w.show()
                    self.close()
                elif ret_code == 10002:
                    MessageBox("Login", "账号/密码错误", self).exec_()
                elif ret_code == 10003:
                    MessageBox("Login", "账号被封禁", self).exec_()
                elif ret_code == 1001:
                    MessageBox("Login", "请输入2FA验证码\n且不能为为空/小于6位", self).exec_()
                elif ret_code == 1002:
                    MessageBox("Login", "2FA验证码校验错误", self).exec_()
                else:
                    MessageBox("Login", f'其他错误{resp_data["message"]}', self).exec_()
        self.disable_button(True)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale().system())
    app.installTranslator(translator)

    demo = LoginWindow()
    demo.show()
    sys.exit(app.exec_())
