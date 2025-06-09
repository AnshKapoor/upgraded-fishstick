from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot
from contextlib import suppress
import threading
import qtawesome as qta
import pyqtgraph as pg

try:
    from gspy_egse.gui.hardware_modules.spi_interface.spi_onyx import SPIConsole
    from gspy_egse.gui.utils.plugin_settings import PluginSettings
    from gspy_egse.gui.utils.misc import add_value_to_data, Extendable, WrappedMessageHandler
    from gspy_egse.gui.utils.widget import expand_widget, SplitterWithSettings, re_plot, call_in_main_thread
    from gspy_egse.gui.utils.plugin import Setting, ObjectWithSettings, WidgetWithExtension
    from gspy_egse.gui.utils.recorder import Recordable
except (ValueError, ImportError):
    from hardware_modules.spi_interface.spi_onyx import SPIConsole
    from utils.plugin_settings import PluginSettings
    from utils.misc import add_value_to_data, Extendable, WrappedMessageHandler
    from utils.widget import expand_widget, SplitterWithSettings, re_plot, call_in_main_thread
    from utils.plugin import Setting, ObjectWithSettings, WidgetWithExtension
    from utils.recorder import Recordable


class SpiInterfaceConnection(QtCore.QObject, ObjectWithSettings, Recordable):
    def __init__(self, window: Extendable, *args, **kwargs):
        with suppress(Exception):
            if window.has_extension_class(self.__class__):
                return

        self.window = window
        super().__init__(*args, plugin_settings=PluginSettings(__file__), **kwargs)
        self.hardware_params_changed.connect(self.open)
        self.open_timer = None
        self.open_lock = threading.Lock()

        self.port = self.add_setting(
            name="OP_Mode",
            default="SPi/GPIO",
            in_settings=True,
            type_=Setting.STRING,
            listener=self.open,
            widget_id=None)
        self.ch = self.add_setting(
            name="Slave Select",
            default=1,
            in_settings=True,
            min_=1,
            max_=4,
            type_=Setting.INT,
            listener=self.open,
            widget_id=None)
        self.baudrate = self.add_setting(
            setting_index=1,
            name="Bit Rate",
            default=200000,
            in_settings=True,
            min_=200000,
            max_=25000000,
            type_=Setting.INT,
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
        self.hardware = SPIConsole(master_mode=False)

    def close(self):
        self.hardware.close()
        self.hardware = None

class SpiInterfaceWidget(WidgetWithExtension):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, plugin_name=NAME, ext_cls=SpiInterfaceConnection, **kwargs)

    def _delay_init(self, extension=None, _=False):
        self.inherit_settings_from_parent(extension)
        self.connection = extension  # type: SpiInterfaceConnection

        self.message_handler = WrappedMessageHandler(None, "SPI Interface")
        self.ui = uic.loadUi("src/gspy_egse/gui/ui/spiInterface.ui", self)
        self.pushButton_File.clicked.connect(self.fileTransfer)      
        self.pushButton_Transmit.clicked.connect(self.write)
        self.slaveReadButton.clicked.connect(self.read)
        self.label.setText(f"Device: {self.connection.hardware.myDevice.Description}")
        self.label_2.setText(f"Id: {self.connection.hardware.myDevice.Id}")
        self.label_3.setText(f"Serial Number: {self.connection.hardware.myDevice.SerialNumber}")
        self.label_4.setText(f"Device Connection Status: {self.connection.hardware.myDevice.DeviceConnectionStatus}")
        self.label_5.setText(f"Bit Rate: {self.connection.hardware.actual_Set_Speed}")
        self.label_6.setText(f"Operation Mode: {self.connection.hardware.operationMode}")
        self.make_settings_btn(self.settingsButton)

    def fileTransfer(self):
        self.FileData = []
        selected_file = ""
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setWindowTitle("Select File")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                selected_file = file_paths[0]
                self.selectedFileLabel.setText(f"Selected File: {selected_file}")
                        
        if selected_file:
            with open(selected_file, 'r') as file_:
                data_as_string = file_.read()
                self.FileData = data_as_string

    def convertToBytes(self, text):
        #Removal of non-hexadecimal characters
        cleanedText = ''.join(filter(lambda x: x in '0123456789abcdefABCDEF', text))
        if(len(cleanedText) % 2 != 0):
            cleanedText = cleanedText[:-1] + '0' + cleanedText[-1]
        #Division of the text into two-line segments and conversion into bytes
        bytesList = bytes.fromhex(cleanedText)
        return bytesList

    def write(self):
        if self.isMasterMode():
            self.hexReceive.clear()
            if(self.tabWidget.currentIndex() == 0):
                input = self.FileData
            elif(self.tabWidget.currentIndex() == 1):
                input = self.userInput.toPlainText()

            txBytes = self.convertToBytes(input)
            self.connection.hardware.spi_Master_Write(txBytes)
            self.transmitResult.setText(f"TransmitResult: {self.connection.hardware.onyxStatus}")
            self.exchangedByteCount.setText(f"ExchangedByteCount: {self.connection.hardware.exchangedByteCount} bytes.")
            for rx in self.connection.hardware.rxBytes:
                self.hexReceive.insertPlainText(f"{rx}")
        else:
            self.message_handler.error("Device is in Slave Mode. Cannot write data.")
            return

    def read(self):
        if not self.isMasterMode():
            self.hexReceive.clear()
            self.connection.hardware.slave_read()
            self.transmitResult.setText(f"TransmitResult: {self.connection.hardware.onyxStatus}")
            self.exchangedByteCount.setText(f"ExchangedByteCount: {self.connection.hardware.exchangedByteCount} bytes.")
            for rx in self.connection.hardware.rxBytes:
                self.hexReceive.insertPlainText(f"{rx}")
        else:
            self.message_handler.error("Device is in Master Mode. Cannot read data.")
            return

    def isMasterMode(self):
        if(self.connection.hardware.Master == True):
            return True
        else:
            return False

VERSION = 1
NAME = "SPI Interface"
BACKGROUND_TASKS = [SpiInterfaceConnection]
