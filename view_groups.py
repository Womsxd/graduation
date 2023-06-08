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


class ViewGroups(QWidget, Ui_Form):
    now_pages = 1
    user_group_ids = set()

    def __init__(self):
        super(ViewGroups, self).__init__()
        self.setObjectName("ViewGroups")
        self.setupUi(self)
        self.label_title.setText("用户组管理")
        self.TableWidget.setColumnCount(2)
        self.TableWidget.setWordWrap(False)
        self.TableWidget.verticalHeader().hide()
        self.TableWidget.setHorizontalHeaderLabels(['编号', '用户组名称'])
        self.TableWidget.setStyleSheet("QTableWidget { border: none; }")
        self.pushbutton_query.clicked.connect(self.get_server_data)
        self.TableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TableWidget.customContextMenuRequested.connect(self.show_context_menu)
        if not utils.check_permission("groups.add"):
            self.pushbutton_add.setEnabled(False)
        else:
            self.pushbutton_add.clicked.connect(self.add)
        self.TableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def get_server_data(self):
        keyword = self.line_edit_keyword.text()
        params = {"page": self.now_pages, "search": keyword}
        resp = http.get(setting.GROUP_LIST, params=params)
        if resp.status_code != 200:
            MessageBox("成绩管理系统", "接口请求错误", self).exec_()
            return
        try:
            data = resp.json()
        except json.decoder.JSONDecodeError:
            MessageBox("成绩管理系统", "接口返回数据有误", self).exec_()
            return
        self.flush_table(data["data"]["groups"])
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
        w = my_dialog.MessageForGroup("权限管理", "请输入学院名称", self)
        if w.exec():
            adds = w.get_input()
            if adds == "" or w.line_edit_perms.text() == "":
                MessageBox("权限组管理", "输入不可为空", self).exec()
            else:
                pda = {"name": adds, "permissions": w.line_edit_perms.text()}
                if w.line_edit_ins.text() != "":
                    pda["inherit"] = w.line_edit_ins.text()
                resp = http.post(setting.GROUP_ADD, data=pda)
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
        if utils.check_permission("group.edit"):
            menu.addAction("编辑")
        if utils.check_permission("group.delete"):
            menu.addAction("删除")

        action = menu.exec_(self.TableWidget.mapToGlobal(pos))

        if action:
            if action.text() == "编辑":
                selected_items = self.TableWidget.selectedItems()
                print(selected_items)
                if selected_items:
                    current_row = selected_items[0].row()
                    w = my_dialog.MessageForGroup("权限组管理", "请进行修改", self)
                    server_user_info = http.get(setting.GROUP_QUERY,
                                                params={"id": int(self.TableWidget.item(current_row, 0).text())}).json()
                    w.line_edit_name.setText(self.TableWidget.item(current_row, 1).text())
                    w.line_edit_perms.setText(server_user_info["data"]["permissions"])
                    w.line_edit_ins.setText(server_user_info["data"]["inherit"])
                    if w.exec():
                        adds = w.get_input()
                        if adds != "":
                            resp = http.post(setting.COLLEGE_EDIT,
                                             data={"id": int(self.TableWidget.item(current_row, 0).text()),
                                                   "name": adds, "permissions": w.line_edit_perms.text(),
                                                   "inherit": w.line_edit_ins.text()})
                            if resp.status_code != 200:
                                MessageBox("成绩管理系统", "接口请求错误", self).exec_()
                                return
                            data = resp.json()
                            if data["code"] == 10001:
                                MessageBox("成绩管理系统", "未登入，请重启软件", self).exec_()
                            elif data["code"] == 10103:
                                MessageBox("成绩管理系统", "修改失败，请重试", self).exec_()
                            else:
                                MessageBox("成绩管理系统", "修改成功", self).exec_()
                                self.get_server_data()
            if action.text() == "删除":
                selected_items = self.TableWidget.selectedItems()
                if selected_items:
                    current_row = selected_items[0].row()
                    w = MessageBox("权限组管理管理", f"是否删除 {self.TableWidget.item(current_row, 1).text()}", self)
                    if w.exec():
                        resp = http.post(setting.GROUP_DELETE,
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

    def flush_table(self, colleges: list):
        row = len(colleges)
        self.TableWidget.setRowCount(row)
        for i in range(row):
            self.TableWidget.setItem(i, 0, QTableWidgetItem(str(colleges[i]["id"])))
            self.user_group_ids.add(str(colleges[i]["id"]))
            self.TableWidget.setItem(i, 1, QTableWidgetItem(colleges[i]["name"]))
