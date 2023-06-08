from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent
from qfluentwidgets import SwitchButton, IndicatorPosition


class CustomSwitchButton(SwitchButton):
    clicked = pyqtSignal(bool)

    def __init__(self, parent=None, indicatorPos=IndicatorPosition.LEFT):
        super().__init__(parent, indicatorPos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        self.clicked.emit(self.indicator.isChecked())
