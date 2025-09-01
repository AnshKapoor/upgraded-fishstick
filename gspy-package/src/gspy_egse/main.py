# src/gspy_egse/gui/main.py
import os, platform, sys, logging
from datetime import datetime
from typing import List
from contextlib import suppress

# Setup logger
os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/%Y-%m-%d_%H-%M-%S.log")
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

def run(argv: List[str] | None = None) -> None:
    """
    GUI entry‑point for the `gspy-gui` launcher *and*
    for direct execution via `python -m gspy_egse.gui.main`.
    """
    if argv is None:                     # called by setuptools wrapper
        argv = sys.argv

    logger.info("Starting GSPY GUI application...")
    logger.debug(f"Arguments received: {argv}")
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
    logger.info("QApplication initialized.")

    production = False
    splash_img = QtGui.QPixmap(f":/icon-big{'-beta' if not production else ''}.png")
    splash = QtWidgets.QSplashScreen(splash_img)
    dpi_scale = splash.logicalDpiX() / 96.0
    splash.setPixmap(splash_img.scaledToWidth(int(400 * dpi_scale)))
    splash.show()
    logger.info("Splash screen displayed.")

    # diagnostics only on first launch
    if "--reopen" not in argv:
        python_ver = platform.python_version()
        logger.info(f"Python version: {python_ver}")
        logger.info(f"PyQt version: {PYQT_VERSION_STR} (Qt {QT_VERSION_STR})")

    app.setWindowIcon(CusIcon(f":/icon{'-beta' if not production else ''}.png"))
    app.processEvents()
    logger.debug("Main window icon set and events processed.")

    delay_in_main_thread(50,
        lambda: MyMainWindow(argv, splash=splash, main_file_path=os.path.abspath(__file__)).show()
    )
    logger.info("Main window scheduled to show after splash.")
    logger.info("Starting Qt event loop...")
    sys.exit(app.exec())

# Optional convenience for `python -m gspy_egse.gui.main`
if __name__ == "__main__":
    run()
