"""
BrickMk4 Service 1 Plugin
-------------------------

Implements the logic for the DHU Simulator (Service 1) screen.
This plugin manages interaction between the GUI (defined in `service1.ui`)
and the SpaceWire Brick Mk4 hardware.

Main responsibilities:
    - Load and bind the UI layout to GUI controls.
    - Build and send CCSDS/PUS TM packets over the SpaceWire interface.
    - Receive and parse telemetry packets using `parse_tm_packet`.
    - Update GUI labels and status fields with parsed results.
    - Support "dummy mode" operation (for offline demos or tests).

Classes:
    RequirePlugins:
        Declares plugin dependencies (SpaceWireConnection and BrickMk4).

    BrickMk4Service1Widget:
        Main GUI widget implementing the Simulator logic, event handling,
        and hardware interaction.
"""

from gspy_egse.gui.utils.pus_parser import parse_tm_packet
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from pathlib import Path
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

from importlib.resources import files, as_file  # stdlib, Python ≥3.9

pkg = "gspy_egse.gui.ui"
ui_name = "service1.ui"


class RequirePlugins(WidgetWithExtension): #background task is super important
    """
    Declares required plugins and hardware extensions.

    Ensures that this widget only loads if both a valid
    SpaceWire connection and a BrickMk4 hardware module
    are available.
    """
    def __init__(self, *args, **kwargs):
        """Register the dependency list with the plugin base class."""

        super().__init__(*args, ext_cls=SpaceWireConnection, identifier="_", sub_exts=[
            BrickMk4
        ], **kwargs)

    def _init(self) -> None:
        """Expose an initialization hook expected by the plugin loader."""

        # Cache the dependency information for introspection or debugging use.
        self._required_extensions: list[type] = [SpaceWireConnection, BrickMk4]


class BrickMk4Service1Widget(WidgetWithExtension, Recordable):
    """
    GUI controller for the DHU Simulator Service 1.

    This widget links the user interface (`service1.ui`) with
    the backend logic for sending and receiving TM packets
    through the SpaceWire Brick Mk4 hardware interface.

    Attributes:
        spw (BrickMk4_HW_Transmit): Hardware driver instance.
        connection (SpaceWireConnection): Active SpaceWire connection.
        packetDataBuffer (list[int]): Outgoing packet data buffer.
        addressBuffer (list[int]): Destination address buffer.
        dummy (bool): If True, enables offline demonstration mode.
    """

    def __init__(self, *args, **kwargs):
        """Initialize widget and register it as a non-singleton SpaceWire plugin."""
        self.spw, self.connection = (None,) * 2
        super().__init__(*args, plugin_name="SpaceWire", ext_cls=SpaceWireConnection, singleton=False, **kwargs)

    def _init(self) -> None:
        """Prepare default attributes that are populated during delayed initialization."""

        # Buffers and locks are defined upfront to prevent attribute lookup failures.
        self.addressBuffer: list[int] = []
        self.packetDataBuffer: list[int] = []
        self.writeOutLock: threading.Lock | None = None
        self.dummy: bool = False
        self.storage: TransmitResultStorage | None = None
        self._step_counter: int = 0

    def _delay_init(self, extension=None, _=False):
        """
        Deferred initialization executed once the SpaceWire extension is available.

        Loads the UI from the `.ui` resource file, connects button signals
        to command handlers, and initializes communication buffers.
        """
        self.addressBuffer = []
        self.packetDataBuffer = []
        self.inherit_settings_from_parent(extension)
        self.connection = extension
        self.writeOutLock = threading.Lock()
        print(f"connection for BrickMk4 is: {extension}")
        self.spw = self.connection.hardware
        
        ui_res = files(pkg).joinpath(ui_name)
        with as_file(ui_res) as ui_path:
            self.ui = uic.loadUi(str(ui_path), self)
        # self.ui = uic.loadUi("gspy_egse/gui/ui/service1.ui", self)
        self._step_counter = 0

        # The UI historically defined a button named "FreqSet".  Store a guarded
        # reference so later logic can safely enable/disable the control even if
        # the widget is absent in legacy UI versions.
        self.FreqSet: QtWidgets.QWidget | None = getattr(self, "FreqSet", None)

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
        Load dummy mode configuration from 'dummymode.json'.

        When dummy mode is True, no hardware is required, and
        limited UI functionality is enabled for demonstration.
        """
        pass
        with open('dummymode.json', 'rt') as f:
            data = json.load(f)
        self.dummy = data["dummymode"]

    def _build_tm_packet(self, subservice: int, step_id: int | None = None) -> bytes:
        """
        Construct a complete CCSDS + PUS telemetry (TM) packet.

        This method builds a binary packet that follows the **CCSDS Space Packet Protocol**
        and the **ECSS PUS-C (Packet Utilisation Standard)** conventions. The resulting
        byte array is ready to be transmitted over the SpaceWire link to the Brick Mk4
        hardware. Each packet consists of:
        
        +--------------------------------------------------------------+
        | CCSDS Primary Header (6 bytes)                               |
        |   version=0, type=TM, sec_hdr_flag=1, apid=0x321, ...        |
        +--------------------------------------------------------------+
        | PUS TM Header (4 bytes)                                      |
        |   pus_version=1, service_type=1, subservice=1/3/5/7, src=1   |
        +--------------------------------------------------------------+
        | Payload (optional, e.g., step_id for subservice 5)           |
        +--------------------------------------------------------------+

        1. **CCSDS Primary Header** — 6 bytes  
           Defines general packet properties (version, type, APID, sequence control, and length):
           - `version` (3 bits): Packet version number (0 for standard CCSDS).
           - `pkt_type` (1 bit): 0 = Telemetry (TM), 1 = Telecommand (TC).
           - `sec_hdr_flag` (1 bit): Indicates the presence of a secondary header (set to 1 here).
           - `apid` (11 bits): Application Process ID (0x321 identifies the Brick Mk4 service).
           - `seq_flags` (2 bits): Sequence flags (3 = standalone packet, no segmentation).
           - `seq_count` (14 bits): Sequence counter (currently fixed to 1).
           - `pkt_length` (16 bits): Length of the remaining packet content minus 1.

        2. **PUS Telemetry Header** — 4 bytes  
           Defines the PUS structure and the TM service/subservice:
           - `pus_version` (1 byte): Set to 1 for PUS-C.
           - `service_type` (1 byte): Fixed to 1 → “Service 1: Request Verification”.
           - `service_subtype` (1 byte): Defined by the `subservice` argument (e.g., 1, 3, 5, 7).
           - `source_id` (1 byte): Set to 1 (identifier of the originating subsystem).

        3. **Payload** — Variable length  
           For subservice 5 (`SUBSERVICE_SUCCESSFUL_PROGRESS`), a single byte payload
           containing the `step_id` is included. For other subservices, the payload is empty.

        Args:
            subservice (int):  
                The PUS subservice identifier that defines the meaning of the packet.  
                Expected values:
                - 1 → TM[1,1] Acceptance Successful  
                - 3 → TM[1,3] Start Successful  
                - 5 → TM[1,5] Progress (includes `step_id`)  
                - 7 → TM[1,7] Completion Successful  

            step_id (Optional[int]):  
                Step counter byte included only for subservice 5 packets.  
                Used to track progress within a running procedure.

        Returns:
            bytes:  
                Fully assembled telemetry packet in binary format ready for SpaceWire transmission.

        Example:
            >>> pkt = self._build_tm_packet(subservice=5, step_id=12)
            >>> list(pkt)
            [0, 49, 192, 1, 0, 4, 1, 1, 5, 1, 12]

        Notes:
            - The CCSDS primary header ensures compatibility with standard space
              communication protocols.
            - The PUS header encodes service/subservice metadata used by the receiving system
              to interpret the telemetry.
            - This implementation assumes fixed-length primary and secondary headers,
              without additional time fields or data field headers.
        """

        # === CCSDS PRIMARY HEADER (6 bytes) ===
        # Each of these fields defines basic packet-level information.
        version = 0             
        pkt_type = 0
        sec_hdr_flag = 1
        apid = 0x321
        seq_flags = 3
        seq_count = 1

        # Combine high/low bytes of CCSDS header words.
        # first16 -> version, type, header flag, and APID
        first16 = (version << 13) | (pkt_type << 12) | (sec_hdr_flag << 11) | apid
        # second16 -> sequence control information
        second16 = (seq_flags << 14) | (seq_count & 0x3FFF)

        # Assemble the 6-byte primary header
        header = [
            (first16 >> 8) & 0xFF, first16 & 0xFF,
            (second16 >> 8) & 0xFF, second16 & 0xFF,
            0, 0
        ]

        # === PUS TM HEADER (4 bytes) ===
        # Defines the PUS service/subservice and source.
        pus_header = [
            1,              # PUS version (1 = PUS-C)
            1,              # Service type = 1 (Request Verification)
            subservice,     # Service subtype (1, 3, 5, or 7)
            1   
                                    # Source ID (subsystem identifier)
        ]

        # === PAYLOAD (optional) ===
        # For subservice 5 (Progress), append a one-byte step ID.  
        payload = []
        if subservice == 5 and step_id is not None:
            payload = [step_id & 0xFF]

        # === LENGTH CALCULATION ===
        # Total length of the secondary header + payload minus one,
        # as required by the CCSDS specification.
        total_len = len(pus_header) + len(payload)
        pkt_len = total_len - 1
        
        # Update the last two bytes of the primary header (packet length field)
        header[4] = (pkt_len >> 8) & 0xFF
        header[5] = pkt_len & 0xFF

        # === FINAL PACKET ASSEMBLY ===
        # Concatenate all components into a single byte array.
        # Order: [CCSDS header | PUS header | payload]
        return bytes(header + pus_header + payload)

    def _prepare_and_send(self, subservice: int):
        """
        Prepare and transmit a Telemetry (TM) packet based on user interaction.

        This function is triggered **whenever one of the simulator buttons is pressed**.
        Each button corresponds to a different PUS Service 1 subservice, as defined
        during widget initialization:

            - `pushButton`   → TM[1,1]  (Acceptance Success)
            - `pushButton_2` → TM[1,3]  (Start Success)
            - `pushButton_3` → TM[1,5]  (Progress, includes a step counter)
            - `pushButton_4` → TM[1,7]  (Completion Success)

        When a button is clicked, Qt invokes this function with the corresponding
        `subservice` argument (1, 3, 5, or 7). The function then builds the TM packet,
        fills transmission buffers, and sends it through the SpaceWire interface.

        Args:
            subservice (int): The PUS subservice ID that identifies the type of TM
                            packet to be sent. For subservice 5, a step counter
                            is automatically appended.

        Behavior:
            - For subservice 5 (Progress), the `step_id` is incremented cyclically
            on every call (0–255).
            - The function clears and updates both the data and address buffers
            before sending the new packet.
            - The final transmission is performed by the BrickMk4 hardware via
            `self.spw.spw_send()`.

        Example:
            User clicks "Progress" → TM[1,5] button → this method builds and sends
            a TM packet with the current step counter.

        """
        step = None

        # For subservice 5 (Progress), include a cyclic step counter in the payload.
        if subservice == 5:
            step = self._step_counter
            self._step_counter = (self._step_counter + 1) % 256

        # Build the CCSDS + PUS packet
        pkt = self._build_tm_packet(subservice, step)

        # Clear old data and load the new packet into the transmission buffer
        self.clearPacketDataBuffer()
        self.appendToPacketDataBuffer(list(pkt))

        # Update the destination address buffer
        self.clearAddressBuffer()
        self.appendToAddressBuffer(self.connection.spw_dest_addr.value)

        # Transmit the packet through the SpaceWire link
        self.spw.spw_send(self.packetDataBuffer, self.addressBuffer)

    def update_ui(self):
        """Enable or disable UI controls depending on whether dummy mode is active."""
        self.load_dummy()

        if self.dummy:
            state = False
            # self.comboBox.clear()
            # self.comboBox.addItem("SpaceWire Brick Mk4 Dummy")
        else:
            state = True
            # self.comboBox.setItemText(0, self.spw.getDeviceName())
        print(f"{self.dummy=} {state=}")

        # Only toggle the frequency control when it is available in the UI to
        # prevent `AttributeError` in legacy deployments.
        if self.FreqSet is not None:
            self.FreqSet.setEnabled(state)
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
        """
        Display transmission statistics and parsed telemetry results.

        This method is **automatically invoked when the SpaceWire interface receives data**
        from the connected BrickMk4 hardware. The signal–slot connection is established
        during initialization:

            self.spw.spw.spw_raw.signalEmitter.dataReceived.connect(self.displayResults)

        Therefore, the SpaceWire backend calls this function whenever a new telemetry
        packet (TM) is received after a transmission.

        Args:
            Transmitresult (str): Result status of the last transmission (e.g., "OK" or "Error").
            dataThroughPut (float): Effective data throughput in Mbit/s.
            totalDuration (float): Duration of the transmission in microseconds.
            receivedPackage (list[int]): Raw list of received bytes representing a TM packet.

        Behavior:
            - Updates GUI labels with transmission metrics such as duration and throughput.
            - Parses the received TM packet using `parse_tm_packet()`.
            - Displays key CCSDS/PUS header fields and any decoded step information
            in the text console (`plainTextEdit`).
            - If parsing fails, a human-readable hex dump of the packet is shown instead.

        Signal Origin:
            The `dataReceived` signal is emitted by:
                BrickMk4.spw.spw_raw.signalEmitter.dataReceived
            where `BrickMk4` is the low-level SpaceWire hardware module integrated
            with this plugin.

        Example:
            When a TM[1,5] Progress packet is received from the hardware,
            this method decodes it, prints its contents, and displays
            "StepID: X" in the GUI console.

        """
        # Update GUI fields with numeric transmission data
        self.TransmitResultLabel.setText(f"Transmit Result: {Transmitresult}")
        self.TimeNeededLabel.setText(f"Time Needed: {totalDuration} Microseconds")
        self.DataThroughPutlabel.setText(f"Data Through Put: {dataThroughPut} Mbit/s")
        self.transmittedLengthLabel.setText(f"Transmitted Payload Length: {len(self.packetDataBuffer)} Bytes")
        self.receivedLengthLabel.setText(f"Received Payload Length: {len(receivedPackage)} Bytes")

        try:
            # Try to parse the received TM packet (CCSDS + PUS)
            parsed = parse_tm_packet(receivedPackage)
            lines = []

            # Extract and display key header information
            p = parsed.primary
            ph = parsed.pus
            lines.append(f"CCSDS: ver={p.version}, type={p.pkt_type}, sec={p.sec_hdr_flag}, "
                         f"APID={p.apid}, seq_flags={p.seq_flags}, seq={p.seq_count}, len={p.pkt_length}")
            lines.append(
                f"PUS: ver={ph.pus_version}, svc={ph.service_type}, ssvc={ph.service_subtype}, src={ph.source_id}")
            
            # Add summary and optional Step ID information
            if parsed.summary:
                m = re.search(r'\bTM\[\s*\d+\s*,\s*\d+\s*\]', parsed.summary)
                if m:
                    lines.append(m.group(0))

            if parsed.step_id is not None:
                lines.append(f"StepID: {parsed.step_id}")

            # Write the parsed information to the GUI console

            self.plainTextEdit.clear()
            self.plainTextEdit.insertPlainText("\n".join(lines))

        except Exception as e:
            # If parsing fails, show an error and a hex dump of the first 100 bytes
            self.plainTextEdit.clear()
            self.plainTextEdit.insertPlainText(
                "Parse failed: " + str(e) + "\n" +
                "HEX: " + " ".join(f"{b:02X}" for b in receivedPackage[:100]) +
                (" …" if len(receivedPackage) > 100 else "")
            )

    def printReceivedPackage(self, receivedPackage):
        """Display the first 100 bytes of the received packet as a hex string in the UI."""
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
        """Return the current SpaceWire transmit channel number."""
        return self.connection.spw_trans_channel.value

    def getReceiveChannelNumber(self) ->int:
        """Return the current SpaceWire receive channel number."""
        return self.connection.spw_receive_channel.value

    def buttonMultiplePacket(self,b):
        """Enable or disable multiple-packet transmission mode."""
        if b:
            self.spw.spw_setMultiplePacket(True)
        else:
            self.spw.spw_setMultiplePacket(False)

    def appendToPacketDataBuffer(self, data):
        """Thread-safe append to the outgoing packet data buffer."""
        with self.writeOutLock:
            self.packetDataBuffer.extend(data)

    def clearPacketDataBuffer(self):
        """Thread-safe clear of the outgoing packet data buffer."""
        with self.writeOutLock:
            self.packetDataBuffer.clear()

    def appendToAddressBuffer(self, address):
        """Thread-safe append to the destination address buffer."""
        with self.writeOutLock:
            self.addressBuffer.append(address)

    def clearAddressBuffer(self):
        """Thread-safe clear of the destination address buffer."""
        with self.writeOutLock:
            self.addressBuffer.clear()

    def start_testing(self):
        """
        Perform automated transmission tests over a range of packet sizes.

        Generates random payloads and sends them sequentially, waiting for
        device acknowledgment between each transmission.
        """
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
        """Send the prepared packet buffer through the SpaceWire interface."""
        self.clearAddressBuffer()
        self.appendToAddressBuffer(self.connection.spw_dest_addr.value)
        self.spw.spw_send(self.packetDataBuffer,self.addressBuffer)


VERSION = 1
NAME = "Simulator"
BACKGROUND_TASKS = [RequirePlugins]
