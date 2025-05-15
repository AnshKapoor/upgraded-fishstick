from PyQt6 import QtCore, QtWidgets, uic


class EmptyWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)
        self.ui = uic.loadUi("ui/emptywidget.ui", self)
