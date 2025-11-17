from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import logging
import pyqtgraph as pg
from functools import wraps
import threading
from typing import *

from gspy_egse.gui.utils.plugin import ObjectWithSettings, Setting
from gspy_egse.gui.utils.recorder import Recordable


logger = logging.getLogger(__name__)

def event_name(number: int) -> str:
    try:
        for name in dir(QEvent):
            e = QEvent(number)
            if QEvent.__getattribute__(e, name) == number:
                return "%s (%d)" % (name, number)
        return str(number)
    except:
        import traceback
        traceback.print_exc()


def mix_color(c1: QColor, c2: QColor, percentage=.5):
    p = percentage
    q = 1 - percentage

    r = QColor(*(v * 255 for v in (int(c1.redF() * p + c2.redF() * q),
                                   int(c1.greenF() * p + c2.greenF() * q),
                                   int(c1.blueF() * p + c2.blueF() * q),
                                   int(c1.alphaF() * p + c2.alphaF() * q)
                                   )))
    return r


class FloatProgress(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value_f = self.value()
        self.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self, _):
        self.setFormat('%.02f%%' % self._value_f)

    def setValue(self, value):
        self._value_f = value
        QProgressBar.setValue(self, int(value))


class SwitchBoard(QWidget, Recordable):
    def __init__(self, *args, instance_name=None, value=0, names: Optional[List[str]] = None,
                 listener: Optional[Callable[[int, int], None]] = None, **kwargs):
        self.has_name = instance_name is not None
        super().__init__(*args, singleton=False, register=self.has_name, instance_name=instance_name,
                         **kwargs)
        self.names = names if names is not None else []
        self.switches: List[Switch] = []
        self.listener = listener
        self.value = value
        self.reconstruct()

    def set_value(self, value):
        self.value = value
        mask = 1 << len(self.names)
        for s in self.switches:
            mask >>= 1
            if s is not None:
                call_in_main_thread(s.switch_to, (self.value & mask > 0,))

    def set_names(self, names: Optional[List[str]], name: Optional[str] = None):
        if not self.has_name and name is not None:
            self.has_name = True
            self.instance_name = name
            self.recorder_register()
        self.names = names
        self.reconstruct()

    def set_listener(self, listener: Callable[[int, int], None]):
        self.listener = listener

    @pyqtSlot()
    def call_listener(self):
        if self.listener is None:
            return

        v = 0
        m = 0
        n = 0
        for s in self.switches:
            v <<= 1
            m <<= 1
            if s is not None and s.is_on:
                v += 1
            if s == self.sender():
                m += 1
                if self.has_name:
                    self.set_switch(n, s.is_on)
            n += 1
        self.value = v
        self.listener(v, m)

    @Recordable.record_method()
    def set_switch(self, index: int, state: bool, play_back=False):
        if not play_back:
            return
        self.switches[index].switch_to(state, True)

    def reconstruct(self):
        call_in_main_thread(self._reconstruct)

    def _reconstruct(self):
        l = self.layout()
        if l is not None:
            for i in reversed(range(l.count())):
                l.itemAt(i).widget().deleteLater()
        else:
            l = QFormLayout(self)
            self.setLayout(l)
        self.switches = []
        mask = 1 << len(self.names)
        for n in self.names:
            mask >>= 1
            if n != "_" and n != "":
                s = Switch(self, switch=(self.value & mask > 0))
                s.clicked.connect(self.call_listener)

                layout = QHBoxLayout()
                layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))
                layout.addWidget(s)
                self.switches.append(s)
                l.addRow(n, layout)
            else:
                self.switches.append(None)


class Switch(QAbstractButton):
    clicked = pyqtSignal()

    def __init__(self, *args, height=22, opacity=0., switch=False, margin=None, on_color="#009688",
                 off_color="#858585", dpi_scale_values=True, timeout=1500, **kwargs):
        super().__init__(*args, **kwargs)
        if margin is None:
            margin = height * 4 // 22
        if dpi_scale_values:
            height *= self.logicalDpiX() / 96.0
            margin *= self.logicalDpiX() / 96.0
        self._h = height
        self._opacity = opacity
        self._switch = switch
        self._margin = margin
        self._timeout = timeout
        self._wait_timeout = False
        self._pending_value = False
        self._offset = 0. if not switch else self.width() - self.height()
        self._thumb = QColor(off_color)
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._brush = QColor(on_color)
        self.setFixedWidth(int(self.width()))
        self.setFixedHeight(int(self.height()))

    @property
    def is_on(self) -> bool:
        return self._switch

    @pyqtProperty(float)
    def offset(self) -> float:
        return self._offset

    @offset.setter
    def offset(self, offset: float):
        self._offset = offset
        self.update()

    def paintEvent(self, e: QPaintEvent):
        p = QPainter(self)
        p.setPen(Qt.NoPen)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setOpacity(1.)
        if not self.isEnabled():
            p.setOpacity(.7)

        m = self._margin
        o = self._offset
        h = self.height()
        w = self.width()

        bkg = mix_color(self._thumb, QColor("#FFF"), .34)
        p.setBrush(mix_color(self._brush, bkg, .3))

        p.drawRoundedRect(QRectF(m, m, o + h - m * 2, h - m * 2), h / 2 - m, h / 2 - m)

        p.setBrush(bkg)
        p.drawRoundedRect(QRectF(o + m, m, w - m * 2 - o, h - m * 2), h / 2 - m, h / 2 - m)

        p.setBrush(self._brush if self._switch else self._thumb)
        p.drawEllipse(QRectF(o, 0., h, h))

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() & Qt.LeftButton:
            self.start_timeout()
            self.toggle_switch()
            self.clicked.emit()

        QAbstractButton.mouseReleaseEvent(self, e)

    def start_timeout(self):
        if self._timeout > 0:
            self._wait_timeout = True
            self.setEnabled(False)
            delay_in_main_thread(self._timeout, self.end_timeout)

    def end_timeout(self):
        if not self._wait_timeout:
            return
        self._wait_timeout = False
        self.setEnabled(True)
        if self._pending_value:
            self._pending_value = False
            self.toggle_switch()

    def switch_to(self, state, with_timeout=False):
        if self._switch == state:
            if self._wait_timeout:
                self._pending_value = False
                self.end_timeout()
            return
        if self._wait_timeout:
            self._pending_value = True
            return

        if with_timeout:
            self.start_timeout()
        self.toggle_switch()

    def toggle_switch(self):
        self._switch = not self._switch
        self._anim.setStartValue(self._offset)
        if self._switch:
            self._anim.setEndValue(self.width() - self.height())
        else:
            self._anim.setEndValue(0.)
        self._anim.setDuration(120)
        self._anim.start()

    def switch_on(self):
        self.switch_to(True)

    def switch_off(self):
        self.switch_to(False)

    def enterEvent(self, e: QEvent):
        self.setCursor(Qt.PointingHandCursor)
        QAbstractButton.enterEvent(self, e)

    def width(self):
        return self._h * 2

    def height(self):
        return self._h


class ActivationListener(QObject):
    def __init__(self, widget: QWidget, listener: callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widget
        self.listener = listener
        self.last_event = None
        widget.installEventFilter(self)

    def eventFilter(self, source: QObject, event: QEvent):
        if source is self.widget and (event.type() == QEvent.MouseButtonPress and self.last_event not in [
            QEvent.InputMethodQuery
        ] or (event.type() == QEvent.FocusIn and self.last_event not in [
            QEvent.FocusIn,
            QEvent.WindowActivate
        ])):
            self.last_event = event.type()
            self.listener()
        else:
            self.last_event = event.type()
        return QObject.eventFilter(self, source, event)


class GenericListener(QObject):
    def __init__(self, widget: QWidget, listener: callable, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widget
        self.listener = listener
        self.last_event = None
        self._event = event
        widget.installEventFilter(self)

    def eventFilter(self, source: QObject, event: QEvent):
        if source is self.widget and event.type() == self._event:
            self.listener()

        return QObject.eventFilter(self, source, event)


class PaintListener(GenericListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, event=QEvent.Paint, **kwargs)


class ResizeListener(GenericListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, event=QEvent.Resize, **kwargs)


def select_file(listener: Callable[[str], None], path: Union[str, Callable[[], str]] = ".",
                type_filter: Optional[str] = None, create_new: bool = False):
    if callable(path):
        path = path()
    async_in_main_thread(_select_file, args=(listener, path, type_filter, create_new))


def _select_file(listener: Callable[[str], None], path=".", type_filter=None, create_new=False):
    call = QFileDialog.getSaveFileName if create_new else QFileDialog.getOpenFileName

    f, _ = call(None, 'Open file', str(path), "Files (*)" if type_filter is None else type_filter)
    if f != '':
        listener(f)


class _PyQtObject(QObject):
    my_signal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_list = []
        self.my_signal.connect(self.my_slot)

    @pyqtSlot()
    def my_slot(self):
        my_list = self.my_list
        self.my_list = []
        for func, args, kwargs in my_list:
            try:
                if kwargs is not None:
                    if args is not None:
                        func(*args, **kwargs)
                    else:
                        func(**kwargs)
                elif args is not None:
                    func(*args)
                else:
                    func()
            except (Exception,):
                import traceback
                traceback.print_exc()

    def call_in_main_thread(self, func: callable, args: tuple = None, kwargs: dict = None):
        self.my_list.append((func, args, kwargs))
        self.my_signal.emit()


_py_qt_object = _PyQtObject()


def call_in_main_thread(func: callable, args: tuple = None, kwargs: dict = None):
    _py_qt_object.call_in_main_thread(func, args, kwargs)


def async_in_main_thread(func: callable, args: tuple = None, kwargs: dict = None):
    threading.Thread(target=lambda: call_in_main_thread(func, args=args, kwargs=kwargs)).start()


def delay_in_main_thread(time, func: callable, args: tuple = None, kwargs: dict = None):
    t = QTimer(_py_qt_object)
    t.timeout.connect(lambda: call_in_main_thread(func, args=args, kwargs=kwargs))
    t.setSingleShot(True)
    t.start(time)


def expand_widget(widget: (QWidget, QSpacerItem)):
    if isinstance(widget, QSpacerItem):
        assert isinstance(widget, QSpacerItem)
        widget.changeSize(
            10000,
            10000,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
    else:
        widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
    return widget


def expand_rect(rect, offset_x, offset_y=0):
    offset_y = offset_x if offset_y == 0 else offset_y
    if isinstance(rect, QRectF):
        point = QPointF
    else:
        point = QPoint
    if isinstance(offset_x, QPoint) or isinstance(offset_x, QPointF):
        point = point(offset_x)
    else:
        point = point(offset_x, offset_y)

    rect.setTopLeft(rect.topLeft() - point)
    rect.setBottomRight(rect.bottomRight() + point)

    return rect


def shrink_rect(rect, offset_x, offset_y=0):
    return expand_rect(rect, -offset_x, -offset_y)


def re_plot(plot: pg.PlotWidget, *args, **kwargs):
    plot_item = plot.getPlotItem()
    if len(plot_item.listDataItems()) > 0:
        plot_item.listDataItems()[0].setData(*args, **kwargs)
    else:
        plot_item.plot(*args, **kwargs)
    plot.viewport().update()


class Splitter(QSplitter):
    H = 0
    V = 1

    @staticmethod
    def shrink_right(widget: Union[QWidget, QLayout], margin: int = 2) -> None:
        """Reduce a widget's right margin while logging a clean message on failure."""

        try:
            layout = widget.layout()
            if layout and layout != widget:
                # Recurse into layouts so nested widgets inherit the adjustment.
                Splitter.shrink_right(layout, margin)
                margin = 0
            if not hasattr(widget, "getContentsMargins") or not hasattr(widget, "setContentsMargins"):
                logger.debug("Widget %r is missing contents margin accessors; skipping shrink_right.", widget)
                return
            l, t, r, b = widget.getContentsMargins()
            widget.setContentsMargins(int(l), int(t), int(margin), int(b))
        except Exception:
            logger.exception("Failed to shrink right for widget %r.", widget)

    @staticmethod
    def shrink_left(widget: Union[QWidget, QLayout], margin: int = 2) -> None:
        """Reduce a widget's left margin while keeping log noise to a minimum."""

        try:
            layout = widget.layout()
            if layout and layout != widget:
                # Recurse into layouts so nested widgets inherit the adjustment.
                Splitter.shrink_left(layout, margin)
                margin = 0
            if not hasattr(widget, "getContentsMargins") or not hasattr(widget, "setContentsMargins"):
                logger.debug("Widget %r is missing contents margin accessors; skipping shrink_left.", widget)
                return
            l, t, r, b = widget.getContentsMargins()
            widget.setContentsMargins(int(margin), int(t), int(r), int(b))
        except Exception:
            logger.exception("Failed to shrink left for widget %r.", widget)

    def resizeEvent(self, q_resize_event):
        QSplitter.resizeEvent(self, q_resize_event)
        self.setStyleSheet(self.cus_style.replace("percentage_", str(self.height() * .35)))

    def __init__(self, *args, orientation=H, shrink=True, **kwargs):
        super().__init__(Qt.Horizontal if orientation == Splitter.H else Qt.Vertical, *args, **kwargs)
        self.shrink = shrink
        self.dpi_scale = self.logicalDpiX() / 96.0
        self.cus_style = "QSplitter.handle:horizontal {" \
                         "  border: 1px ridge #777;" \
                         "  border-width: 0px %(s).1fpx;" \
                         "  min-height: %(s00).1fpx;" \
                         "  max-height: %(s00).1fpx;" \
                         "  margin: percentage_px %(s).1fpx;" \
                         "  opacity: .1;" \
                         "}" % {'s': 2 * self.dpi_scale, 's00': 200 * self.dpi_scale}
        self.setStyleSheet(self.cus_style.replace("percentage_", str(self.height() * .35)))
        self.setHandleWidth(11 * int(self.dpi_scale))
        expand_widget(self)

    @property
    def identifier(self):
        ids = []
        for i in reversed(range(self.count())):
            try:
                ids.append(self.widget(i).identifier)
            except AttributeError:
                widget = self.widget(i)
                logger.debug("Widget %r does not expose an identifier.", widget, exc_info=True)
            except Exception:
                widget = self.widget(i)
                logger.exception("Failed to read identifier for widget %r.", widget)
        return ";".join(reversed(ids))

    def addWidget(self, *args):
        r = QSplitter.addWidget(self, *args)

        if not self.shrink:
            return r
        if self.count() > 1:
            Splitter.shrink_right(self.widget(self.count() - 2))
            Splitter.shrink_left(self.widget(self.count() - 1))
        return r

    def delete_settings(self):
        for i in range(self.count()):
            widget = self.widget(i)
            try:
                widget.delete_settings()
            except AttributeError:
                logger.debug("Widget %r does not implement delete_settings().", widget, exc_info=True)
            except Exception:
                logger.exception("Failed to delete settings for widget %r.", widget)

    # noinspection PyPep8Naming
    def deleteLater(self):
        for i in range(self.count()):
            widget = self.widget(i)
            try:
                widget.deleteLater()
            except AttributeError:
                logger.debug("Widget %r does not implement deleteLater().", widget, exc_info=True)
            except Exception:
                logger.exception("Failed to call deleteLater on widget %r.", widget)
        QSplitter.deleteLater(self)

    def handle_detach(self, cls=None):
        for i in range(self.count()):
            widget = self.widget(i)
            try:
                widget.handle_detach(cls=cls)
            except AttributeError:
                logger.debug("Widget %r does not implement handle_detach().", widget, exc_info=True)
            except Exception:
                logger.exception("Failed to handle_detach for widget %r.", widget)

    def handle_reattach(self, cls=None):
        for i in range(self.count()):
            widget = self.widget(i)
            try:
                widget.handle_reattach(cls=cls)
            except AttributeError:
                logger.debug("Widget %r does not implement handle_reattach().", widget, exc_info=True)
            except Exception:
                logger.exception("Failed to handle_reattach for widget %r.", widget)


class SplitterWithSettings(Splitter):
    def __init__(self, obj: ObjectWithSettings, *args, name=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Splitter_%s_pos" % str(name)

        self.object = obj
        self.sizes_ = None
        self.ignore_movement = True
        self.update_after_resize = True
        try:
            identifier = obj.identifier
        except AttributeError:
            identifier = None
        self.setting = obj.add_setting(
            unique=True,
            name=self.name,
            default=.5,
            in_settings=False,
            min_=0,
            max_=1,
            step=.01,
            type_=Setting.FLOAT,
            listener=self.set,
            widget_id=identifier
        )
        self.splitterMoved.connect(self.listener)
        self.ignore_movement = False

    def resizeEvent(self, q_resize_event):
        Splitter.resizeEvent(self, q_resize_event)
        if self.update_after_resize:
            self.update_after_resize = False
            self.update_sizes()

    @pyqtSlot(int, int)
    def listener(self, pos, *_):
        if self.ignore_movement:
            return
        width = self.width() - self.handleWidth()
        self.setting.set(pos / width)

    def set(self, value, init=True, **_):
        if init:
            self.update_after_resize = True
        self.sizes_ = [value, 1 - value]
        self.update_sizes()

    def addWidget(self, *args):
        Splitter.addWidget(self, *args)
        self.update_sizes()
        self.update_after_resize = True

    def update_sizes(self):
        if self.sizes_ is None:
            return
        self.ignore_movement = True
        sizes_as_int = [int(s * self.width()) for s in self.sizes_]
        self.setSizes(sizes_as_int)
        self.ignore_movement = False


class CusIcon(QIcon):
    def paint(self, q_painter, *__args):
        print(q_painter.device().width())
        return QIcon.paint(self, q_painter, *__args)

    def pixmap(self, *__args):
        print(__args)
        return QIcon.paint(self, *__args)
