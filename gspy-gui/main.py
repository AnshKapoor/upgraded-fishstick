import os
import platform
import sys
from typing import List


def run(argv: List[str]):
    """
    Run the application

    :param argv: List of command parameters
    """
    global app, app_icon
    from branding import COMPANY, PRODUCT, VERSION_STR
    from PyQt6 import QtWidgets, QtGui
    from mainwindow import MyMainWindow
    from utils.widget import CusIcon, delay_in_main_thread
    from contextlib import suppress
    from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

    if os.name == 'nt' or os.name == 'WINDOWS_NT':
        with suppress(Exception):
            import ctypes
            app_id = '%s.%s.%s.%s' % (COMPANY, PRODUCT, PRODUCT, VERSION_STR)  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    app = QtWidgets.QApplication(argv)

    production = False # TODO: Where is this relevant

    splash_img = QtGui.QPixmap(':/icon-big%s.png' % ('' if production else '-beta'))
    splash = QtWidgets.QSplashScreen(splash_img)
    dpi_scale = splash.logicalDpiX() / 96.0
    splash.setPixmap(splash_img.scaledToWidth(400 * int(dpi_scale)))
    splash.show()

    with open(".py_bin", 'w') as f:
        f.write(sys.executable)
    main_file_path = os.path.abspath(__file__)

    if "--reopen" not in argv:  # only print environment info at first execution
        print("Python version:", platform.python_version())
        print("PyQt version: %s (Qt %s)" % (PYQT_VERSION_STR, QT_VERSION_STR))

    app_icon = CusIcon(':/icon%s.png' % ('' if production else '-beta'))
    app.setWindowIcon(app_icon)

    app.processEvents()

    delay_in_main_thread(50, lambda: MyMainWindow(argv, splash=splash, main_file_path=main_file_path).show())

    sys.exit(app.exec())

if __name__ == "__main__":
    run(sys.argv)