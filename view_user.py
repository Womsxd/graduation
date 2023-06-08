import json
from PyQt5 import QtWidgets
import my_dialog
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from qfluentwidgets import MessageBox, DWMMenu
import setting
import utils
from ui_other import Ui_Form
from request import http


class ViewUser(QWidget, Ui_Form):
    now_pages = 1

    def __init__(self):
        super(ViewUser, self).__init__()
        self.setObjectName("ViewUser")
        self.setupUi(self)
        self.label_title.setText("用户管理")
        self.TableWidget.setColumnCount(3)
        self.TableWidget.setWordWrap(False)
        self.TableWidget.verticalHeader().hide()
        self.TableWidget.setHorizontalHeaderLabels(['编号', '用户名', '用户组'])
        self.TableWidget.setStyleSheet("QTableWidget { border: none; }")
        self.pushbutton_query.clicked.connect(self.get_server_data)
        self.TableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TableWidget.customContextMenuRequested.connect(self.show_context_menu)
        if not utils.check_permission("user.add"):
            self.pushbutton_add.setEnabled(False)
        else:
            self.pushbutton_add.clicked.connect(self.add)
        self.TableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def get_server_data(self):
        keyword = self.line_edit_keyword.text()
        params = {"page": self.now_pages, "search": keyword}
        resp = http.get(setting.USER_LIST, params=params)
        if resp.status_code != 200:
            MessageBox("成绩管理系统", "接口请求错误", self).exec_()
            return
        try:
            data = resp.json()
        except json.decoder.JSONDecodeError:
            MessageBox("成绩管理系统", "接口返回数据有误", self).exec_()
            return
        self.flush_table(data["data"]["users"])
        if data["data"]["maximum"] == 1:
            self.pushbutton_previous_page.setEnabled(False)
            self.pushbutton_next_page.setEnabled(False)
        else:
            self.pushbutton_previous_page.setEnabled(True)
            self.pushbutton_next_page.setEnabled(True)
            if data["data"]["current"] == data["data"]["maximum"]:
                self.pushbutton_next_page.setEnabled(False)
            elif data["data"]["current"] == 1:
                self.pushbutton_previous_page.setEnabled(False)
            self.now_pages = data["data"]["current"]
            split_pages = self.label_pages.text().split("/")
            self.label_pages.setText(f"{self.now_pages}/{split_pages[1]}")

    def add(self):
        w = my_dialog.MessageBoxForUser("用户管理", "请输入班级名称", self)
        w.load_server_data()
        if w.exec():
            if w.line_edit_name.text() == "":
                MessageBox("用户管理", "输入不可为空", self).exec()
            else:
                resp = http.post(setting.USER_ADD,
                                 data={"username": w.line_edit_name.text(), "password": w.line_edit_password.text(),
                                       "group_id": w.groups_combo_box.text().split(": ")[0]})
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
                    MessageBox("成绩管理系统", "添加错误，请重试", self).exec_()
                else:
                    MessageBox("成绩管理系统", "添加成功", self).exec_()
                    self.get_server_data()

    def show_context_menu(self, pos):
        menu = DWMMenu(parent=self.TableWidget)
        if utils.check_permission("user.edit"):
            menu.addAction("编辑")
        if utils.check_permission("user.delete"):
            menu.addAction("删除")

        action = menu.exec_(self.TableWidget.mapToGlobal(pos))

        if action:
            if action.text() == "编辑":
                selected_items = self.TableWidget.selectedItems()
                if selected_items:
                    current_row = selected_items[0].row()
                    w = my_dialog.MessageBoxForUser("用户管理", "请进行修改", self)
                    w.edit_add()
                    w.load_server_data()
                    server_user_info = http.get(setting.USER_QUERY,
                                                params={"id": int(self.TableWidget.item(current_row, 0).text())}).json()
                    w.line_edit_name.setEnabled(False)
                    w.line_edit_name.setText(self.TableWidget.item(current_row, 1).text())
                    w.groups_combo_box.setText(self.TableWidget.item(current_row, 2).text())
                    if int(server_user_info["data"]["otp_status"]):
                        w.switch_otp.setChecked(True)
                    else:
                        w.switch_otp.setEnabled(False)
                    w.switch_banned.setChecked(bool(int(server_user_info["data"]["banned"])))
                    if w.exec():
                        post_data = {"id": int(self.TableWidget.item(current_row, 0).text()),
                                     "name": w.line_edit_name.text(),
                                     "group_id": w.groups_combo_box.text().split(": ")[0]}
                        if int(server_user_info["data"]["otp_status"]):
                            if not w.switch_otp.isChecked():
                                post_data["disable_otp"] = "true"
                        if bool(int(server_user_info["data"]["banned"])) != w.switch_banned.isChecked():
                            post_data["set_banned"] = str(w.switch_banned.isChecked()).lower()
                        resp = http.post(setting.USER_EDIT, data=post_data)
                        if resp.status_code != 200:
                            MessageBox("成绩管理系统", "接口请求错误", self).exec_()
                            return
                        data = resp.json()
                        if data["code"] == 10001:
                            MessageBox("成绩管理系统", "未登入，请重启软件", self).exec_()
                        elif data["code"] == 10103:
                            MessageBox("成绩管理系统", "修改失败，请重试", self).exec_()
                        elif data["code"] == 10202:
                            MessageBox("成绩管理系统", "修改失败，系统只剩下最后一个默认权限组的超级管理员", self).exec_()
                        elif data["code"] == 10201:
                            MessageBox("成绩管理系统", "管理员禁止在此处修改自己的密码", self).exec_()
                        elif data["code"] == 10204:
                            MessageBox("成绩管理系统", "你不能封禁你自己", self).exec_()
                        elif data["code"] == 10205:
                            MessageBox("成绩管理系统", "禁止在此处关闭自己的OTP", self).exec_()
                        else:
                            MessageBox("成绩管理系统", "修改成功", self).exec_()
                            self.get_server_data()
            if action.text() == "删除":
                selected_items = self.TableWidget.selectedItems()
                if selected_items:
                    current_row = selected_items[0].row()
                    w = MessageBox("用户管理", f"是否删除 {self.TableWidget.item(current_row, 1).text()}", self)
                    if w.exec():
                        resp = http.post(setting.USER_DELETE,
                                         data={"id": int(self.TableWidget.item(current_row, 0).text())})
                        if resp.status_code != 200:
                            MessageBox("成绩管理系统", "接口请求错误", self).exec_()
                            return
                        data = resp.json()
                        if data["code"] == 10001:
                            MessageBox("成绩管理系统", "未登入，请重启软件", self).exec_()
                        elif data["code"] == 10103:
                            MessageBox("成绩管理系统", "删除失败，请重试", self).exec_()
                        else:
                            MessageBox("成绩管理系统", "删除成功", self).exec_()
                            self.get_server_data()

    def flush_table(self, datas: list):
        row = len(datas)
        self.TableWidget.setRowCount(row)
        for i in range(row):
            self.TableWidget.setItem(i, 0, QTableWidgetItem(str(datas[i]["id"])))
            self.TableWidget.setItem(i, 1, QTableWidgetItem(datas[i]["account"]))
            self.TableWidget.setItem(i, 2, QTableWidgetItem(str(datas[i]["group"])))
