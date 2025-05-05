from PyQt6 import QtCore, QtWidgets, QtGui, uic
from gspy.gui.utils.widget import expand_rect, shrink_rect


class DropHint(QtWidgets.QWidget):
    def __init__(self, *args):
        self._animation_factor = 0.0
        self.animation = None
        self.mouse_pos = None
        self.mouse_inside = False
        self.was_hidden = False
        QtWidgets.QWidget.__init__(self, *args)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.dpi_scale = self.logicalDpiX() / 96.0
        self.ui = uic.loadUi("src/gspy/gui/ui/drophint.ui", self)
        self.blue = QtGui.QColor(80, 80, 255, 128)

        self.label_icon.setText(chr(0xf2d2))
        f = QtGui.QFont("FontAwesome_new", 32)
        f.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.label_icon.setFont(f)
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(2)
        effect.setColor(QtGui.QColor(0, 0, 0, 100))
        effect.setOffset(2, 2)
        self.label_icon.setGraphicsEffect(effect)
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(2)
        effect.setColor(QtGui.QColor(0, 0, 0, 100))
        effect.setOffset(2, 2)
        self.label.setGraphicsEffect(effect)


    @QtCore.pyqtProperty(float)
    def animation_factor(self):
        return self._animation_factor

    @animation_factor.setter
    def animation_factor(self, value):
        if value != 0.0 and value != 1.0 and abs(self._animation_factor - value) < .01:  # prevents some lag
            return
        self._animation_factor = value
        self.update()

    def paintEvent(self, q_paint_event):
        if self._animation_factor < 0.01:
            self.label.hide()
            self.label_icon.hide()
            self.was_hidden = True
            return QtWidgets.QWidget.paintEvent(self, q_paint_event)
        if self.was_hidden:
            self.was_hidden = False
            self.label.show()
            self.label_icon.show()

        off = 20 * self.dpi_scale

        fac = max(self._animation_factor * 1.5, 0)
        fac = min(fac, 1)
        self.blue.setAlphaF(fac / 2)
        self.label.setStyleSheet("color: rgba(255,255,255,%f);" % fac)
        self.label_icon.setStyleSheet("color: rgba(255,255,255,%f);" % fac)
        p = QtGui.QPainter(self)
        # p.setRenderHint(QtGui.QPainter.Antialiasing)
        path = QtGui.QPainterPath()

        r1 = QtCore.QRect(self.childrenRect())  # type: QtCore.QRect
        r1 = expand_rect(r1, r1.topLeft() / 2)
        r2 = expand_rect(QtCore.QRectF(r1), off)
        r2 = shrink_rect(r2, (r2.bottomRight() - r2.topLeft()) / 2 * (1 - self._animation_factor))
        path.addRoundedRect(r2, 20 * self.dpi_scale, 20 * self.dpi_scale)
        p.fillPath(path, self.blue)

        r_global = QtCore.QRect(r1)  # type: QtCore.QRect
        r_global.setBottomRight(self.mapToGlobal(r_global.bottomRight()))
        r_global.setTopLeft(self.mapToGlobal(r_global.topLeft()))

        self.mouse_inside = self.mouse_pos is not None and r_global.contains(self.mouse_pos)
        if self.mouse_inside:
            p.fillRect(r1, QtGui.QColor(255, 255, 255, 75))
        #b = QtGui.QBackingStore
        #b.endPaint() TODO check what this does
        return QtWidgets.QWidget.paintEvent(self, q_paint_event)

    def fade_in(self):
        a = self.animation = QtCore.QPropertyAnimation(self, b"animation_factor")
        a.setDuration(500)
        a.setStartValue(self._animation_factor)
        a.setEndValue(1.0)
        a.setEasingCurve(QtCore.QEasingCurve.OutBounce)
        a.start()

    def fade_out(self):
        self.mouse_pos = None
        a = self.animation = QtCore.QPropertyAnimation(self, b"animation_factor")
        a.setDuration(100)
        a.setStartValue(self._animation_factor)
        a.setEndValue(0.0)
        a.start()

    def set_mouse_pos(self, pos):
        self.mouse_pos = pos
        self.update()

    @property
    def animation_finished(self):
        return self.animation is not None and not self.animation.state() == QtCore.QAbstractAnimation.Running
