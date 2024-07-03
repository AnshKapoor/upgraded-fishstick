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
    import getpass
    import os
    import pip

    if not ask_root and os.name == 'posix' and getpass.getuser() != 'root':
        ask_root = True
        if install_yes or query_yes_no("The installation probably requires root privileges. Try 'sudo'?\n"
                                       "WARNING: This will open another window"):
            from subprocess import Popen

            open(TMP_FILE_HANDLE, "a").close()
            Popen(["xterm", "-e", "sudo", sys.executable, os.path.abspath(__file__), "--root-install"])
            wait_handle(TMP_FILE_HANDLE)
    if not ask_root and (os.name == 'nt' or os.name == 'WINDOWS_NT'):
        shell32 = ctypes.windll.shell32

        try:
            admin = shell32.IsUserAnAdmin()
        except (Exception,):
            admin = False
        if not admin:
            ask_root = True
            if install_yes or query_yes_no("The installation probably requires admin privileges. Try elevating?"):
                try:
                    from shutil import copy2
                    file = os.path.join(os.path.expanduser("~"), "main.tmp.py")
                    copy2(__file__, file)
                    change_dir(file)
                    open(TMP_FILE_HANDLE, "a").close()
                    ctypes.windll.shell32.ShellExecuteW(None,
                                                        "runas",
                                                        sys.executable,
                                                        " ".join([str(file), "--root-install"]),
                                                        None,
                                                        1)

                    wait_handle(TMP_FILE_HANDLE)
                    os.remove(file)
                    change_dir()
                except (Exception,):
                    import traceback
                    traceback.print_exc()

    if not updated:
        updated = True
        pip.main(['install', '-U', 'pip'])
    if isinstance(packages, list):
        for package in packages:
            pip.main(['install', package])
    else:
        pip.main(['install', packages])


def check_py(try_update: bool = False):
    """
    Check if the running python interpreter meets the programs requirements. Also try to update it
    
    :param try_update: whether we should try to install the required python if it's not installed
    :return: 0: No update installed, check for requirement
             1: Requirement not met.
             2: exit this program, another instance was started.
    """
    global install_yes, py3
    try:
        if try_update:
            if os.path.isfile(".py_bin"):
                with open(".py_bin", 'r') as f:
                    py = f.read()
                    if os.path.isfile(py) and sys.executable != py:
                        import subprocess
                        subprocess.call([py, os.path.abspath(__file__)])
                        return 2  # exit

        version_s = platform.python_version_tuple()
        version = [
            int(version_s[0]),
            int(version_s[1])
        ]
        py3 = version[0] >= 3
        if try_update and (version[0] < 3 or version[1] < 6):
            if install_yes or query_yes_no("Your python is outdated. Attempt automatic upgrade?"):
                import subprocess
                if (os.name == 'nt' or os.name == 'WINDOWS_NT'):
                    subprocess.call(["install-windows.bat"])
                    subprocess.call(["C:\\Python3.6\\python.exe", os.path.abspath(__file__)])
                    return 2  # exit
                elif os.name == 'posix':
                    subprocess.call(["./install-ubuntu.sh"])
                    return 2  # exit
            else:
                return 0  # continue
        if version[0] < 3:
            print("[Error!] Python 3 required.")
            return 1  # abort
        elif version[0] > 3:
            print("[Warning!] Python %d might be incompatible. Python 3 is recommended." % version[0])
        elif version[1] < 6:
            print("[Error!] Python 3.6 or newer required.")
            return 1  # abort
    except (Exception,):
        print("[Warning!] Could not find out if your python version is compatible!")

    return 0  # continue


def check_installation() -> bool:
    """
    Check if the running environment meets all requirements, try to install missing ones
    
    :return: True if the environment is okay, False if the program cannot run
    """
    global install_yes
    check = check_py(True)
    if check == 2:
        return False
    if check == 0 and check_py() == 1:
        return False

    try:
        import PyQt6
    except (ModuleNotFoundError, ImportError):
        install("pyqt6")
        import PyQt6
    try:
        import serial
    except (ModuleNotFoundError, ImportError):
        install("pyserial")
        import serial
    try:
        import pyqtgraph
    except (ModuleNotFoundError, ImportError):
        install("pyqtgraph")
        import pyqtgraph
    try:
        import qtawesome
    except (ModuleNotFoundError, ImportError):
        install("qtawesome")
        import qtawesome
    try:
        import matplotlib
    except (ModuleNotFoundError, ImportError):
        install("matplotlib")
        import matplotlib
    try:
        import PIL
    except (ModuleNotFoundError, ImportError):
        install("Pillow")
        import PIL
    try:
        import pympler
    except (ModuleNotFoundError, ImportError):
        install("Pympler")
        import pympler
    try:
        import pygit2
    except (ModuleNotFoundError, ImportError):
        install("pygit2")
        try:
            import pygit2
        except (Exception,):
            if os.name == 'posix':
                if install_yes or query_yes_no("pygit2 could not be installed. Attempt ubuntu fix?"):
                    from subprocess import call

                    os.chmod("install-libgit.sh", 0o755)
                    call(["./install-libgit.sh"])
                else:
                    print("pygit2 could not be installed.")
                    return False
            else:
                raise Exception("pygit2 could not be installed.")
    return True


def run(argv: List[str]):
    """
    Run the application
    
    :param argv: List of command parameters
    """
    global app, app_icon
    from gseos_qt import COMPANY, PRODUCT, VERSION_STR
    from pygit2 import Repository
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


if __name__ == '__main__':
    """ Main entry point of the program """
    print(sys.version)
    change_dir()

    install_only = "--root-install" in sys.argv
    install_yes = "--install-y" in sys.argv
    try:
        #if check_installation() and not install_only:
        run(sys.argv)
    finally:
        if install_only:
            os.remove(TMP_FILE_HANDLE)

# TODO restore panels fails under pyqt6
# TODO File down upload file explorer keeps reopening
# TODO check for program not closing properly
