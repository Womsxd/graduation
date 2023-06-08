import json
from PyQt5 import QtWidgets
import my_dialog
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from qfluentwidgets import MessageBox, DWMMenu
import setting
from ui_other import Ui_Form
from request import http
import utils


class ViewStudent(QWidget, Ui_Form):
    now_pages = 1

    def __init__(self):
        super(ViewStudent, self).__init__()
        self.setObjectName("ViewStudent")
        self.setupUi(self)
        self.label_title.setText("学生管理")
        self.TableWidget.setColumnCount(5)
        self.TableWidget.setWordWrap(False)
        self.TableWidget.verticalHeader().hide()
        self.TableWidget.setHorizontalHeaderLabels(['编号', '学号', "姓名", "性别", '班级'])
        self.TableWidget.setStyleSheet("QTableWidget { border: none; }")
        self.pushbutton_query.clicked.connect(self.get_server_data)
        self.TableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TableWidget.customContextMenuRequested.connect(self.show_context_menu)
        if not utils.check_permission("student.add"):
            self.pushbutton_add.setEnabled(False)
        else:
            self.pushbutton_add.clicked.connect(self.add)
        self.TableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def get_server_data(self):
        keyword = self.line_edit_keyword.text()
        params = {"page": self.now_pages, "search": keyword}
        resp = http.get(setting.STUDENT_LIST, params=params)
        if resp.status_code != 200:
            MessageBox("成绩管理系统", "接口请求错误", self).exec_()
            return
        try:
            data = resp.json()
        except json.decoder.JSONDecodeError:
            MessageBox("成绩管理系统", "接口返回数据有误", self).exec_()
            return
        self.flush_table(data["data"]["students"])
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
        w = my_dialog.MessageBoxForStudent("学生管理", "请输入学学生信息", self)
        w.load_server_data()
        if w.exec():
            if w.line_edit_name.text() == "":
                MessageBox("学生管理", "输入不可为空", self).exec()
            else:
                sex_helper = utils.SexMap()
                resp = http.post(setting.STUDENT_ADD,
                                 data={"sid": w.line_edit_sid.text(), "name": w.line_edit_name.text(),
                                       "sex": sex_helper.to_number(w.sex_combo_box.text()),
                                       "class": w.class_combo_box.text().split(": ")[0]})
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
        if utils.check_permission("student.edit"):
            menu.addAction("编辑")
        if utils.check_permission("student.delete"):
            menu.addAction("删除")

        action = menu.exec_(self.TableWidget.mapToGlobal(pos))

        if action:
            if action.text() == "编辑":
                selected_items = self.TableWidget.selectedItems()
                if selected_items:
                    current_row = selected_items[0].row()
                    w = my_dialog.MessageBoxForStudent("学生管理", "请进行修改", self)
                    w.load_server_data()
                    w.line_edit_sid.setText(self.TableWidget.item(current_row, 1).text())
                    w.line_edit_name.setText(self.TableWidget.item(current_row, 2).text())
                    w.sex_combo_box.setText(self.TableWidget.item(current_row, 3).text())
                    w.class_combo_box.setText(self.TableWidget.item(current_row, 4).text())
                    if w.exec():
                        sex_helper = utils.SexMap()
                        resp = http.post(setting.STUDENT_EDIT,
                                         data={"id": int(self.TableWidget.item(current_row, 0).text()),
                                               "sid": w.line_edit_sid.text(), "name": w.line_edit_name.text(),
                                               "sex": sex_helper.to_number(w.sex_combo_box.text()),
                                               "class": w.class_combo_box.text().split(": ")[0]})
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
                    w = MessageBox("学生管理", f"是否删除 {self.TableWidget.item(current_row, 2).text()}", self)
                    if w.exec():
                        resp = http.post(setting.STUDENT_DELETE,
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
        sex_helper = utils.SexMap()
        for i in range(row):
            self.TableWidget.setItem(i, 0, QTableWidgetItem(str(datas[i]["id"])))
            self.TableWidget.setItem(i, 1, QTableWidgetItem(datas[i]["sid"]))
            self.TableWidget.setItem(i, 2, QTableWidgetItem(datas[i]["name"]))
            self.TableWidget.setItem(i, 3, QTableWidgetItem(sex_helper.to_string(datas[i]["sex"])))
            self.TableWidget.setItem(i, 4, QTableWidgetItem(datas[i]["class"]))
