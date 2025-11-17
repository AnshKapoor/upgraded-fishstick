import json
import logging
import random
import threading
import time

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6 import QtCore, QtGui, QtWidgets, uic

from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.hardware_modules.juice_lib.BrickMk4_HW_Transmit import BrickMk4
from gspy_egse.gui.plugins.juice.spacewire import SpaceWireConnection
from gspy_egse.gui.utils.plugin import WidgetWithExtension
from gspy_egse.gui.utils.recorder import Recordable
from gspy_egse.gui.utils.transmitResultStorage import TransmitResultStorage
from gspy_egse.gui.utils.widget import (
    ActivationListener,
    async_in_main_thread,
    call_in_main_thread,
    delay_in_main_thread,
    select_file,
)

try:
    from PIL import Image
except ImportError:
    Image = None  # or handle gracefully


from importlib.resources import files, as_file  # stdlib, Python ≥3.9

logger = logging.getLogger(__name__)

pkg = "gspy_egse.gui.ui"
ui_name = "BrickMk4.ui"


class RequirePlugins(WidgetWithExtension): #background task is super important
    def __init__(self, *args, **kwargs):
        """Declare dependency on the SpaceWire connection and BrickMk4 hardware."""

        super().__init__(*args, ext_cls=SpaceWireConnection, identifier="_", sub_exts=[
            BrickMk4
        ], **kwargs)

    def _init(self) -> None:
        """Provide a no-op hook so the loader can safely invoke optional initialization."""

        # The loader expects this method; no additional startup state is required here.
        self._required_extensions: list[type] = [SpaceWireConnection, BrickMk4]


class BrickMk4Widget(WidgetWithExtension, Recordable):
    """
    :type spw: BrickMk4_HW_Transmit
    :type connection: SpaceWireConnection
    """
    def __init__(self, *args, **kwargs):
        """Initialize the widget and register its extension dependencies."""
        self.spw, self.connection = (None,) * 2
        super().__init__(*args, plugin_name="SpaceWire", ext_cls=SpaceWireConnection, singleton=False, **kwargs)

    def _init(self) -> None:
        """Set up default state before delayed initialization executes."""

        # Ensure attributes referenced by helper methods exist before _delay_init runs.
        self.addressBuffer: list[int] = []
        self.packetDataBuffer: list[int] = []
        self.writeOutLock: threading.Lock | None = None
        self.dummy: bool = False
        self.storage: TransmitResultStorage | None = None

    def _delay_init(self, extension: SpaceWireConnection | None = None, _: bool = False) -> None:
        """Complete the delayed UI initialization once SpaceWire is available."""

        self.addressBuffer = []
        self.packetDataBuffer = []
        self.inherit_settings_from_parent(extension)
        if extension is None:
            logger.error("BrickMk4Widget._delay_init() received no SpaceWire connection; skipping setup.")
            return

        self.connection = extension
        self.writeOutLock = threading.Lock()
        print(f"connection for BrickMk4 is: {extension}")
        self.spw = self.connection.hardware  # hardware = BrickMk4_HW_Transmit

        ui_res = files(pkg).joinpath(ui_name)
        with as_file(ui_res) as ui_path:
            self.ui = uic.loadUi(str(ui_path), self)
        # self.ui = uic.loadUi("gspy_egse/gui/ui/BrickMk4.ui", self)
        self.getFrequency()

        self.pushButton_preDefinedData.clicked.connect(self.simpleTransfer)
        self.pushButton_File.clicked.connect(self.fileTransfer)
        self.pushButton_Transmit.clicked.connect(self.send)
        self.resetButton.clicked.connect(self.resetDevice)
        self.FreqSet.clicked.connect(self.setFrequency)
        self.multiplePackets.toggled.connect(self.buttonMultiplePacket)
        self.spw.spw.spw_raw.signalEmitter.dataReceived.connect(self.displayResults)

# testing button
        self.testingButton = QtWidgets.QPushButton("Loop Testing", self)
        # Position des Buttons festlegen
        self.testingButton.setGeometry(600, 10, 90, 25)  # Beispielposition und -größe
        # Verbinden Sie den Button mit der start_testing-Funktion
        self.testingButton.clicked.connect(self.start_testing)
# testing button end

        self.update_ui()

        device_name: str | None = self._try_get_device_name()
        if not self.dummy and device_name:
            self.comboBox.addItem(device_name)
        self.storage = TransmitResultStorage()

        self.make_settings_btn(self.settingsButton)

    def _try_get_device_name(self) -> str | None:
        """Safely query the hardware for its device name.

        The helper catches :class:`STARAPIError` instances so the rest of the
        delayed initialization can finish without polluting the logs with the
        large stack traces previously emitted from ``plugin.py``.

        :return: The name reported by the device or ``None`` when unavailable.
        """

        if self.spw is None:
            logger.warning(
                "BrickMk4Widget._try_get_device_name() called before hardware binding was established."
            )
            return None

        try:
            return self.spw.getDeviceName()
        except STARAPIError as err:
            logger.error("Unable to query BrickMk4 device name: %s", err)
            return None
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Unexpected failure while querying the BrickMk4 device name.")
            return None



    def load_dummy(self):
        """
        loads dummy state from file, determined and written in hwmodules spacewire_brick_mk4.py

        dummy True means no connected device, but UI shows anyway with limited functionality for demonstration purpose
        """
        pass
    
        with open('dummymode.json', 'rt') as f:
            data = json.load(f)
        self.dummy = data["dummymode"]

    def update_ui(self):
        """
        updates ui to disable or enable functionality depending on whether dummy_mode is on or off
        """
        self.load_dummy()

        if self.dummy:
            state = False
            self.comboBox.clear()
            self.comboBox.addItem("SpaceWire Brick Mk4 Dummy")
        else:
            state = True
            self.comboBox.setItemText(0, self.spw.getDeviceName())
        print(f"{self.dummy=} {state=}")

        self.FreqSet.setEnabled(state)
        self.settingsButton.setEnabled(state)
        self.pushButton_Transmit.setEnabled(state)
        self.testingButton.setEnabled(state)
        self.pushButton_preDefinedData.setEnabled(state)
        self.pushButton_File.setEnabled(state)

    def resetDevice(self):
        self.spw.spw_resetDevice()
        self.set_to_default_settings()
        self.getFrequency()

        self.update_ui()
        return

    def simpleTransfer(self):
        # Create SpaceWire address.
        tmpPacketDataBuffer = []
        self.clearPacketDataBuffer()
        buffer_length = self.connection.spw_packet_size.value
        tmpPacketDataBuffer = [random.randint(0, 255) for _ in range(buffer_length)]
        self.appendToPacketDataBuffer(tmpPacketDataBuffer)
        print("arbitary Buffer with settings packet size loaded")

    def fileTransfer(self):
        self.clearPacketDataBuffer()
        selected_file = ""
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setWindowTitle("Select File")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                selected_file = file_paths[0]
                self.selectedFileLabel.setText(f"Selected File: {selected_file}")

        print(f"selected file is: {selected_file}")

        if selected_file:
            with open(selected_file, 'r') as file_:
                data_as_string = file_.read()

            cleanedText = self.filterInput(data_as_string)
            bytesList = bytes.fromhex(cleanedText)
            intList = list(bytesList)
            self.appendToPacketDataBuffer(intList)
            print("FileData Buffer loaded")

    def send(self):
        self.clearAddressBuffer()
        self.appendToAddressBuffer(self.connection.spw_dest_addr.value)
        if self.tabWidget.currentIndex() == 2:
            self.clearPacketDataBuffer()
            self.userData()

        self.spw.spw_send(self.packetDataBuffer,self.addressBuffer)

    def displayResults(self, Transmitresult, dataThroughPut, totalDuration, receivedPackage):
        self.TransmitResultLabel.setText(f"Transmit Result: {Transmitresult}")
        self.TimeNeededLabel.setText(f"Time Needed: {totalDuration} Microseconds")
        self.DataThroughPutlabel.setText(f"Data Through Put: {dataThroughPut} Mbit/s")
        self.transmittedLengthLabel.setText(f"Transmitted Payload Length: {len(self.packetDataBuffer)} Bytes")
        self.receivedLengthLabel.setText(f"Received Payload Length: {len(receivedPackage)} Bytes")
        self.printReceivedPackage(receivedPackage)

    def printReceivedPackage(self, receivedPackage):
        hex_strings = []

        if len(receivedPackage) > 100:
            receivedPackage = receivedPackage[:100]

        for packetByte in receivedPackage:
            # Convert each byte to a hex string and append to the list
            # [2:] to remove the '0x' prefix, zfill(2) to ensure two characters
            hex_strings.append(hex(packetByte)[2:].zfill(2))

        # Join all hex strings with a space in between each
        hex_string_with_spaces = ' '.join(hex_strings)

        # Insert the complete hex string into the QPlainTextEdit widget
        self.plainTextEdit.clear()
        self.plainTextEdit.insertPlainText(hex_string_with_spaces + " ")

    def userData(self):
        input = self.userDataTextEdit.toPlainText()
        if not input:
            print("Keine Eingabe gefunden.")
            return []
        cleanedText = self.filterInput(input)
        # Division of the text into two-line segments and conversion into bytes
        bytesList = bytes.fromhex(cleanedText)
        intList = list(bytesList)
        self.appendToPacketDataBuffer(intList)

    def filterInput(self, input):
        # Removal of non-hexadecimal characters
        cleanedText = ''.join(filter(lambda x: x in '0123456789abcdefABCDEF', input))
        if len(cleanedText) % 2 != 0:
            cleanedText += '0'
        return cleanedText

    def setFrequency(self):
        self.spw.spw_setTransmitSignallingRate(self.connection.spw_Link_1_output_clock_rate.value, 1)
        self.spw.spw_setTransmitSignallingRate(self.connection.spw_Link_2_output_clock_rate.value, 2)
        self.getFrequency()

    def getFrequency(self):
        transmitClockLink_1, transmitClockLink_2 = self.spw.spw_getTransmitSignallingRate()
        self.link_1_freq.setText(f"Link 1 Signaling Rate: {transmitClockLink_1} Mbps")
        self.link_2_freq.setText(f"Link 2 Signaling Rate: {transmitClockLink_2} Mbps")

    def getTransmitChannelNumber(self) ->int:
        return self.connection.spw_trans_channel.value

    def getReceiveChannelNumber(self) ->int:
        return self.connection.spw_receive_channel.value

    def buttonMultiplePacket(self,b):
        if b:
            self.spw.spw_setMultiplePacket(True)
        else:
            self.spw.spw_setMultiplePacket(False)

    def appendToPacketDataBuffer(self, data):
        with self.writeOutLock:
            self.packetDataBuffer.extend(data)

    def clearPacketDataBuffer(self):
        with self.writeOutLock:
            self.packetDataBuffer.clear()

    def appendToAddressBuffer(self, address):
        with self.writeOutLock:
            self.addressBuffer.append(address)

    def clearAddressBuffer(self):
        with self.writeOutLock:
            self.addressBuffer.clear()

    def start_testing(self):
        print("star_testing called")
        testPacketSizes = list(range(0,512000,1000))
        for packetSizes in testPacketSizes:
            tmpPacketDataBuffer = []
            self.clearPacketDataBuffer()
            tmpPacketDataBuffer = [random.randint(0, 255) for _ in range(packetSizes)]
            self.appendToPacketDataBuffer(tmpPacketDataBuffer)
            self.send_testing()
            # TODO Check if this should really be blocking the main thread
            self.spw.spw_waitEvent()
        print("testing done")

    def send_testing(self):
        self.clearAddressBuffer()
        self.appendToAddressBuffer(self.connection.spw_dest_addr.value)
        self.spw.spw_send(self.packetDataBuffer,self.addressBuffer)


VERSION = 1
NAME = "SpaceWire Testing"
BACKGROUND_TASKS = [RequirePlugins]
