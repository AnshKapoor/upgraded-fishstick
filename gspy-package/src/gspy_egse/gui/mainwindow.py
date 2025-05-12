import os
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon
from contextlib import suppress
from typing import *

from gspy_egse.gui.branding import *
from gspy_egse.gui.utils.misc import Extendable
from gspy_egse.gui.utils.widget import call_in_main_thread, event_name
from gspy_egse.gui.widgets.emptywidget import EmptyWidget
from gspy_egse.gui.widgets.bottomwidget import BottomWidget
from gspy_egse.gui.widgets.drophint import DropHint
from gspy_egse.gui.utils.widget import async_in_main_thread, ResizeListener, PaintListener
from gspy_egse.gui.utils.recorder import RecorderWindow, Recorder

global recorder
recorder = Recorder()
MAIN_FILE_PATH = None

class MessageHandler(QtCore.QObject):
    def __init__(self, box: QtWidgets.QTextBrowser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.box = box
        box.setFont(QtGui.QFont("Source Code Pro", 11))
        self._stale_max = 0
        self._do_scroll = False
        self.lines = []
        self._l = [ResizeListener(self.box, self.post_scroll),
                   PaintListener(self.box, self.pre_scroll)]
        self.pre_scroll()

    def pre_scroll(self):
        try:
            scroll = self.box.verticalScrollBar()
        except (Exception,):
            return

        self._do_scroll = False
        if scroll.value() >= self._stale_max:
            self._do_scroll = True

    def post_scroll(self):
        try:
            scroll = self.box.verticalScrollBar()
        except (Exception,):
            return

        if self._do_scroll:
            scroll.setValue(scroll.maximum())
        self._stale_max = scroll.maximum()

    def a_add_lines(self):
        self.pre_scroll()
        while len(self.lines):
            line = self.lines[0]
            self.box.append(line)
            del self.lines[0]
        self.post_scroll()

    def warning(self, message):
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:orange">[Warning]</span> %s</span>' % message,))

    def error(self, message):
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:red   ">[Error]</span>   %s</span>' % message,))

    def info(self, message):
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:blue  ">[Info]</span>    %s</span>' % message,))

    def success(self, message):
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:green ">[Success]</span> %s</span>' % message,))


def stacked_widget_set(stacked, widget):
    while stacked.count() > 0:
        stacked.removeWidget(stacked.currentWidget())
    stacked.addWidget(widget)
    widget.setParent(stacked)
    widget.show()


def selection_to_array(sel: QtCore.QModelIndex) -> "[int]":
    if sel.parent().parent() == sel.parent():
        return [sel.row()]

    l = selection_to_array(sel.parent())
    l.append(sel.row())
    return l


class DetachedWindow(QtWidgets.QMainWindow):
    def __init__(self, window: "MyMainWindow", widget: QtWidgets.QWidget, selection, name, *args, **kwargs):
        self.initialized = False
        # self.i = 0
        # self.llast_event = None
        self.last_event = None
        self.dragging = False
        super().__init__(*args, **kwargs)
        self.main_window = window
        self.setWindowTitle(window.windowTitle())
        self.widget = widget
        self.selection = selection
        self.name = name
        self.saved = False

        pos = widget.mapToGlobal(widget.pos())  # type: QtCore.QPoint
        pos -= window.mapToGlobal(window.rect().topLeft()) - window.pos()
        geo = widget.geometry()

        window.set_widget(EmptyWidget(), False)
        self.setCentralWidget(widget)
        widget.setParent(self)

        self.setGeometry(geo)
        self.move(pos)
        self.show()
        if os.name == 'nt' or os.name == 'WINDOWS_NT':
            self.hide()
            self.show()

        with suppress(Exception):
            # noinspection PyUnresolvedReferences
            self.widget.handle_detach()
        widget.show()
        self.initialized = True

    def event(self, q_event: QtCore.QEvent):
        p_e = QtCore.QEvent.Paint
        m_e = QtCore.QEvent.Move
        u_e = QtCore.QEvent.UpdateRequest
        c_e = QtCore.QEvent.Close
        z_o_c = QtCore.QEvent.ZOrderChange
        l_r = QtCore.QEvent.LayoutRequest

        if not self.initialized or q_event.type() in [216, p_e, u_e, z_o_c, l_r]:
            return QtWidgets.QMainWindow.event(self, q_event)
        if q_event.type() == c_e:
            self.initialized = False
            if self.widget is not None:
                if not self.saved:
                    with suppress(Exception):
                        self.widget.delete_settings()
                self.widget.deleteLater()
                self.widget = None
            if self.main_window is not None:
                self.main_window.windows.remove(self)
                self.main_window = None
            return QtWidgets.QMainWindow.event(self, q_event)
        if not self.dragging and self.last_event == m_e and q_event.type() == m_e:
            if self.main_window.isVisible() and not self.main_window.isMinimized():
                self.main_window.drop_hint.fade_in()
                self.dragging = True
                self.main_window.raise_()
        elif self.dragging and q_event.type() != m_e:
            self.dragging = False
            self.main_window.drop_hint.fade_out()
            if self.main_window.drop_hint.mouse_inside:
                self.reattach()
        elif self.dragging and self.main_window.drop_hint.animation_finished:
            self.main_window.drop_hint.set_mouse_pos(QtGui.QCursor.pos())

        if self.initialized and (not self.main_window.isVisible() or self.main_window.isMinimized()):
            self.main_window.drop_hint.fade_out()
        elif self.dragging:
            self.raise_()

        self.last_event = q_event.type()
        return QtWidgets.QMainWindow.event(self, q_event)

    def reattach(self):
        self.initialized = False
        if self.main_window is not None:
            self.main_window.set_widget(self.widget)
            self.main_window.restore_selection(self.selection, check_name=self.name)
            self.main_window.windows.remove(self)
            self.initialized = False
            self.main_window = None

        with suppress(Exception):
            self.widget.handle_reattach()

        self.widget = None
        self.deleteLater()

    def to_variant(self):
        self.saved = True
        try:
            identifier = self.widget.identifier
        except AttributeError:
            identifier = None

        val_map = {
            "geometry": self.saveGeometry(),
            "selection": self.selection,
            "name": self.name,
            "identifier": identifier
        }
        return QtCore.QVariant(val_map)

    @staticmethod
    def from_variant(window, val):
        import copy
        name = val["name"]
        sel = val["selection"]
        sel_cp = copy.deepcopy(sel)
        item = window.model.item(int(sel[0]))
        while len(sel) > 1:
            del sel[0]
            item = item.child(int(sel[0]))

        if name != item.name:
            window.message_handler.error("Window %s could not be restored." % name)
            return None

        try:
            widget = item.widget(window, identifier=val["identifier"])
        except TypeError:
            widget = item.widget(window)
        window = DetachedWindow(window, widget, sel_cp, name)
        window.restoreGeometry(val["geometry"])

        return window


class MyMainWindow(QtWidgets.QMainWindow, Extendable):
    def __init__(self, argv, *args, splash: QtWidgets.QSplashScreen = None, main_file_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        global MAIN_FILE_PATH
        if main_file_path is not None:
            MAIN_FILE_PATH = main_file_path
        self.initialized = False
        self.splash = splash
        self.setWindowOpacity(0)
        print("now we are in the init of MyMainWindow Class")

        # noinspection PyCallByClass,PyTypeChecker
        QtGui.QFontDatabase.addApplicationFont(":/SourceCodePro-Regular.ttf")
        # noinspection PyCallByClass,PyTypeChecker
        QtGui.QFontDatabase.addApplicationFont(":/FontAwesome_new.ttf")

        self.record_window = None
        self.model = QStandardItemModel()
        self.message_handler = None  # type: MessageHandler
        self.current_widget = None  # type: QtWidgets.QWidget
        self.selection = None
        self.last_selection_item = None
        self.bottom_dock = None
        self.bottom_widget = None
        self.tree_dock = None
        self.tree_widget = None  # type: QtWidgets.QTreeView
        self.background_tasks = []
        self.windows: List[QtWidgets.QMainWindow] = []
        self.setCorner(QtCore.Qt.BottomLeftCorner, QtCore.Qt.LeftDockWidgetArea)
        self.ui = uic.loadUi("src/gspy_egse/gui/ui/mainwindow.ui", self)
        self.setWindowTitle(PRODUCT)
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.set_widget(EmptyWidget())
        self.restore_panels()
        self.actionRestore_Panels.triggered.connect(self.restore_panels)
        self.actionDetach.triggered.connect(self.detach_screen)
        self.actionRecorder.triggered.connect(self.show_recorder)

        dh = self.drop_hint = DropHint(self)
        dh.setGeometry(self.rect())

        if "--refresh-config" in argv:
            QtCore.QSettings(COMPANY, PRODUCT).clear()
        if "--corrupt-config" in argv:
            self.hide()
            QtCore.QSettings(COMPANY, PRODUCT).setValue("geometry", -1)
            print("Config is now broken")
            self.kill_later()
        elif "--restore-settings" in argv:
            self.hide()
            async_in_main_thread(self.restore_settings)
        else:
            QtCore.QTimer(self).singleShot(500, self.read_settings)

    def show_recorder(self):
        try:
            self.record_window.show()
            self.record_window.raise_()
        except (Exception,):
            self.record_window = RecorderWindow()
            self.record_window.show()
            self.record_window.raise_()

    def restore_settings(self):
        """
        Asks the user if he wants to reset his settings
        """
        reply = QtWidgets.QMessageBox.warning(
            None, PRODUCT,
            "It seems your settings could not be loaded. Your configuration seems invalid. "
            "Do you want to refresh it? (Your settings will be lost.)",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.re_open(["--refresh-config"])
        else:
            self.kill()

    def re_open(self, params=None):
        from subprocess import call
        from sys import executable
        try:
            cmd = [executable, MAIN_FILE_PATH, "--reopen"]
            if params is not None:
                for p in params:
                    cmd.append(p)
            self.kill()
            call(cmd)
        except (Exception,):
            import traceback
            traceback.print_exc()

    def kill_later(self):
        QtCore.QTimer(self).singleShot(500, self.kill)

    def kill(self):
        self.initialized = True
        self.finish_splash()
        for w in self.windows:
            w.saved = True
            w.main_window = None
            w.close()
            w.deleteLater()
        self.kill_tasks()
        self.initialized = False
        self.close()
        self.deleteLater()
        if self.current_widget is not None:
            self.current_widget.deleteLater()

    def event(self, q_event: QtCore.QEvent):
        if not self.initialized:
            return QtWidgets.QMainWindow.event(self, q_event)
        if q_event.type() == QtCore.QEvent.Resize:
            self.drop_hint.setGeometry(self.rect())
        if q_event.type() == QtCore.QEvent.Close:
            self.setWindowOpacity(.8)
            self.setEnabled(False)
            QtWidgets.QApplication.processEvents()
            detached_windows = list()
            for window in self.windows:
                detached_windows.append(window.to_variant())
                window.main_window = None
                window.close()
                window.deleteLater()
            if self.current_widget is not None:
                self.current_widget.deleteLater()
            self.kill_tasks(True)
            settings = QtCore.QSettings(COMPANY, PRODUCT)
            settings.setValue("geometry", self.saveGeometry())
            # settings.setValue("windowState", self.saveState())
            settings.setValue("initialized", 1)
            settings.setValue("selection", self.selection)
            settings.setValue("selection_name",
                              None if self.last_selection_item is None else self.last_selection_item.name)
            settings.setValue("detached_windows", detached_windows)

        return QtWidgets.QMainWindow.event(self, q_event)

    def read_settings(self):
        try:
            self._read_settings()
            self.finish_splash()
        except (Exception,):
            import traceback
            traceback.print_exc()

            self.re_open(["--restore-settings"])

    def _read_settings(self):
        global settings
        settings = QtCore.QSettings(COMPANY, PRODUCT)
        self.initialized = True
        QtCore.QTimer(self).singleShot(1, self.show)
        try:
            if int(settings.value("initialized")) != 1:
                return
        except TypeError:
            return

        self.restoreGeometry(settings.value("geometry"))

        windows = settings.value("detached_windows")
        windows = [] if windows is None else windows
        for window in windows:
            window = DetachedWindow.from_variant(self, window)
            if window is not None:
                self.windows.append(window)
        selection = settings.value("selection")
        if selection is not None:
            # import time
            # time.sleep(.1)  # this fixes a sigsegv crash
            with suppress(Exception):
                self.restore_selection(selection, check_name=settings.value("selection_name"), set_widget=True)
                # self.restoreState(settings.value("windowState"))
        if settings.value("recorder_visible", 0) == 1:
            self.show_recorder()

    def finish_splash(self):
        if self.splash is not None:
            self.splash.finish(self)
            self.splash = None

    def restore_selection(self, sel: List[int], check_name=None, set_widget=False):
        item = self.model.item(int(sel[0]))
        while len(sel) > 1:
            del sel[0]
            item = item.child(int(sel[0]))

        if check_name != item.name:
            self.message_handler.error('Screen %s could not be restored.' % check_name)
            return
        index = self.model.indexFromItem(item)

        selection_item = self.update_selection(index)
        if not set_widget or selection_item is None:
            return

        self.set_widget(selection_item.widget(self))
        self.message_handler.info("Loading Screen " + selection_item.name + ".")

    def kill_tasks(self, on_close=False):
        for t in self.background_tasks:
            with suppress(Exception):
                t.close()
        try:
            self.record_window.close()
            if on_close:
                QtCore.QSettings(COMPANY, PRODUCT).setValue("recorder_visible", 1)
        except (Exception,):
            if on_close:
                QtCore.QSettings(COMPANY, PRODUCT).setValue("recorder_visible", 0)
        self.background_tasks = list()

    def set_widget(self, widget: QtWidgets.QWidget, close=True):
        if close and self.current_widget is not None:
            self.current_widget.deleteLater()
        self.current_widget = widget
        stacked_widget_set(self.stackedWidget, widget)
        widget.show()
        if self.message_handler is not None:
            self.message_handler.post_scroll()

    def detach_screen(self):
        if self.last_selection_item is None:
            return
        self.windows.append(DetachedWindow(self, self.current_widget, self.selection, self.last_selection_item.name))
        self.tree_widget.selectionModel().clearSelection()
        self.last_selection_item = None

    def widget_selected(self):
        selection = self.tree_widget.selectedIndexes()
        if len(selection) != 1:
            return

        selection_item = self.update_selection(selection[0])
        if selection_item is None:
            return

        self.set_widget(selection_item.widget(self))
        self.message_handler.info("Changed to %s" % selection_item.name)

    def update_selection(self, index):
        selection_item = self.model.itemFromIndex(index)  # type: QItemPluginItem
        if not isinstance(selection_item, QItemPluginItem):
            return None
        if self.last_selection_item == selection_item:
            return None
        self.tree_widget.selectionModel().clearSelection()
        self.tree_widget.selectionModel().setCurrentIndex(index, QtCore.QItemSelectionModel.SelectCurrent)
        self.selection = selection_to_array(index)
        self.last_selection_item = selection_item

        return selection_item

    def restore_panels(self):
        with suppress(Exception):
            self.tree_widget.deleteLater()
        with suppress(Exception):
            self.tree_dock.deleteLater()
        with suppress(Exception):
            self.bottom_widget.deleteLater()
        with suppress(Exception):
            self.bottom_dock.deleteLater()
        self.bottom_widget = BottomWidget()
        self.bottom_dock = QtWidgets.QDockWidget("Info", self)
        self.bottom_dock.setObjectName("BottomDock")
        self.bottom_dock.setWidget(self.bottom_widget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottom_dock)
        self.message_handler = MessageHandler(self.bottom_widget.textBrowser)
        global recorder
        return recorder.set_message_handler(self.message_handler)

        # TODO on restore panels from view crashes here
        self.load_plugins()

        self.load_screens()
        self.tree_widget = QtWidgets.QTreeView()
        self.tree_widget.setModel(self.model)
        self.tree_widget.header().hide()
        self.tree_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # noinspection PyUnresolvedReferences
        self.tree_widget.clicked.connect(self.widget_selected)
        self.tree_dock = QtWidgets.QDockWidget("Screens", self)
        self.tree_dock.setObjectName("WidgetsDock")
        self.tree_dock.setWidget(self.tree_widget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.tree_dock)

    def load_plugins(self, plugins=None, package="plugins"):
        pass
        """
        PLugin Loading must be refactored to allow separation of plugins into separate packages
        
        import plugins as p
        import pkgutil
        import importlib
        importlib.import_module(package)
        
        loaded_plugin_names = []  # To store the names of loaded plugins

        if plugins is None:
           self.kill_tasks()

            n = self.load_plugins(pkgutil.iter_modules(p.__path__))
            self.message_handler.info("%s plugins loaded." % n)
            return
        n = 0
        for importer, module_name, is_pkg in plugins:
            if is_pkg:
                path = p.__path__[0]
                path = os.path.join(path, module_name)
                path = [path]
                loaded_plugin_names.append(package + "." + module_name)  # Store loaded plugin name

                n += self.load_plugins(pkgutil.iter_modules(path), package + "." + module_name)

            else:
                n += 1
                module_ = importlib.import_module(package + "." + module_name, package=package)
                loaded_plugin_names.append(package + "." + module_name)  # Store loaded plugin name
                try:
                    tasks = module_.BACKGROUND_TASKS
                except AttributeError:
                    tasks = []
                for Task in tasks:
                    self.background_tasks.append(Task(self))
                    
        # Print loaded plugin names and their order
        # for i, plugin_name in enumerate(loaded_plugin_names, 1):
        #    print(f"Loaded plugin {i}: {plugin_name}")
            
        return n
        """

    def load_screens(self):
        pass
        """
        This must be handled differently to allow for screens to be loaded from independent packages
        
        from . import screens
        import pkgutil

        model = self.model
        model.clear()

        for importer, module_name, is_pkg in pkgutil.iter_modules(screens.__path__):
            model.appendRow(self.module_to_item(importer, module_name, is_pkg, package="screens"))
        """

    def module_to_item(self, importer, module_name, is_package, package=__package__):
        import pkgutil
        import importlib
        # print(package)

        importlib.import_module(package)

        if not is_package:
            # print("Importing:")
            module_ = importlib.import_module(package + "." + module_name, package=package)
            # importer.find_module(module_name).load_module(module_name)

            try:
                widget = module_.MAIN_WIDGET
            except AttributeError:
                widget = EmptyWidget
            try:
                tasks = module_.BACKGROUND_TASKS
            except AttributeError:
                tasks = []
            for Task in tasks:
                self.background_tasks.append(Task(self))
            return QItemPluginItem(module_.SCREEN_NAME, widget=widget)

        item = QItemPluginFolder(module_name)

        path = os.path.join(os.path.dirname(__file__), package)
        path = os.path.join(path, module_name)
        path = [path]

        for importer, modname, is_pkg in pkgutil.iter_modules(path):
            item.appendRow(self.module_to_item(importer, modname, is_pkg, package=package + "." + module_name))
        return item

    def show(self):
        QtWidgets.QMainWindow.show(self)
        with suppress(AttributeError):
            if self.initialized:
                self.setWindowOpacity(1)


class QItemPluginFolder(QStandardItem):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.setIcon(QIcon(":/folder.svg"))
        self.name = name


class QItemPluginItem(QStandardItem):
    def __init__(self, name, widget, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.setIcon(QIcon(":/window.svg"))
        self.name = name
        self.widget = widget
