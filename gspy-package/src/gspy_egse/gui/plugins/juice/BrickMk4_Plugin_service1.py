from gspy_egse.gui.utils.pus_parser import parse_tm_packet
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from pathlib import Path
from contextlib import suppress
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from typing import *
import threading
import random
import time
import json
import re

from gspy_egse.gui.plugins.juice.spacewire import SpaceWireConnection
from gspy_egse.gui.utils.plugin import WidgetWithExtension
from gspy_egse.gui.utils.widget import call_in_main_thread, delay_in_main_thread, async_in_main_thread, select_file, ActivationListener
from gspy_egse.gui.utils.recorder import Recordable
from gspy_egse.gui.hardware_modules.juice_lib.BrickMk4_HW_Transmit import BrickMk4
from gspy_egse.gui.utils.transmitResultStorage import TransmitResultStorage

try:
    from PIL import Image
except ImportError:
    Image = None  # or handle gracefully


class RequirePlugins(WidgetWithExtension): #background task is super important
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ext_cls=SpaceWireConnection, identifier="_", sub_exts=[
            BrickMk4
        ], **kwargs)


class BrickMk4Service1Widget(WidgetWithExtension, Recordable):
    """
    :type spw: BrickMk4_HW_Transmit
    :type connection: SpaceWireConnection
    """
    def __init__(self, *args, **kwargs):
        self.spw, self.connection = (None,) * 2
        super().__init__(*args, plugin_name="SpaceWire", ext_cls=SpaceWireConnection, singleton=False, **kwargs)

    def _delay_init(self, extension=None, _=False):
        self.addressBuffer = []
        self.packetDataBuffer = []
        self.inherit_settings_from_parent(extension)
        self.connection = extension
        self.writeOutLock = threading.Lock()
        print(f"connection for BrickMk4 is: {extension}")
        self.spw = self.connection.hardware
        self.ui = uic.loadUi("src/gspy_egse/gui/ui/service1.ui", self)
        self._step_counter = 0

        self.pushButton.clicked.connect(lambda: self._prepare_and_send(1))  # TM[1,1]
        self.pushButton_2.clicked.connect(lambda: self._prepare_and_send(3))  # TM[1,3]
        self.pushButton_3.clicked.connect(lambda: self._prepare_and_send(5))  # TM[1,5]
        self.pushButton_4.clicked.connect(lambda: self._prepare_and_send(7))  # TM[1,7]
        self.make_settings_btn(self.settingsButton)

        # self.FreqSet.clicked.connect(self.setFrequency)
        self.resetButton.clicked.connect(self.resetDevice)
        self.spw.spw.spw_raw.signalEmitter.dataReceived.connect(self.displayResults)

        # self.getFrequency()
        self.update_ui()

        deviceName = self.spw.getDeviceName()
        if not self.dummy:
            self.comboBox.addItem(deviceName)
        self.storage = TransmitResultStorage()



    def load_dummy(self):
        """
        loads dummy state from file, determined and written in hwmodules spacewire_brick_mk4.py

        dummy True means no connected device, but UI shows anyway with limited functionality for demonstration purpose
        """
        pass
        with open('dummymode.json', 'rt') as f:
            data = json.load(f)
        self.dummy = data["dummymode"]

    def _build_tm_packet(self, subservice: int, step_id: int | None = None) -> bytes:
        version = 0
        pkt_type = 0
        sec_hdr_flag = 1
        apid = 0x321
        seq_flags = 3
        seq_count = 1

        first16 = (version << 13) | (pkt_type << 12) | (sec_hdr_flag << 11) | apid
        second16 = (seq_flags << 14) | (seq_count & 0x3FFF)
        header = [
            (first16 >> 8) & 0xFF, first16 & 0xFF,
            (second16 >> 8) & 0xFF, second16 & 0xFF,
            0, 0
        ]

        pus_header = [1, 1, subservice, 1]  # PUS ver=1, svc=1, ssvc=sub, src=1
        payload = []
        if subservice == 5 and step_id is not None:
            payload = [step_id & 0xFF]

        total_len = len(pus_header) + len(payload)
        pkt_len = total_len - 1
        header[4] = (pkt_len >> 8) & 0xFF
        header[5] = pkt_len & 0xFF

        return bytes(header + pus_header + payload)

    def _prepare_and_send(self, subservice: int):
        step = None
        if subservice == 5:
            step = self._step_counter
            self._step_counter = (self._step_counter + 1) % 256

        pkt = self._build_tm_packet(subservice, step)
        self.clearPacketDataBuffer()
        self.appendToPacketDataBuffer(list(pkt))

        self.clearAddressBuffer()
        self.appendToAddressBuffer(self.connection.spw_dest_addr.value)
        self.spw.spw_send(self.packetDataBuffer, self.addressBuffer)

    def update_ui(self):
        """
        updates ui to disable or enable functionality depending on whether dummy_mode is on or off
        """
        self.load_dummy()

        if self.dummy:
            state = False
            # self.comboBox.clear()
            # self.comboBox.addItem("SpaceWire Brick Mk4 Dummy")
        else:
            state = True
            # self.comboBox.setItemText(0, self.spw.getDeviceName())
        print(f"{self.dummy=} {state=}")

        # self.FreqSet.setEnabled(state)
        self.settingsButton.setEnabled(state)
        self.pushButton.setEnabled(state)
        self.pushButton_2.setEnabled(state)
        self.pushButton_3.setEnabled(state)
        self.pushButton_4.setEnabled(state)

    def resetDevice(self):
        self.spw.spw_resetDevice()
        self.set_to_default_settings()
        # self.getFrequency()

        self.update_ui()
        return

    def displayResults(self, Transmitresult, dataThroughPut, totalDuration, receivedPackage):
        self.TransmitResultLabel.setText(f"Transmit Result: {Transmitresult}")
        self.TimeNeededLabel.setText(f"Time Needed: {totalDuration} Microseconds")
        self.DataThroughPutlabel.setText(f"Data Through Put: {dataThroughPut} Mbit/s")
        self.transmittedLengthLabel.setText(f"Transmitted Payload Length: {len(self.packetDataBuffer)} Bytes")
        self.receivedLengthLabel.setText(f"Received Payload Length: {len(receivedPackage)} Bytes")

        try:
            parsed = parse_tm_packet(receivedPackage)
            lines = []
            p = parsed.primary
            ph = parsed.pus
            lines.append(f"CCSDS: ver={p.version}, type={p.pkt_type}, sec={p.sec_hdr_flag}, "
                         f"APID={p.apid}, seq_flags={p.seq_flags}, seq={p.seq_count}, len={p.pkt_length}")
            lines.append(
                f"PUS: ver={ph.pus_version}, svc={ph.service_type}, ssvc={ph.service_subtype}, src={ph.source_id}")
            if parsed.summary:
                m = re.search(r'\bTM\[\s*\d+\s*,\s*\d+\s*\]', parsed.summary)
                if m:
                    lines.append(m.group(0))

            if parsed.step_id is not None:
                lines.append(f"StepID: {parsed.step_id}")

            self.plainTextEdit.clear()
            self.plainTextEdit.insertPlainText("\n".join(lines))

        except Exception as e:
            self.plainTextEdit.clear()
            self.plainTextEdit.insertPlainText(
                "Parse failed: " + str(e) + "\n" +
                "HEX: " + " ".join(f"{b:02X}" for b in receivedPackage[:100]) +
                (" …" if len(receivedPackage) > 100 else "")
            )

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


    # def setFrequency(self):
    #     self.spw.spw_setTransmitSignallingRate(self.connection.spw_Link_1_output_clock_rate.value, 1)
    #     self.spw.spw_setTransmitSignallingRate(self.connection.spw_Link_2_output_clock_rate.value, 2)
    #     self.getFrequency()

    # def getFrequency(self):
    #     transmitClockLink_1, transmitClockLink_2 = self.spw.spw_getTransmitSignallingRate()
    #     self.link_1_freq.setText(f"Link 1 Signaling Rate: {transmitClockLink_1} Mbps")
    #     self.link_2_freq.setText(f"Link 2 Signaling Rate: {transmitClockLink_2} Mbps")

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
NAME = "Simulator"
BACKGROUND_TASKS = [RequirePlugins]
