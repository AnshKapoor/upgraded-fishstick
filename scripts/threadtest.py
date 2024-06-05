from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5 import QtWidgets
import sys
import time

sys.path.append("../gseos_qt")
try:
    from ..gseos_qt.utils.widget import call_in_main_thread
except (ValueError, ImportError):  # modules can be found from PATH
    from gseos_qt.utils.widget import call_in_main_thread


@pyqtSlot()
def slot(done=True):
    print("Im a slot!")
    if done:
        print()
        print("done.")
        sys.exit()


s = QTimer()


def slota():
    import threading

    print("starting thread.")
    threading.Thread(target=slotb).start()


def slotb():
    print("in new thread.")
    slotc()
    time.sleep(2)
    call_in_main_thread(slotc, (True,))


def slotc(in_main=False):
    if in_main:
        print()
    print("-------------")
    print("with%s main:" % ("out" if not in_main else ""))
    time.sleep(.1)
    s.timeout.connect(slot)
    s.setSingleShot(True)
    s.start(10)
    print("slot queued..")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    print("testing slot:")
    slot(False)
    slota()
    sys.exit(app.exec_())
