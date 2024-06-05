from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from contextlib import suppress
import threading
import re

try:
    from ...hardware_modules.spacewire import SpaceWire
    from ...hardware_modules.spacewire_gresb import SpaceWireBridgeGresb
    from ...hardware_modules.spacewire_shimafuji import SpaceWireBridgeShimafuji
    from ...hardware_modules.spacewire_brick_mk4 import SpaceWireBrickMk4
    from ...hardware_modules.juice_lib.commands import *
    from ...utils.misc import Extendable
    from ...utils.plugin import Setting, ObjectWithSettings, PluginSettings
    from ...utils.recorder import Recordable
except (ValueError, ImportError):
    from hardware_modules.spacewire import SpaceWire
    from hardware_modules.spacewire_gresb import SpaceWireBridgeGresb
    from hardware_modules.spacewire_shimafuji import SpaceWireBridgeShimafuji
    from hardware_modules.spacewire_brick_mk4 import SpaceWireBrickMk4
    from hardware_modules.juice_lib.commands import *
    from utils.misc import Extendable
    from utils.plugin import Setting, ObjectWithSettings, PluginSettings
    from utils.recorder import Recordable


class RecordableSpaceWire(SpaceWire, Recordable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @Recordable.intercept_on_playback()
    @Recordable.record_method()
    def message_received(self, *args, play_back=False, **kwargs):
        return SpaceWire.message_received(self, *args, **kwargs)

    @Recordable.intercept_on_playback()
    def cmd(self, *args, play_back=False, **kwargs):
        return SpaceWire.cmd(self, *args, **kwargs)

class SpaceWireConnection(QtCore.QObject, ObjectWithSettings, Recordable):
    hardware_params_changed = pyqtSignal()

    def __init__(self, window: Extendable, *args, **kwargs):
        with suppress(Exception):
            if window.has_extension_class(self.__class__):
                return

        super().__init__(*args, plugin_settings=PluginSettings(__file__), **kwargs)
        self.window = window

        self.open_lock = threading.Lock()
        self.open_timer = None
        self.hardware_params_changed.connect(self.open)
        self.hardware = None
        self.message_handler = window.message_handler
        self.initialized = False  # lock open listeners
         
        self.ip = self.add_setting(
            name='ip',
            default='127.0.0.1',
            in_settings=False,
            type_=Setting.STRING,
            listener=self.open
        )
        self.port = self.add_setting(
            name='port',
            default=3000,
            in_settings=False,
            min_=0,
            max_=65535,
            type_=Setting.INT,
            listener=self.open
        )
        self.bridge_type = self.add_setting(
            name='bridge_type',
            default='BrickMk4',
            in_settings=True,
            reg_ex=re.compile('^(gresb|shimafuji|brickmk4)$', re.IGNORECASE),
            type_=Setting.STRING,
            listener=self.open
        )
        self.spw_dest_addr = self.add_setting(
            name='spw_dest_addr',
            default=2,
            min_=0,
            in_settings=True,
            type_=Setting.INT,
            listener=self.open
        )
        self.spw_trans_channel = self.add_setting(
            name='transmission_channel',
            default=1,
            min_=1,
            max_=2,
            in_settings=False,
            type_=Setting.INT,
            listener=self.open
        )
        self.spw_receive_channel = self.add_setting(
            name='receive_channel',
            default=2,
            min_=1,
            max_=2,
            in_settings=False,
            type_=Setting.INT,
            listener=self.open
        )
        self.spw_packet_size = self.add_setting(
            name='spw_packet_size',
            default=4096,
            min_=0,
            in_settings=True,
            type_=Setting.INT,
            listener=self.open
        )
        self.spw_Link_1_output_clock_rate = self.add_setting(
            name='spw_output_clock_rate_Link1',
            default=100,
            min_=1,
            max_=200,
            in_settings=True,
            type_=Setting.INT,
            listener=self.open
        )
        self.spw_Link_2_output_clock_rate = self.add_setting(
            name='spw_output_clock_rate_Link2',
            default=100,
            min_=1,
            max_=200,
            in_settings=True,
            type_=Setting.INT,
            listener=self.open
        )

        self.open()  # synchronous open to ensure open state then extension is added
        self.initialized = True  # lock open listeners
        self.window.add_extension(self)

    def _open_bridge(self):
        if self.bridge_type.value.lower() == 'shimafuji':
            Cls = SpaceWireBridgeShimafuji 
        elif self.bridge_type.value.lower() == 'brickmk4':
            Cls = SpaceWireBrickMk4
        else: 
            Cls = SpaceWireBridgeGresb

        return Cls(self.ip.value, self.port.value)

    def re_open(self):
        with self.open_lock:
            self.hardware.set_spw_dest_addr(self.spw_dest_addr.value)
            self.hardware.set_spw_packet_size(self.spw_packet_size.value)
            self.hardware.set_spw_raw_synchronous(self._open_bridge())

    @pyqtSlot()
    def open(self, *_, **listener_args):
        if self.open_lock.locked():
            return
        with self.open_lock:
            if len(listener_args) > 0:
                if not self.initialized:
                    return
                if self.open_timer is not None:
                    self.open_timer.start(self.open_timer.interval())
                    return
                self.open_timer = QtCore.QTimer(self)
                self.open_timer.timeout.connect(self.hardware_params_changed.emit)
                self.open_timer.setSingleShot(True)
                self.open_timer.start(10)
                return
            if self.hardware is not None:
                return threading.Thread(target=self.re_open).start()
            self.hardware = RecordableSpaceWire(
                self._open_bridge(),
                spw_dest_addr=self.spw_dest_addr.value,
                spw_packet_size=self.spw_packet_size.value,
                message_handler=self.message_handler
            )

    def close(self):
        with suppress(Exception):
            self.hardware.close()
            self.hardware = None
        self.message_handler.info("Spacewire is gone.")


VERSION = 1
BACKGROUND_TASKS = [SpaceWireConnection]
