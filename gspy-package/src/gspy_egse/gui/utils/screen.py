from contextlib import suppress
from PyQt6 import QtWidgets, QtCore

from .widget import SplitterWithSettings
from .plugin import WidgetWithSettings


def _init(cls, window, *args, **kwargs):
    cls(window, *args, **kwargs)


class DoubleScreen(QtWidgets.QWidget):
    def __init__(self, cls, window, identifier="DoubleWidget1;DoubleWidget2",
                 args1=None, args2=None, kwargs1=dict, kwargs2=dict):
        try:
            QtWidgets.QWidget.__init__(self)

            self.identifier = identifier
            identifier = identifier.split(";")
            l = QtWidgets.QHBoxLayout(self)
            self.setLayout(l)

            self.w1_is_initialized = False
            self.w2_is_initialized = False
            kwargs1['identifier'] = identifier[0]
            kwargs2['identifier'] = identifier[1]
            if args1 is not None:
                self.w1 = cls(window, *args1, **kwargs1)
            else:
                self.w1 = cls(window, **kwargs1)
            assert isinstance(self.w1, WidgetWithSettings)
            if args2 is not None:
                self.w2 = cls(window, *args2, **kwargs2)
            else:
                self.w2 = cls(window, **kwargs2)
            assert isinstance(self.w2, WidgetWithSettings)
            self.w1.add_init_complete_listener(self.w1_initialized)
            self.w2.add_init_complete_listener(self.w2_initialized)


        except (Exception,):
            import traceback
            traceback.print_exc()

    def display_widgets(self):
        s = SplitterWithSettings(self.w1, name="Double")
        s.addWidget(self.w1)
        s.addWidget(self.w2)
        self.layout().addWidget(s)

    def w1_initialized(self):
        if self.w2_is_initialized:
            self.display_widgets()
        self.w1_is_initialized = True

    def w2_initialized(self):
        if self.w1_is_initialized:
            self.display_widgets()
        self.w2_is_initialized = True

    def delete_settings(self):
        for i in reversed(range(self.layout().count())):
            with suppress(AttributeError):
                self.layout().itemAt(i).widget().delete_settings()

    # noinspection PyPep8Naming
    def deleteLater(self):
        for i in reversed(range(self.layout().count())):
            try:
                self.layout().itemAt(i).widget().deleteLater()
            except:
                import traceback
                traceback.print_exc()
        QtWidgets.QWidget.deleteLater(self)

    def handle_detach(self, cls=None):
        cls = cls if cls is not None else self.__class__
        ids = []
        for i in reversed(range(self.layout().count())):
            with suppress(AttributeError):
                self.layout().itemAt(i).widget().handle_detach(cls)
                ids.append(self.layout().itemAt(i).widget().identifier)
        self.identifier = ";".join(reversed(ids))

    def handle_reattach(self, cls=None):
        cls = cls if cls is not None else self.__class__
        ids = []
        for i in reversed(range(self.layout().count())):
            with suppress(AttributeError):
                self.layout().itemAt(i).widget().handle_reattach(cls)
                ids.append(self.layout().itemAt(i).widget().identifier)
        self.identifier = ";".join(reversed(ids))