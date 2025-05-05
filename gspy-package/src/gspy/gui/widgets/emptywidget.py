from PyQt6 import QtWidgets, uic


class EmptyWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)
        self.ui = uic.loadUi("src/gspy/gui/ui/emptywidget.ui", self)
