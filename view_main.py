from PyQt5.QtWidgets import QWidget
from qfluentwidgets import setThemeColor
import my_globals
from ui_view_main import Ui_ViewMain

import datetime

def get_greeting():
    now = datetime.datetime.now()
    hour = now.hour

    if hour < 6:
        text = "夜深了，注意休息!"
    elif hour < 9:
        text = "早上好！今天要做点什么?"
    elif hour < 12:
        text = "上午好，一定要保持好心态哦!"
    elif hour < 14:
        text = "中午好，吃完饭记得休息一下!"
    elif hour < 18:
        text = "下午好，时间过得好快呀!"
    else:
        text = "晚上好，今天过得如何? 要注意休息哦!"
    return text


class ViewMain(QWidget,Ui_ViewMain):
    def __init__(self):
        super(ViewMain, self).__init__()
        self.setupUi(self)
        setThemeColor('#28afe9')

        self.label_username.setText(my_globals.user_name)
        self.label_greeting.setText(get_greeting())
