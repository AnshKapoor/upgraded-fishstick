from PyQt6 import QtCore, QtWidgets, uic
from .consolewidget import ConsoleWidget

from importlib.resources import files, as_file  # stdlib, Python ≥3.9

pkg = "gspy_egse.gui.ui"
ui_name = "tabwidget.ui"

def stackedWidgetSet(stacked, widget):
    while stacked.count() > 0:
        stacked.removeWidget(stacked.currentWidget())
    stacked.addWidget(widget)


class BottomWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        ui_res = files(pkg).joinpath(ui_name)
        with as_file(ui_res) as ui_path:
            self.ui = uic.loadUi(str(ui_path), self)
        # self.ui = uic.loadUi("gspy_egse/gui/ui/tabwidget.ui", self)
        stackedWidgetSet(self.consoleWidget, ConsoleWidget())
