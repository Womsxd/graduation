import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator, NavigationItemPosition
import view_examinfo
import view_groups
import view_session
import setting
import view_class
import view_setting
import view_student
import view_subject
import view_user
from ui_main import Ui_MainWindow
from qframelesswindow import FramelessWindow, StandardTitleBar
import view_main
import view_college
from qfluentwidgets import FluentIcon
from request import http
import my_globals


class MainWindow(FramelessWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        setThemeColor('#28afe9')

        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()

        self.setWindowIcon(QIcon('resource/image/software_icon.png'))
        self.setWindowTitle('成绩管理系统')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.init_server_data()

        self.init_load_view()
        self.init_navigation()

        self.stackedWidget.currentChanged.connect(self.update_navigation)
        self.NavigationInterface.setCurrentItem(self.view_main.objectName())

    def add_navigation_label(self, interface, object_name, icon, text: str, position=NavigationItemPosition.TOP):
        interface.setObjectName(object_name)
        self.stackedWidget.addWidget(interface)
        self.NavigationInterface.addItem(interface.objectName(), icon, text,
                                         lambda: self.navigation_label_switch(interface), position=position,
                                         tooltip=text)

    def update_navigation(self, index):
        now_widget = self.stackedWidget.widget(index)
        self.NavigationInterface.setCurrentItem(now_widget.objectName())

    def navigation_label_switch(self, widget):
        self.stackedWidget.setCurrentWidget(widget)

    def init_load_view(self):
        self.view_main = view_main.ViewMain()
        self.view_college = view_college.ViewCollege()
        self.view_class = view_class.ViewClass()
        self.view_session = view_session.ViewSession()
        self.view_subject = view_subject.ViewSubject()
        self.view_student = view_student.ViewStudent()
        self.view_groups = view_groups.ViewGroups()
        self.view_user = view_user.ViewUser()
        self.view_examinfo = view_examinfo.ViewExamInfo()
        self.view_setting = view_setting.ViewSetting()

    def init_navigation(self):
        def check_if_load(permission):
            if any(i.startswith(permission) for i in my_globals.user_permission):
                return True
            return False

        def check_only(permission, pass_permission):
            present = False
            for item in my_globals.user_permission:
                if item == f"{permission}{pass_permission}":
                    present = True
                elif not item.startswith(permission):
                    return False
            return present

        pass_check = False
        if "*" in my_globals.user_permission:
            pass_check = True
        self.add_navigation_label(self.view_main, 'ViewMain', FluentIcon.HOME, "主页")
        if pass_check or check_if_load("school.college.") and not check_only("school.college.", "list"):
            self.add_navigation_label(self.view_college, "ViewCollege",
                                      QIcon(QtGui.QPixmap(":/resource/image/college.svg")), "学院")
        if pass_check or check_if_load("school.class.") and not check_only("school.class.", "list"):
            self.add_navigation_label(self.view_class, "ViewClass", QIcon(QtGui.QPixmap(":/resource/image/class.svg")),
                                      "班级")
        if pass_check or check_if_load("exam.session."):  # and not check_only("session", "list") 感觉考试不需要
            self.add_navigation_label(self.view_session, "ViewSession",
                                      QIcon(QtGui.QPixmap(":/resource/image/session.svg")), "考试")
        if pass_check or check_if_load("subject.") and not check_only("subject.", "list"):
            self.add_navigation_label(self.view_subject, "ViewSubject",
                                      QIcon(QtGui.QPixmap(":/resource/image/subject.svg")), "科目")
        if pass_check or check_if_load("exam.info."):
            self.add_navigation_label(self.view_examinfo, "ViewExamInfo",
                                      QIcon(QtGui.QPixmap(":/resource/image/examinfo.svg")), "成绩")
        if pass_check or check_if_load("student.") and not check_only("student.", "list"):
            self.add_navigation_label(self.view_student, "ViewStudent",
                                      QIcon(QtGui.QPixmap(":/resource/image/student.svg")), "学生")
        if pass_check or check_if_load("groups.") and not check_only("groups.", "list"):
            self.add_navigation_label(self.view_groups, "ViewGroups",
                                      QIcon(QtGui.QPixmap(":/resource/image/groups.svg")), "权限组")
        if pass_check or check_if_load("user."):  # and not check_only("user.", "list")
            self.add_navigation_label(self.view_user, "ViewUser",
                                      QIcon(QtGui.QPixmap(":/resource/image/user.svg")), "用户")
        self.add_navigation_label(self.view_setting, "ViewSetting", FluentIcon.SETTING, '设置',
                                  NavigationItemPosition.BOTTOM)

    def init_server_data(self):
        def get_data(api_url):
            resp = http.get(api_url)
            if resp.status_code != 200:
                return {}
            data = resp.json()
            return data.get("data", {})
        my_globals.user_permission = get_data(setting.GROUP_GET_MY_PERMISSIONS).get("permissions", [])


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale().system())
    app.installTranslator(translator)

    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())
