from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot
from contextlib import suppress
import threading
import qtawesome as qta
import pyqtgraph as pg

try:
    from gspy_egse.gui.hardware_modules import powersupply
    from ..utils.plugin_settings import PluginSettings
    from ..utils.misc import add_value_to_data, Extendable
    from ..utils.widget import expand_widget, SplitterWithSettings, re_plot, call_in_main_thread
    from ..utils.plugin import Setting, ObjectWithSettings, WidgetWithExtension
    from ..utils.recorder import Recordable
except (ValueError, ImportError):
    from hardware_modules import powersupply
    from utils.plugin_settings import PluginSettings
    from utils.misc import add_value_to_data, Extendable
    from utils.widget import expand_widget, SplitterWithSettings, re_plot, call_in_main_thread
    from utils.plugin import Setting, ObjectWithSettings, WidgetWithExtension
    from utils.recorder import Recordable


class PowerSupplyConnection(QtCore.QObject, ObjectWithSettings, Recordable):
    def __init__(self, window: Extendable, *args, **kwargs):
        print(f"powersupply.py: PowerSupplyConnection.__init__")
        with suppress(Exception):
            if window.has_extension_class(self.__class__):
                return

        self.window = window
        super().__init__(*args, plugin_settings=PluginSettings(__file__), **kwargs)
        self.hardware_params_changed.connect(self.open)
        self.open_timer = None
        self.open_lock = threading.Lock()

        self.port = self.add_setting(
            name="port",
            default="COM4",
            in_settings=True,
            type_=Setting.STRING,
            listener=self.open,
            widget_id=None)
        self.ch = self.add_setting(
            name="channels",
            default=1,
            in_settings=True,
            min_=1,
            max_=4,
            type_=Setting.INT,
            listener=self.open,
            widget_id=None)
        self.baudrate = self.add_setting(
            setting_index=1,
            name="baudrate",
            default=19200,
            in_settings=True,
            min_=110,
            max_=921600,
            type_=Setting.INT,
            listener=self.open,
            widget_id=None)
        self.poll = self.add_setting(
            name="poll",
            default=True,
            in_settings=True,
            type_=Setting.BOOL,
            listener=self.open,
            widget_id=None)
        self.i_val = self.add_setting(
            name="poll_ival",
            title="Poll Interval",
            default=250,
            in_settings=True,
            type_=Setting.INT,
            listener=None,
            widget_id=None)
        self.mockup = self.add_setting(
            name="mockup",
            title="Mockup Values",
            default=False,
            in_settings=True,
            type_=Setting.BOOL,
            listener=self.open,
            widget_id=None)

        self.hardware = None
        self.message_handler = window.message_handler
        self.window.add_extension(self)

    hardware_params_changed = pyqtSignal()

    @pyqtSlot()
    def open(self, *_, **listener_args):
        if len(listener_args) > 0:
            if self.open_lock.locked():
                return
            with self.open_lock:
                if self.open_timer is not None:
                    self.open_timer.start(self.open_timer.interval())
                    return
                self.open_timer = QtCore.QTimer(self)
                self.open_timer.timeout.connect(self.hardware_params_changed.emit)
                self.open_timer.setSingleShot(True)
                self.open_timer.start(10)
            return
        if self.hardware is not None:
            self.close()
        constructor = powersupply.MockupPowerSupply if self.mockup.value else powersupply.PowerSupply
        ch = self.ch.value

        self.hardware = constructor(
            port=self.port.value,
            baudrate=self.baudrate.value,
            channels=ch,
            polling=self.poll.value,
            polling_interval=self.i_val.value,
            message_handler=self.message_handler
        )
        self.hardware.add_listeners([self._state_set] * ch, [self._v_set] * ch, [self._i_set] * ch, [self._v_out] * ch,
                                    [self._i_out] * ch)

    def add_widget(self, w: "PowerSupplyWidget"):
        if w.channel > self.ch.value:
            self.message_handler.error("PowerSupply: Can't display channel %d of %d!" % (w.channel, self.ch.value))
            w.edit_v.setEnabled(False)
            w.edit_i.setEnabled(False)
            w.button.setEnabled(False)
            w.stateLabel.setText("Error")
            w.stateLabel.setStyleSheet("background-color: {0};padding: 0 {1} 0 {1};".format("red", "5px"))
            w.radioNone.setEnabled(False)
            w.radioPlot.setEnabled(False)
            w.radioCurrent.setEnabled(False)
            w.radioVoltage.setEnabled(False)
            w.radioNone.setEnabled(False)
            w.radioBoth.setEnabled(False)
            return
        w.hardware = self.hardware
        w.button.pressed.connect(w.toggle_state)
        w.edit_v.setText(str(self.hardware.voltage[w.channel - 1]))
        w.edit_i.setText(str(self.hardware.intensity[w.channel - 1]))
        w.set_button(self.hardware.state[w.channel - 1])
        self.state_set.connect(w.state_set)
        self.v_set.connect(w.v_set)
        self.i_set.connect(w.i_set)
        self.v_out.connect(w.v_out)
        self.i_out.connect(w.i_out)

    @Recordable.intercept_on_playback()
    @Recordable.record_method()
    def _state_set(self, value, channel=1, play_back=False):
        _ = play_back  # unused
        self.state_set.emit(value, channel)

    state_set = pyqtSignal(bool, int)

    @Recordable.intercept_on_playback()
    @Recordable.record_method()
    def _v_set(self, value, channel=1, play_back=False):
        _ = play_back  # unused
        self.v_set.emit(value, channel)

    v_set = pyqtSignal(float, int)

    @Recordable.intercept_on_playback()
    @Recordable.record_method()
    def _i_set(self, value, channel=1, play_back=False):
        _ = play_back  # unused
        self.i_set.emit(value, channel)

    i_set = pyqtSignal(float, int)

    @Recordable.intercept_on_playback()
    @Recordable.record_method()
    def _v_out(self, value, channel=1, play_back=False):
        _ = play_back  # unused
        self.v_out.emit(value, channel)

    v_out = pyqtSignal(float, int)

    @Recordable.intercept_on_playback()
    @Recordable.record_method()
    def _i_out(self, value, channel=1, play_back=False):
        _ = play_back  # unused
        self.i_out.emit(value, channel)

    i_out = pyqtSignal(float, int)

    def close(self):
        self.hardware.close()
        self.hardware = None


class PowerSupplyWidget(WidgetWithExtension):
    def __init__(self, *args, default_channel=1, default_view=None, **kwargs):
        print(f"powersupply.py: PowerSupplyWidget.__init__")
        self._params = (default_channel, default_view)
        super().__init__(*args, plugin_name=NAME, ext_cls=PowerSupplyConnection, **kwargs)

    def _delay_init(self, extension=None, _=False):
        self.inherit_settings_from_parent(extension)
        c = self.connection = extension  # type: PowerSupplyConnection

        (default_channel, default_view) = self._params
        self.ui = uic.loadUi("ui/powersupplywidget.ui", self)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.v_plot = pg.PlotWidget(self)
        self.v_plot.setLabel("left", "Voltage", units="V")
        self.v_plot.setLabel("bottom", "Time", units="s")
        self.v_plot.hide()
        expand_widget(self.v_plot)
        self.i_plot = pg.PlotWidget(self)
        self.i_plot.setLabel("left", "Current", units="A")
        self.i_plot.setLabel("bottom", "Time", units="s")
        self.i_plot.hide()
        expand_widget(self.i_plot)
        self.manual_deletes.add(self.v_plot)
        self.manual_deletes.add(self.i_plot)

        if default_view is None:
            default_view = [1, 3]

        self.views = self.add_setting(
            name="views",
            default=default_view,
            in_settings=False,
            min_length=2,
            max_length=2,
            value_type=int,
            type_=Setting.LIST,
            listener=self.set_views,
            widget_id=self.identifier)

        self._channel = self.add_setting(
            name="channel",
            default=default_channel,
            in_settings=True,
            min_=1,
            max_=4,
            type_=Setting.INT,
            listener=self.set_title,
            widget_id=self.identifier)

        self.poll_history = self.add_setting(
            name="poll_history",
            unit="seconds",
            default=10,
            in_settings=True,
            min_=1,
            max_=60,
            type_=Setting.FLOAT,
            listener=None,
            widget_id=self.identifier)

        self.plot_data = {"v": {"x": list(), "y": list()}, "i": {"x": list(), "y": list()}}
        c.add_widget(self)
        self.edit_v.returnPressed.connect(self.set_v)
        self.edit_i.returnPressed.connect(self.set_i)
        self.make_settings_btn(self.settingsButton)

    @property
    def channel(self):
        return self._channel.value

    def set_views(self, value=None, **kwargs):
        from_setting = value is not None
        if from_setting and kwargs["init"]:  # setting has changed, update checkboxes
            self.radioNone.setChecked(value[0] == 0)
            self.radioNone.released.connect(self.set_views)
            self.radioPlot.setChecked(value[0] == 1)
            self.radioPlot.released.connect(self.set_views)
            self.radioGauge.setChecked(value[0] == 2)
            self.radioGauge.released.connect(self.set_views)

            self.radioVoltage.setChecked(value[1] == 1)
            self.radioVoltage.released.connect(self.set_views)
            self.radioCurrent.setChecked(value[1] == 2)
            self.radioCurrent.released.connect(self.set_views)
            self.radioBoth.setChecked(value[1] == 3)
            self.radioBoth.released.connect(self.set_views)
        try:  # checkboxes changed, update setting
            self.clear_view()
            l_old = l = self.viewLayout  # type: QtWidgets.QHBoxLayout

            view_type = int(self.radioPlot.isChecked()) + int(self.radioGauge.isChecked()) * 2
            view_show = int(self.radioVoltage.isChecked()) + int(self.radioCurrent.isChecked()) * 2 + int(
                self.radioBoth.isChecked()) * 3

            if view_type == 0:
                l.addSpacerItem(expand_widget(QtWidgets.QSpacerItem(10, 10)))
            elif view_type == 1:
                if view_show == 3:
                    s = SplitterWithSettings(self)
                    l = s
                if view_show & 1 == 1:
                    l.addWidget(self.v_plot)
                    self.v_plot.show()
                if view_show & 2 == 2:
                    l.addWidget(self.i_plot)
                    self.i_plot.show()
                if view_show == 3:
                    l_old.addWidget(l)

            if not from_setting:
                self.views.set([view_type, view_show])
        except:
            import traceback
            traceback.print_exc()

    def clear_view(self):
        for i in reversed(range(self.viewLayout.count())):
            item = self.viewLayout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QtWidgets.QSplitter):
                self.viewLayout.addWidget(self.v_plot)
                self.viewLayout.addWidget(self.i_plot)
                self.viewLayout.removeWidget(widget)
                widget.deleteLater()
                return self.clear_view()
            if isinstance(item, QtWidgets.QSpacerItem):
                self.viewLayout.removeItem(item)
                del item
            else:
                self.viewLayout.removeWidget(widget)
                widget.hide()

    def set_title(self, value=None):
        value = self.channel if value is None else value
        title = self.title.text()[:-1] + str(value)
        self.title.setText(title)

    def set_button(self, state):
        self.button.setText("Off" if state else "On")
        self.stateLabel.setText("On" if state else "Off")
        self.stateLabel.setStyleSheet("background-color: {0};padding: 0 {1} 0 {1};".format(
            "rgb(200, 255, 200)" if state else "rgb(255, 180, 180)",
            "5px"
        ))

    def toggle_state(self):
        self.connection.hardware.set_state_to_device(channel=self.channel, value=self.button.text() == "On")

    def set_v(self):
        val = float(self.edit_v.text())
        self.connection.hardware.set_voltage_to_device(channel=self.channel, value=val)

    def set_i(self):
        val = float(self.edit_i.text())
        self.connection.hardware.set_intensity_to_device(channel=self.channel, value=val)

    @pyqtSlot(bool, int)
    def state_set(self, value, channel):
        if channel != self.channel:
            return
        self.set_button(value)

    @pyqtSlot(float, int)
    def v_set(self, value, channel):
        if channel != self.channel:
            return
        self.edit_v.setText(str(value))

    @pyqtSlot(float, int)
    def i_set(self, value, channel):
        if channel != self.channel:
            return
        self.edit_i.setText(str(value))

    @pyqtSlot(float, int)
    def v_out(self, value, channel):
        if channel != self.channel:
            return
        self.label_vout.setText(str(value))
        add_value_to_data(self.plot_data["v"], value, self.connection.i_val.value / 1000, self.poll_history.value)
        re_plot(self.v_plot, x=self.plot_data["v"]["x"], y=self.plot_data["v"]["y"], pen=pg.mkPen('k'))

    @pyqtSlot(float, int)
    def i_out(self, value, channel):
        if channel != self.channel:
            return
        self.label_iout.setText(str(value))
        add_value_to_data(self.plot_data["i"], value, self.connection.i_val.value / 1000, self.poll_history.value)
        re_plot(self.i_plot, x=self.plot_data["i"]["x"], y=self.plot_data["i"]["y"], pen=pg.mkPen('k'))


VERSION = 1
NAME = "Power Supply"
BACKGROUND_TASKS = [PowerSupplyConnection]
