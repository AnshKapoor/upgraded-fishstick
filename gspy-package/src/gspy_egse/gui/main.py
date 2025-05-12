# src/gspy_egse/gui/main.py
import os, platform, sys
from typing import List
from contextlib import suppress

def run(argv: List[str] | None = None) -> None:
    """
    GUI entry‑point for the `gspy-gui` launcher *and*
    for direct execution via `python -m gspy_egse.gui.main`.
    """
    if argv is None:                     # called by setuptools wrapper
        argv = sys.argv

    # -- lazy imports keep startup time minimal ----------------------------
    from gspy_egse.gui.branding import COMPANY, PRODUCT, VERSION_STR
    from PyQt6 import QtWidgets, QtGui
    from gspy_egse.gui.mainwindow import MyMainWindow
    from gspy_egse.gui.utils.widget import CusIcon, delay_in_main_thread
    from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

    # Windows per‑application taskbar ID
    if os.name == "nt":
        with suppress(Exception):
            import ctypes
            app_id = f"{COMPANY}.{PRODUCT}.{PRODUCT}.{VERSION_STR}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QtWidgets.QApplication(argv)

    production = False
    splash_img = QtGui.QPixmap(f":/icon-big{'-beta' if not production else ''}.png")
    splash = QtWidgets.QSplashScreen(splash_img)
    dpi_scale = splash.logicalDpiX() / 96.0
    splash.setPixmap(splash_img.scaledToWidth(int(400 * dpi_scale)))
    splash.show()

    # diagnostics only on first launch
    if "--reopen" not in argv:
        print("Python version:", platform.python_version())
        print(f"PyQt version: {PYQT_VERSION_STR} (Qt {QT_VERSION_STR})")

    app.setWindowIcon(CusIcon(f":/icon{'-beta' if not production else ''}.png"))
    app.processEvents()

    delay_in_main_thread(50,
        lambda: MyMainWindow(argv, splash=splash, main_file_path=os.path.abspath(__file__)).show()
    )

    sys.exit(app.exec())

# Optional convenience for `python -m gspy_egse.gui.main`
if __name__ == "__main__":
    run()
