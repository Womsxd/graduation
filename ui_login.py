# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_login.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(700, 500)
        Form.setMinimumSize(QtCore.QSize(700, 500))
        font = QtGui.QFont()
        font.setFamily("思源黑体 CN VF Medium")
        font.setPointSize(12)
        Form.setFont(font)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setMinimumSize(QtCore.QSize(350, 500))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/resource/image/login-bg.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setMinimumSize(QtCore.QSize(350, 500))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(15, 0, 21, 0)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setMinimumSize(QtCore.QSize(128, 128))
        self.label_2.setMaximumSize(QtCore.QSize(128, 128))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/resource/image/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 3, 1, 2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("思源黑体 CN VF Medium")
        font.setPointSize(20)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 1, 1, 3)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 1, 4, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem5 = QtWidgets.QSpacerItem(20, 23, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem5)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.username_line = LineEdit(self.widget)
        self.username_line.setObjectName("username_line")
        self.verticalLayout.addWidget(self.username_line)
        self.label_4 = QtWidgets.QLabel(self.widget)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.password_line = LineEdit(self.widget)
        self.password_line.setText("")
        self.password_line.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.password_line.setObjectName("password_line")
        self.verticalLayout.addWidget(self.password_line)
        spacerItem6 = QtWidgets.QSpacerItem(20, 22, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)
        self.login_button = PrimaryPushButton(self.widget)
        self.login_button.setObjectName("login_button")
        self.verticalLayout.addWidget(self.login_button)
        spacerItem7 = QtWidgets.QSpacerItem(20, 23, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem7)
        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_5.setText(_translate("Form", "学生成绩管理系统"))
        self.label_3.setText(_translate("Form", "用户名"))
        self.label_4.setText(_translate("Form", "密码"))
        self.login_button.setText(_translate("Form", "登入"))
from qfluentwidgets import LineEdit, PrimaryPushButton
import resource_rc