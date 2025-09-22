from PyQt6 import QtWidgets, uic

from importlib.resources import files, as_file  # stdlib, Python ≥3.9

pkg = "gspy_egse.gui.ui"
ui_name = "emptywidget.ui"

class EmptyWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)
        ui_res = files(pkg).joinpath(ui_name)
        with as_file(ui_res) as ui_path:
            self.ui = uic.loadUi(str(ui_path), self)
