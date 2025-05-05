import cmd
import threading
import io

from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtCore import pyqtSlot


def buffer_pop(s: io.StringIO) -> str:
    s.flush()
    out = s.getvalue()
    s.truncate(0)
    s.seek(0)
    return out


def append_no_newline(edit: QtWidgets.QTextEdit, s: str):
    edit.moveCursor(QtGui.QTextCursor.End)
    edit.insertPlainText(s)
    edit.moveCursor(QtGui.QTextCursor.End)


class ConsoleWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)
        self.ui = uic.loadUi("src/gspy/gui/ui/consolewidget.ui", self)
        self.buffer = io.StringIO()
        self.interpreter = GseConsole(sout=self.buffer)
        self.lineEdit = self.lineEditWidget  # type: QtWidgets.QLineEdit
        self.textBrowser = self.textBrowserWidget  # type: QtWidgets.QTextBrowser
        # noinspection PyUnresolvedReferences
        self.lineEdit.returnPressed.connect(self.command_sent)

    @pyqtSlot()
    def command_sent(self):
        cmd = self.lineEdit.text()
        self.lineEdit.clear()
        t = threading.Thread(target=self.gse, args=[cmd])
        t.start()
        t.join()
        print("fertig.")

    def gse(self, prm):
        append_no_newline(self.textBrowser, "%s\n" % prm)
        line = self.interpreter.precmd(prm)
        result = self.interpreter.onecmd(line)
        resultPost = self.interpreter.postcmd(result, line)
        output = buffer_pop(self.buffer)

        append_no_newline(self.textBrowser, "%s> " % output)


class GseConsole(cmd.Cmd):
    def __init__(self, sout):
        cmd.Cmd.__init__(self, stdout=sout)
        self.prompt = "> "
        self.stdout = sout

    def try_exec(self, pycmd):
        from contextlib import redirect_stdout
        try:
            with redirect_stdout(self.stdout):
                exec(pycmd)
        except Exception as e:
            with redirect_stdout(self.stdout):
                print(str(e))

    def do_shell(self, s):
        """Execute shell commands"""
        import subprocess
        from contextlib import redirect_stdout

        with redirect_stdout(self.stdout):
            try:
                result = subprocess.check_output(s, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                print(str(result), end='', flush=True)
            except Exception as e:
                with redirect_stdout(self.stdout):
                    print(str(e))

    def do_exec(self, prm):
        """Execute Python commands"""

        if (prm != ''):
            self.try_exec(prm)

    def do_exit(self, prm):
        """Really?"""
        return True
