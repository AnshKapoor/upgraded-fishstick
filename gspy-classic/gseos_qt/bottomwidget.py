from PyQt6 import QtCore, QtWidgets, uic
from .consolewidget import ConsoleWidget


def stackedWidgetSet(stacked, widget):
    while stacked.count() > 0:
        stacked.removeWidget(stacked.currentWidget())
    stacked.addWidget(widget)


class BottomWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)
        self.ui = uic.loadUi("ui/tabwidget.ui", self)
        stackedWidgetSet(self.consoleWidget, ConsoleWidget())
