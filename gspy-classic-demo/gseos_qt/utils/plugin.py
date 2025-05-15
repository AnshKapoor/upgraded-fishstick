from PyQt6 import QtWidgets, QtCore, uic
from copy import copy
from .plugin_settings import PluginSettings
from contextlib import suppress
from .misc import MAX_INT32, random_identifier


class ObjectWithSettings:
    def __init__(self, *args, plugin_settings=None, settings=None, **kwargs):
        super().__init__(*args, **kwargs)
        # print(self.__class__.__name__, plugin_settings is None)
        self.settings = list() if settings is None else settings  # type: Setting[]
        if plugin_settings is not None:
            self.plugin_settings = plugin_settings

    def inherit_settings_from_parent(self, super_: 'ObjectWithSettings'):
        self.plugin_settings = super_.plugin_settings
        self.settings = copy(super_.settings)

    def add_setting(self, name, *args, setting_index=-1, unique=False, widget_id=None, **kwargs):
        if unique:
            for s in reversed(self.settings):  # type: Setting
                if s.name == name and s.widget_id == widget_id:
                    self.settings.remove(s)
                    del s
        if self.plugin_settings is not None:
            s = Setting(*args, name=name, widget_id=widget_id, settings=self.plugin_settings, **kwargs)
        else:
            s = Setting(*args, name=name, widget_id=widget_id, **kwargs)
        self.settings.insert(len(self.settings) if setting_index == -1 else setting_index, s)
        return s


class WidgetWithSettings(QtWidgets.QWidget, ObjectWithSettings):
    def __init__(self, window, *args, identifier="MainWidget", plugin_name=None, plugin_settings=None, settings=None,
                 **kwargs):
        super().__init__(*args, plugin_settings=plugin_settings, settings=settings, **kwargs)
        self.main_window = window
        self.plugin_name = plugin_name if plugin_name is not None else self.__class__
        self.windows = set()
        self.manual_deletes = set()

        self.identifier = identifier
        self._add_old_identifier = False
        try:
            self.old_identifier = self.add_setting(
                name="old_identifier",
                none_allowed=True,
                default=None,
                type_=Setting.STRING,
                widget_id=self.identifier,
                listener=None,
                in_settings=False
            )
        except AttributeError:
            self._add_old_identifier = True

    def make_settings_btn(self, btn: QtWidgets.QPushButton):
        import qtawesome
        # qtawesome.load_font('fa', '/Users/eike/PycharmProjects/gspy/gspy-classic-demo/gseos_qt/res/FontAwesome_new.ttf', charmap_filename=None)
        btn.setIcon(qtawesome.icon('fa.cogs'))
        btn.setText("Settings")
        btn.released.connect(self.open_settings)

    def inherit_settings_from_parent(self, super_: 'ObjectWithSettings'):
        ObjectWithSettings.inherit_settings_from_parent(self, super_)
        if self._add_old_identifier:
            self._add_old_identifier = False
            self.old_identifier = self.add_setting(
                name="old_identifier",
                none_allowed=True,
                default=None,
                type_=Setting.STRING,
                widget_id=self.identifier,
                listener=None,
                in_settings=False
            )

    @property
    def is_detached(self):
        return self.old_identifier.value is not None

    def open_settings(self):
        if len(self.windows) == 0:
            self.windows.add(PluginSettingsWindow(self, plugin_name=self.plugin_name))
        else:
            next(iter(self.windows)).raise_()

    def delete_settings(self):
        for s in self.settings:
            s.widget_deleted()

    def deleteLater(self):
        for window in self.windows:
            window.widget = None
            window.close()
            window.deleteLater()
        for o in self.manual_deletes:
            o.deleteLater()

        QtWidgets.QWidget.deleteLater(self)

    def handle_detach(self, cls=None):
        if self.is_detached:
            return False
        old_identifier = self.identifier
        self.identifier += "_Detached_%s" % random_identifier(2)
        for s in self.settings:
            s.widget_id_changed(self.identifier, copy_instead_of_move=True)
        self.old_identifier.set(old_identifier)

    def handle_reattach(self, **_):
        if not self.is_detached:
            return False
        self.identifier = self.old_identifier.value
        self.old_identifier.set(None)
        for s in self.settings:
            s.widget_id_changed(self.identifier)

    def set_to_default_settings(self):
        '''
        set the value of the settings back to default
        '''
        for s in self.settings:
            default_value = s.get_default()
            s.set(default_value)

class WidgetWithExtension(WidgetWithSettings):
    def __init__(self, window, *args, ext_cls=None, sub_exts=None, **kwargs):
        super().__init__(window, *args, **kwargs)
        self._init_delay_listeners = []
        self.__delay_init_signal.connect(self.__delay_init)
        self._sub_exts = sub_exts if sub_exts is not None else []

        try:
            self._params
        except AttributeError:
            self._params = (args, kwargs)

        with suppress(AttributeError):
            self._init()

        self._init_delayed = False  # indicate _delay_init that init is not delayed and no listeners need to be called
        window.add_extension_class_listener(ext_cls, self.__delay_init)  # this might call _delay_init:
        if self._init_delayed:  # already finished, _delay_init was called
            self._init_delayed = False  # indicate add_listener to exec immediately
        else:  # we are waiting
            self._init_delayed = True  # indicate _delay_init that init is delayed and listeners need to be called

    def add_init_complete_listener(self, listener):
        if not self._init_delayed:
            try:
                listener(self)
            except TypeError:
                listener()
        else:
            self._init_delay_listeners.append(listener)

    __delay_init_signal = QtCore.pyqtSignal(object, bool)

    def _delay_init(self, *_):
        pass

    @QtCore.pyqtSlot(object, bool)
    def __delay_init(self, extension, threaded=False):
        for E in (self._sub_exts if isinstance(self._sub_exts, list) else [self._sub_exts]):
            with suppress(ValueError):
                E(extension)

        if not self._init_delayed:  # extension is not delayed
            # no listeners
            self._init_delayed = True  # notify __init__ that we already finished
            with suppress(AttributeError):
                try:
                    self._delay_init(extension, False)
                except TypeError:
                    self._delay_init(extension)
        else:  # extension is delayed
            if not threaded:
                return self.__delay_init_signal.emit(extension, True)
            for listener in self._init_delay_listeners:  # notify listeners
                try:
                    listener(self)
                except TypeError:
                    listener()

            self._init_delayed = False  # delayed init done
            with suppress(AttributeError):
                try:
                    self._delay_init(extension, False)
                except TypeError:
                    self._delay_init(extension)


class Setting:
    def __init__(self, settings, type_, default, listener, in_settings, name, *args, title=None, widget_id=None,
                 unit=None, none_allowed=True, **kwargs):
        self.settings = settings
        self.type_ = type_
        self.default = default
        self.listener = listener  # type: "func"
        self.name = name.lower().replace(" ", "_")  # type: "str"
        self.title = name.title().replace("_", " ") if title is None else title  # type: "str"
        self.in_settings = in_settings  # type: "bool"
        self.widget_id = widget_id  # type: "str"
        self.unit = unit
        self.none_allowed = none_allowed

        if type_ == Setting.INT:
            self._int_init(*args, **kwargs)
        elif type_ == Setting.FLOAT:
            self._float_init(*args, **kwargs)
        elif type_ == Setting.STRING:
            self._string_init(*args, **kwargs)
        elif type_ == Setting.LIST:
            self._list_init(*args, **kwargs)
        elif type_ == Setting.BOOL:
            super().__init__(*args, **kwargs)
        else:
            raise TypeError("This type is not supported (yet)!")

        self.value = None
        self.set(self._s_get(), init=True)

    INT = int
    FLOAT = float
    STRING = str
    BOOL = bool
    LIST = list

    def _check_value(self, value):
        if value is None and self.none_allowed:
            return True
        assert isinstance(value, self.type_) or (self.type_ == Setting.FLOAT and isinstance(value, Setting.INT)), \
            "%s is not of type %s!" % (str(value), str(self.type_))
        if self.type_ == Setting.INT:
            if value < self.min or value > self.max:
                raise ValueError("%d is out of bounds! (%s)" % (value, self.name))
        elif self.type_ == Setting.FLOAT:
            if value < self.min or value > self.max:
                raise ValueError("%d is out of bounds! (%s)" % (value, self.name))
        elif self.type_ == Setting.STRING:
            assert isinstance(value, str)  # avoid pycharm type confusion
            if (self.min_length is not None and len(value) < self.min_length) or (
                            self.max_length is not None and len(value) > self.max_length):
                raise ValueError("length of %s is out of bounds!" % value)
            if self.reg_ex is not None and self.reg_ex.match(value) is None:
                raise ValueError("%s does not match %s!" % (value, str(self.reg_ex)))
        elif self.type_ == Setting.LIST:
            assert isinstance(value, list)  # avoid pycharm type confusion
            if (self.min_length is not None and len(value) < self.min_length) or (
                            self.max_length is not None and len(value) > self.max_length):
                raise ValueError("length of %s is out of bounds!" % str(value))
            if self.value_type is not None:
                for v in value:
                    assert isinstance(v, self.value_type), "%s is not of type [%s]!" % (
                        str(value), str(self.value_type))

    def _int_init(self, *args, min_=None, max_=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min = min_ if min_ is not None else -MAX_INT32
        self.max = max_ if max_ is not None else MAX_INT32

    def _float_init(self, *args, min_=None, max_=None, step=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min = min_ if min_ is not None else -MAX_INT32
        self.max = max_ if max_ is not None else MAX_INT32
        self.step = step

    def _string_init(self, *args, min_length=None, max_length=None, reg_ex=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.reg_ex = reg_ex

    def _list_init(self, *args, min_length=None, max_length=None, value_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.value_type = value_type

    def set(self, value, init=False):
        trim = value
        if not init and self.type_ == Setting.FLOAT and self.step is not None:
            if self.step > abs(self.value - value):
                return

            trim = value + self.step / 2
            trim = int(trim / self.step)
            trim = trim * self.step
        self._check_value(value)
        if self.listener is not None:
            try:
                self.listener(value, init=init, changed=self.value != value, old=self.value)
            except TypeError:
                self.listener(value)
        self.value = trim
        if not init:
            self._s_set()

    def _s_get(self):
        if self.widget_id is None:
            self.value = self.settings.get(self.name, self.default)
        else:
            self.value = self.settings.get(["widgets", self.widget_id, self.name], self.default)

        return self.value

    def _s_set(self):
        if self.widget_id is None:
            self.settings.set(self.name, self.value)
        else:
            self.settings.set(["widgets", self.widget_id, self.name], self.value)

        return self.value

    def _s_rm(self):
        if self.widget_id is None:
            self.settings.rm(self.name)
        else:
            self.settings.rm(["widgets", self.widget_id, self.name])

    def widget_id_changed(self, identifier, copy_instead_of_move=False):
        if self.widget_id is None:
            return
        if not copy_instead_of_move:
            self._s_rm()
        self.widget_id = identifier
        self._s_set()

    def widget_deleted(self):
        if self.widget_id is None:
            return
        self._s_rm()

    def is_default(self, strict=False):
        if strict or self.value == self.default or self.type_ in [Setting.INT, Setting.BOOL, Setting.LIST]:
            return self.value == self.default

        if self.type_ == Setting.FLOAT:
            return abs(self.value - self.default) / (self.value + self.default) < .005

        if self.type_ == Setting.STRING:
            return self.value.lower().strip() == self.default.lower().strip()

        return False
    
    def get_default(self, strict=False):
        return self.default


class PluginSettingsWindow(QtWidgets.QMainWindow):
    def __init__(self, widget_: "WidgetWithSettings", plugin_name, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
            from .widget import expand_widget

            self.widget = widget_
            self.setWindowTitle(widget_.window().windowTitle())
            cw = self.central_widget = QtWidgets.QWidget(self)
            l = self.layout_ = QtWidgets.QVBoxLayout(cw)
            top_box = QtWidgets.QGroupBox(cw)
            #top_box.setTitle(plugin_name)
            top_box.setTitle("top_box")
            top = QtWidgets.QFormLayout(top_box)
            bottom_box = QtWidgets.QGroupBox(cw)
            bottom_box.setTitle("bottom_box")
            bottom = QtWidgets.QFormLayout(bottom_box)
            button_box = QtWidgets.QGroupBox(cw)
            button_box.setTitle("buttonBox")
            button_layout = QtWidgets.QHBoxLayout(cw)
            self.settings_tuple = set()
            for s in widget_.settings:  # type: Setting
                if not s.in_settings:
                    continue
                space_left = True
                space_right = False
                if s.type_ == s.INT:
                    w = QtWidgets.QSpinBox(cw)
                    w.setMinimum(s.min)
                    w.setMaximum(s.max)
                    w.setValue(s.value)
                elif s.type_ == s.FLOAT:
                    w = QtWidgets.QDoubleSpinBox(cw)
                    w.setMinimum(s.min)
                    w.setMaximum(s.max)
                    if s.step is not None:
                        w.setSingleStep(s.step)
                    w.setValue(s.value)
                elif s.type_ == s.STRING:
                    w = QtWidgets.QLineEdit(cw)
                    w.setText(s.value)
                elif s.type_ == s.BOOL:
                    w = QtWidgets.QCheckBox(cw)
                    w.setChecked(s.value)
                else:
                    continue
                self.settings_tuple.add((s, w))
                box = top if s.widget_id is None else bottom
                layout = QtWidgets.QHBoxLayout(cw)
                if space_left:
                    layout.addSpacerItem(
                        QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
                layout.addWidget(w)
                if s.unit is not None:
                    layout.addWidget(QtWidgets.QLabel(s.unit))
                if space_right:
                    layout.addSpacerItem(
                        QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
                box.addRow(s.title + ":", layout)

            ok_btn = QtWidgets.QPushButton("OK")
            cancel_btn = QtWidgets.QPushButton("Cancel")
            apply_btn = QtWidgets.QPushButton("Apply")
            ok_btn.pressed.connect(self.save_close)
            cancel_btn.pressed.connect(self.close)
            apply_btn.pressed.connect(self.save)
            button_layout.addSpacerItem(
                QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
            button_layout.addWidget(ok_btn)
            button_layout.addWidget(cancel_btn)
            button_layout.addWidget(apply_btn)

            top_box.setLayout(top)
            bottom_box.setLayout(bottom)
            button_box.setLayout(button_layout)
            if top_box.layout().count() > 0:
                l.addWidget(top_box)
            else:
                top_box.deleteLater()
            if bottom_box.layout().count() > 0:
                l.addWidget(bottom_box)
            else:
                bottom_box.deleteLater()
            space = QtWidgets.QSpacerItem(1, 1)
            l.addSpacerItem(space)
            l.addWidget(button_box)
            cw.setLayout(l)
            self.setCentralWidget(cw)
            self.show()
            geo = self.geometry()
            expand_widget(space)
            self.setGeometry(geo)
        except (Exception,):
            import traceback
            traceback.print_exc()

    def closeEvent(self, q_close_event):
        if self.widget is not None:
            self.widget.windows.remove(self)
        QtWidgets.QMainWindow.closeEvent(self, q_close_event)

    def save(self):
        for setting, widget in self.settings_tuple:
            if setting.type_ in [Setting.INT, Setting.FLOAT]:
                setting.set(widget.value())
            if setting.type_ == Setting.STRING:
                setting.set(widget.text())
            if setting.type_ == Setting.BOOL:
                setting.set(widget.isChecked())

    def save_close(self):
        self.save()
        self.close()
