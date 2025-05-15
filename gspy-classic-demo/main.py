#!/usr/bin/env python

import platform
import sys
import os
import ctypes
from typing import *
import time

updated = False
ask_root = False
install_yes = False
app = None
app_icon = None
py3 = True
TMP_FILE_HANDLE = "out.tmp"


def query_yes_no(question: str, default: Optional[str] = "yes") -> bool:
    """
    Ask a yes/no question via raw_input() and return their answer
    
    :param question: is a string that is presented to the user
    :param default: is the presumed answer if the user just hits <Enter>
                    It must be "yes/ye/y" (the default), "no/n" or None (meaning
                    an answer is required of the user)
    :return: True for "yes" or False for "no"
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        if py3:
            choice = input().lower()
        else:
            choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def wait_handle(file: str):
    """
    Wait for a file to be deleted
    
    :param file: Filename of the file
    """

    while os.path.isfile(file):
        time.sleep(.1)
    time.sleep(.05)


def install(packages: TypeVar('P', List[str], str)):
    """
    Installs one or more packages through pip. This might cause a call of sudo, or elevation depending on the os.
    Executions of other programs are delayed by a prompt though

    :param packages: Name of the package, or a list of names
    """
    global updated, ask_root, install_yes
    pass


def check_py(try_update: bool = False):
    """
    Check if the running python interpreter meets the programs requirements. Also try to update it
    
    :param try_update: whether we should try to install the required python if it's not installed
    :return: 0: No update installed, check for requirement
             1: Requirement not met.
             2: exit this program, another instance was started.
    """
    global install_yes, py3
    return 0


def check_installation() -> bool:
    """
    Check if the running environment meets all requirements, try to install missing ones
    
    :return: True if the environment is okay, False if the program cannot run
    """
    global install_yes
    return True


def run(argv: List[str]):
    """
    Run the application
    
    :param argv: List of command parameters
    """
    global app, app_icon
    from gseos_qt import COMPANY, PRODUCT, VERSION_STR
    from PyQt6 import QtWidgets, QtCore, QtGui
    from gseos_qt.mainwindow import MyMainWindow
    from gseos_qt.utils.widget import CusIcon, delay_in_main_thread
    from contextlib import suppress
    from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    import gseos_qt.qrc
    # from sip import SIP_VERSION_STR

    if os.name == 'nt' or os.name == 'WINDOWS_NT':
        with suppress(Exception):
            import ctypes
            app_id = '%s.%s.%s.%s' % (COMPANY, PRODUCT, PRODUCT, VERSION_STR)  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    app = QtWidgets.QApplication(argv)

    try:
        production = Repository('.').head.shorthand in ['master', 'production', 'release', 'stable']
    except (Exception,):
        production = True

    splash_img = QtGui.QPixmap(':/icon-big%s.png' % ('' if production else '-beta'))
    splash = QtWidgets.QSplashScreen(splash_img)
    dpi_scale = splash.logicalDpiX() / 96.0
    splash.setPixmap(splash_img.scaledToWidth(400 * int(dpi_scale)))
    splash.show()

    with open(".py_bin", 'w') as f:
        f.write(sys.executable)
    main_file_path = os.path.abspath(__file__)

    os.chdir("gseos_qt")

    if "--reopen" not in argv:  # only print environment info at first execution
        print("Python version:", platform.python_version())
        print("PyQt version: %s (Qt %s)" % (PYQT_VERSION_STR, QT_VERSION_STR))

    app_icon = CusIcon(':/icon%s.png' % ('' if production else '-beta'))
    app.setWindowIcon(app_icon)

    app.processEvents()

    delay_in_main_thread(50, lambda: MyMainWindow(argv, splash=splash, main_file_path=main_file_path).show())

    sys.exit(app.exec())


def change_dir(file: Optional[str] = None):
    """
    Changes working directory to the directory of file, if provided, otherwise __file__

    :param file: file in the directory which should become wd
    """
    abspath = os.path.abspath(__file__ if file is None else file)
    dir_name = os.path.dirname(abspath)
    os.chdir(dir_name)


def check_modules():
    """
    Before program start checks if all necessary modules can be imported
    Returns: True if all modules were imported, False otherwise

    """
    success = True
    return success


if __name__ == '__main__':
    """ Main entry point of the program """
    print(sys.version)
    change_dir()

    check_modules()

    install_only = "--root-install" in sys.argv
    install_yes = "--install-y" in sys.argv
    try:
        if check_modules():
            run(sys.argv)
    finally:
        if install_only:
            os.remove(TMP_FILE_HANDLE)

# TODO restore panels fails under pyqt6
# TODO File down upload file explorer keeps reopening
# TODO check for program not closing properly
