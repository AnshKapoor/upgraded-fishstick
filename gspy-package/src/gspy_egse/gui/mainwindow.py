import os
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon
from typing import *

import logging

logger = logging.getLogger(__name__)

from gspy_egse.gui.branding import *
from gspy_egse.gui.utils.misc import Extendable
from gspy_egse.gui.utils.widget import call_in_main_thread, event_name
from gspy_egse.gui.widgets.emptywidget import EmptyWidget
from gspy_egse.gui.widgets.bottomwidget import BottomWidget
from gspy_egse.gui.widgets.drophint import DropHint
from gspy_egse.gui.utils.widget import async_in_main_thread, ResizeListener, PaintListener
from gspy_egse.gui.utils.recorder import RecorderWindow, Recorder
from gspy_egse.gui.utils.externalRecorder import ExternalRecorderWindow

import importlib
import importlib.util
import importlib.resources
from importlib.resources import files, as_file  # stdlib, Python ≥3.9
from contextlib import suppress

from pathlib import Path

global recorder
recorder = Recorder()
MAIN_FILE_PATH = None


# Put your .ui files in: src/gspy_egse/gui/resources/  (must be a package with __init__.py)
pkg = "gspy_egse.gui.ui"
ui_name = "mainwindow.ui"

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
        logger.info("MessageHandler initialized with QTextBrowser.")

    def pre_scroll(self):
        try:
            scroll = self.box.verticalScrollBar()
        except (Exception,):
            return

        self._do_scroll = False
        if scroll.value() >= self._stale_max:
            self._do_scroll = True
        logger.debug(f"pre_scroll: do_scroll={self._do_scroll}, stale_max={self._stale_max}")

    def post_scroll(self):
        try:
            scroll = self.box.verticalScrollBar()
        except (Exception,):
            return
        logger.debug("post_scroll: QTextBrowser scrollbar not available.")

        if self._do_scroll:
            scroll.setValue(scroll.maximum())
        self._stale_max = scroll.maximum()
        logger.debug(f"post_scroll: scroll position set to {self._stale_max}")

    def a_add_lines(self):
        self.pre_scroll()
        while len(self.lines):
            line = self.lines[0]
            self.box.append(line)
            logger.info(f"MessageHandler added line")
            del self.lines[0]
        self.post_scroll()

    def warning(self, message):
        logger.warning(f"GUI Warning: {message}")
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:orange">[Warning]</span> %s</span>' % message,))

    def error(self, message):
        logger.error(f"GUI Error: {message}")
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:red   ">[Error]</span>   %s</span>' % message,))

    def info(self, message):
        logger.info(f"GUI Info: {message}")
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:blue  ">[Info]</span>    %s</span>' % message,))

    def success(self, message):
        logger.info(f"GUI Success: {message}")
        call_in_main_thread(self.box.append, (
            '<span style="white-space: pre"><span style="color:green ">[Success]</span> %s</span>' % message,))


def stacked_widget_set(stacked, widget):
    logger.debug(f"stacked_widget_set: Clearing {stacked.count()} widgets and adding {widget.__class__.__name__}")
    while stacked.count() > 0:
        stacked.removeWidget(stacked.currentWidget())
    stacked.addWidget(widget)
    widget.setParent(stacked)
    widget.show()
    logger.info(f"stacked_widget_set: New widget {widget.__class__.__name__} set successfully.")


def selection_to_array(sel: QtCore.QModelIndex) -> "[int]":
    if sel.parent().parent() == sel.parent():
        logger.debug(f"selection_to_array: Single-level selection")
        return [sel.row()]

    l = selection_to_array(sel.parent())
    l.append(sel.row())
    logger.debug(f"selection_to_array: Current selection path -> {l}")
    return l


class DetachedWindow(QtWidgets.QMainWindow):
    def __init__(self, window: "MyMainWindow", widget: QtWidgets.QWidget, selection, name, *args, **kwargs):
        logger.info(
            f"Creating DetachedWindow for widget {widget.__class__.__name__} with selection {selection} and name '{name}'")
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
        logger.debug("DetachedWindow shown on screen")
        if os.name == 'nt' or os.name == 'WINDOWS_NT':
            self.hide()
            self.show()
            logger.debug("DetachedWindow forced show() on Windows for proper rendering.")

        try:
            # noinspection PyUnresolvedReferences
            self.widget.handle_detach()
        except AttributeError:
            logger.debug("Widget %s does not implement handle_detach().", name, exc_info=True)
        except Exception:
            logger.exception("Unexpected error while detaching widget %s.", name)
        widget.show()
        self.initialized = True
        logger.info(f"DetachedWindow initialized for {name}.")

    def event(self, q_event: QtCore.QEvent):
        event_type = q_event.type()
        logger.debug(f"DetachedWindow event received: type={event_type}")
        p_e = QtCore.QEvent.Paint
        m_e = QtCore.QEvent.Move
        u_e = QtCore.QEvent.UpdateRequest
        c_e = QtCore.QEvent.Close
        z_o_c = QtCore.QEvent.ZOrderChange
        l_r = QtCore.QEvent.LayoutRequest

        if not self.initialized or q_event.type() in [216, p_e, u_e, z_o_c, l_r]:
            return QtWidgets.QMainWindow.event(self, q_event)
        if q_event.type() == c_e:
            logger.info("DetachedWindow close event triggered.")
            self.initialized = False
            if self.widget is not None:
                if not self.saved:
                    try:
                        self.widget.delete_settings()
                    except AttributeError:
                        logger.debug("Widget %s does not implement delete_settings().", self.name, exc_info=True)
                    except Exception:
                        logger.exception("Unexpected error while deleting settings for widget %s.", self.name)
                self.widget.deleteLater()
                self.widget = None
            if self.main_window is not None:
                self.main_window.windows.remove(self)
                self.main_window = None
                logger.debug("DetachedWindow cleanup completed after close event.")
            return QtWidgets.QMainWindow.event(self, q_event)
        if not self.dragging and self.last_event == m_e and q_event.type() == m_e:
            if self.main_window.isVisible() and not self.main_window.isMinimized():
                logger.debug("DetachedWindow starting drag with drop hint fade-in.")
                self.main_window.drop_hint.fade_in()
                self.dragging = True
                self.main_window.raise_()
        elif self.dragging and q_event.type() != m_e:
            logger.debug("DetachedWindow drag finished; checking reattach.")
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
        logger.info(f"Reattaching DetachedWindow widget {self.name} to main window.")
        self.initialized = False
        if self.main_window is not None:
            self.main_window.set_widget(self.widget)
            self.main_window.restore_selection(self.selection, check_name=self.name)
            self.main_window.windows.remove(self)
            self.initialized = False
            self.main_window = None

        try:
            self.widget.handle_reattach()
        except AttributeError:
            logger.debug("Widget %s does not implement handle_reattach().", self.name, exc_info=True)
        except Exception:
            logger.exception("Unexpected error while reattaching widget %s.", self.name)

        self.widget = None
        self.deleteLater()
        logger.debug(f"DetachedWindow for {self.name} successfully reattached and deleted.")

    def to_variant(self):
        logger.debug(f"Saving DetachedWindow state for widget.")
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
        self.external_recorder_window = None # For the external window
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
        # Track widgets that require a working transport layer (serial/SpaceWire).
        self._transport_controls: List[QtCore.QObject] = []
        # Remember the last reported connection state so restore_panels can reapply it.
        self._transport_connected: bool = True
        self.setCorner(QtCore.Qt.BottomLeftCorner, QtCore.Qt.LeftDockWidgetArea)

        ui_res = files(pkg).joinpath(ui_name)
        with as_file(ui_res) as ui_path:
            self.ui = uic.loadUi(str(ui_path), self)

        # self.ui = uic.loadUi("src/gspy_egse/gui/ui/mainwindow.ui", self)
        
        self.setWindowTitle(PRODUCT)
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.set_widget(EmptyWidget())
        self.restore_panels()
        self.actionRestore_Panels.triggered.connect(self.restore_panels)
        self.actionDetach.triggered.connect(self.detach_screen)
        self.actionRecorder.triggered.connect(self.show_recorder)
        self.actionExternalRecorder.triggered.connect(self.show_external_recorder)

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

    def _open_external_recorder(self) -> None:
        """Show the External Recorder popup when the main window starts."""
        self.external_recorder_window = ExternalRecorderWindow()

    def show_recorder(self):
        try:
            self.record_window.show()
            self.record_window.raise_()
        except (Exception,):
            self.record_window = RecorderWindow()
            self.record_window.show()
            self.record_window.raise_()

    def show_external_recorder(self) -> None:
        if self.external_recorder_window is None:
            self.external_recorder_window = ExternalRecorderWindow()
            self.external_recorder_window.destroyed.connect(
                lambda: setattr(self, "external_recorder_window", None)
            )
        self.external_recorder_window.show()
        self.external_recorder_window.raise_()
        self.external_recorder_window.activateWindow()
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
            try:
                self.restore_selection(selection, check_name=settings.value("selection_name"), set_widget=True)
                # self.restoreState(settings.value("windowState"))
            except Exception:
                logger.exception("Failed to restore selection from saved settings.")
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
            try:
                t.close()
            except AttributeError:
                logger.debug("Background task %r does not implement close().", t, exc_info=True)
            except Exception:
                logger.exception("Failed to close background task %r.", t)
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

    def _safe_delete(self, attribute_name: str) -> None:
        """Safely schedule deletion of a widget-like attribute if it exists.

        Args:
            attribute_name (str): Name of the attribute referencing the widget to delete.

        Returns:
            None
        """

        # Retrieve the attribute from the instance; it might not exist yet.
        widget: Optional[QtCore.QObject] = getattr(self, attribute_name, None)
        if widget is None:
            logger.debug("%s not available during restore_panels.", attribute_name)
            return

        try:
            widget.deleteLater()
            # Explicitly reset the attribute so future calls know it is gone.
            setattr(self, attribute_name, None)
        except Exception:
            logger.exception("Failed to delete %s during restore_panels.", attribute_name)

    def restore_panels(self, checked: Optional[bool] = None) -> None:
        """Recreate dock and tree panels while safely cleaning existing widgets.

        Args:
            checked (Optional[bool]): Optional Qt check state when triggered from an action.

        Returns:
            None
        """

        logging.debug('Restore panels function. \n')

        # The ``checked`` flag is unused but preserved to stay compatible with QAction.
        _ = checked

        # Proactively dispose of old widgets while handling missing attributes gracefully.
        self._safe_delete("tree_widget")
        self._safe_delete("tree_dock")
        self._safe_delete("bottom_widget")
        self._safe_delete("bottom_dock")

        # Instantiate fresh bottom panel components for status and messaging features.
        self.bottom_widget = BottomWidget()
        self.bottom_dock = QtWidgets.QDockWidget("Info", self)
        self.bottom_dock.setObjectName("BottomDock")
        self.bottom_dock.setWidget(self.bottom_widget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottom_dock)
        self.message_handler = MessageHandler(self.bottom_widget.textBrowser)

        global recorder
        recorder.set_message_handler(self.message_handler)

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
        # Register the widgets whose enabled state should follow the connection availability.
        self._transport_controls = [
            self.stackedWidget,
            self.tree_widget,
            getattr(self.bottom_widget, "consoleWidget", self.bottom_widget),
        ]
        self._set_connected_ui(self._transport_connected)

    def _set_connected_ui(self, connected: bool) -> None:
        """Toggle transport-dependent controls and surface the connection state."""

        # Persist the state so the next restore_panels call reapplies it immediately.
        self._transport_connected = connected
        status_text: str = (
            "Transport link established."
            if connected
            else "Transport unavailable – waiting for hardware connection."
        )
        try:
            # Keep users informed via the native status bar.
            self.statusBar().showMessage(status_text)
        except Exception:
            logger.debug("Failed to update status bar text for connection state.", exc_info=True)

        for control in self._transport_controls:
            if control is None:
                continue
            try:
                control.setEnabled(connected)
            except Exception:
                logger.debug("Transport control %r lacks setEnabled; skipping.", control, exc_info=True)

    def load_plugins(self, plugin_path: Optional[str] = None, package: str = "gspy_egse.gui.plugins") -> int:
        """Load plugin modules and initialise their background tasks.

        The method safeguards against hardware plugins whose serial connections fail by
        skipping their polling setup until a connection is available.
        Transport-dependent UI elements are updated based on the aggregated connection state
        to prevent accidental command execution while disconnected.

        Args:
            plugin_path: Optional filesystem path that overrides the default search location.
            package: Import path of the plugin package to load.

        Returns:
            The number of plugin modules successfully imported.
        """
        import importlib
        import importlib.resources
        import logging
        import types

        loaded_plugin_names = []
        n = 0

        logging.debug(f"[Load plugins] Loading plugins from package: {package}")
        try:
            base_path = importlib.resources.files(importlib.import_module(package))
            logging.debug(f"[Load plugins] Resolved path: {base_path}")
        except Exception as e:
            logging.error(f"[Load plugins] Could not resolve package path: {e}")
            return 0

        def walk_modules(current_path, current_package):
            for entry in current_path.iterdir():
                if entry.is_dir():
                    # Recurse into subpackage
                    sub_package = f"{current_package}.{entry.name}"
                    yield from walk_modules(entry, sub_package)
                elif entry.name.endswith(".py") and not entry.name.startswith("_"):
                    module_name = entry.name[:-3]  # strip .py
                    full_module_name = f"{current_package}.{module_name}"
                    yield full_module_name

        transport_connected: bool = True

        for full_module_name in walk_modules(base_path, package):
            logging.debug(f"[Load plugins] Attempting to import: {full_module_name}")
            try:
                mod = importlib.import_module(full_module_name)
                loaded_plugin_names.append(full_module_name)
                n += 1

                tasks = getattr(mod, "BACKGROUND_TASKS", [])
                for Task in tasks:
                    task_instance = Task(self)
                    hardware = getattr(task_instance, "hardware", None)
                    is_connected = getattr(hardware, "is_connected", None)
                    if callable(is_connected) and not is_connected():
                        transport_connected = False
                        logging.warning(
                            "[Load plugins] %s hardware not connected; skipping polling and UI activation.",
                            full_module_name,
                        )
                        if self.message_handler is not None:
                            self.message_handler.warning(
                                f"{full_module_name} connection unavailable. Controls remain disabled until a port is configured."
                            )
                        if hasattr(task_instance, "hardware") and hasattr(task_instance.hardware, "stop_polling"):
                            with suppress(Exception):
                                task_instance.hardware.stop_polling()
                        continue
                    self.background_tasks.append(task_instance)
            except Exception as e:
                logging.warning(f"[Load plugins] Failed to import plugin {full_module_name}: {e}")

        self._set_connected_ui(transport_connected)
        logging.info(f"[Load plugins] {n} plugins loaded: {loaded_plugin_names}")
        return n

    def load_screens(self):
        """
        Dynamically loads screen modules and subpackages from the 'screens' subpackage.
        """
        import gspy_egse.gui.screens as screens
        import importlib.resources
        import importlib
        import logging

        logging.debug("[load_screens] Starting to load screens...\n")

        model = self.model
        model.clear()

        try:
            screens_path = importlib.resources.files(screens)
            logging.debug(f"[load_screens] Resolved path to screens: {screens_path}")
        except Exception:
            logging.exception("[load_screens] Failed to resolve screens package")
            return

        for entry in screens_path.iterdir():
            logging.debug(f"[load_screens] Found entry: {entry.name}")

            if entry.name.startswith("_"):
                logging.debug(f"[load_screens] Skipping: {entry.name}")
                continue

            module_name = entry.stem
            full_module_name = f"{screens.__name__}.{module_name}"

            if entry.is_file() and entry.name.endswith(".py"):
                is_package = False
            elif entry.is_dir() and (entry / "__init__.py").exists():
                is_package = True
            else:
                logging.debug(f"[load_screens] Ignoring non-module entry: {entry.name}")
                continue

            logging.debug(f"[load_screens] Attempting to import: {full_module_name} (is_package={is_package})")

            try:
                importlib.import_module(full_module_name)
                item = self.module_to_item(module_name, is_package, package=screens.__name__)
                model.appendRow(item)
                logging.info(f"[load_screens] Successfully loaded: {full_module_name}")
            except Exception:
                logging.exception(f"[load_screens] Failed to import {full_module_name}")

        logging.info("[load_screens] Finished loading screens.")

    def module_to_item(self, module_name, is_package, package):
        """
        Loads a screen module or package and returns a QItemPluginItem or QItemPluginFolder.
        """
        import importlib
        import pkgutil
        import logging

        full_module_name = f"{package}.{module_name}"

        if not is_package:
            try:
                module_ = importlib.import_module(full_module_name)
            except Exception:
                logging.exception(f"[module_to_item] Failed to import module {full_module_name}")
                return QItemPluginItem(module_name + " (broken)", widget=EmptyWidget)

            widget = getattr(module_, "MAIN_WIDGET", EmptyWidget)
            tasks = getattr(module_, "BACKGROUND_TASKS", [])
            for Task in tasks:
                try:
                    self.background_tasks.append(Task(self))
                    logging.debug(f"[module_to_item] Added background task: {Task}")
                except Exception:
                    logging.exception(f"[module_to_item] Failed to instantiate task: {Task}")

            screen_name = getattr(module_, "SCREEN_NAME", module_name)
            return QItemPluginItem(screen_name, widget=widget)

        # Handle subpackage (directory with __init__.py)
        try:
            pkg = importlib.import_module(full_module_name)
            path = pkg.__path__  # this must exist if it's a package
        except Exception:
            logging.exception(f"[module_to_item] Failed to load subpackage: {full_module_name}")
            return QItemPluginFolder(module_name + " (broken)")

        folder_item = QItemPluginFolder(module_name)
        for importer, modname, is_subpkg in pkgutil.iter_modules(path):
            child_item = self.module_to_item(modname, is_subpkg, package=full_module_name)
            folder_item.appendRow(child_item)

        return folder_item

    def show(self):
        QtWidgets.QMainWindow.show(self)
        try:
            if self.initialized:
                self.setWindowOpacity(1)
        except AttributeError:
            logger.debug("Window opacity attribute not available on this platform.", exc_info=True)
        except Exception:
            logger.exception("Failed to update window opacity after showing main window.")


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
