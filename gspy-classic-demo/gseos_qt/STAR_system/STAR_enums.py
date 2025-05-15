""" Contains the enums used throughout STAR-System.

Brief:\n
    Contains the enums used throughout STAR-System.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

from enum import IntEnum


class STAR_TRANSFER_STATUS(IntEnum):
    """Possible states a transfer operation can be in."""

    STAR_TRANSFER_STATUS_NOT_STARTED = 0
    """Not yet started. When a transfer operation is created, this will be its status."""

    STAR_TRANSFER_STATUS_STARTED = 1
    """Transfer has begun. When a transfer operation is submitted, this will be its status,
       until it has completed.
    """

    STAR_TRANSFER_STATUS_COMPLETE = 2
    """Transfer has completed.  Once a transmit operation has successfully
       transmitted all its traffic, or a receive operation has received all its
       requested traffic, this will be its status.
    """

    STAR_TRANSFER_STATUS_CANCELLED = 3
    """Transfer was cancelled.  When a transfer is cancelled by calling
       STAR_cancelTransferOperation(), this will be its status.
    """

    STAR_TRANSFER_STATUS_ERROR = 4
    """An error occurred while processing the transfer.  This will be the status
       of a transfer operation if there was an error creating it, submitting it,
       or there was an error while transmitting or receiving.
    """

class STAR_OPERATION_RESULT(IntEnum):
    """Result of a STAR-System operation (function call)."""

    STAR_ERROR = 0
    """The operation failed (did not succeed)."""

    STAR_SUCCESS = 1
    """The operation succeeded."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CONFIG_OP_RESULT(IntEnum):
    """Result of a STAR-System configuration operation (function call)."""

    STAR_SUCCESS = 0
    """The operation succeeded."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CHANNEL_DIRECTION(IntEnum):
    """Channel directions."""

    IN = 0x01
    """Channel will be used to receive traffic."""

    OUT = 0x02
    """Channel will be used to transmit traffic."""

    INOUT = IN | OUT
    """Channel will be used to both receive and transmit traffic."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_EOP_TYPE(IntEnum):
    """The different End of packet markers that may be present."""

    STAR_EOP_TYPE_INVALID = 0
    """Error occurred determining EOP type."""

    STAR_EOP_TYPE_EOP = 1
    """End of Packet marker."""

    STAR_EOP_TYPE_EEP = 2
    """Error End of Packet marker."""

    STAR_EOP_TYPE_NONE = 3
    """No End of Packet marker present."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CHANNEL_TYPE(IntEnum):
    """Channel types."""

    STAR_CHANNEL_TYPE_NOT_OPEN = 0
    """Not open."""

    STAR_CHANNEL_TYPE_DEVICE = 1
    """Attached to a device."""

    STAR_CHANNEL_TYPE_APPLICATION = 2
    """Attached to an application."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_BUS_TYPE(IntEnum):
    """The different types of bus that can be used to connect a SpaceWire device to a PC."""

    STAR_BUS_UNKNOWN = 0
    """The bus type of a device is unknown."""

    STAR_BUS_PCI = 1
    """The PCI bus type."""

    STAR_BUS_USB = 2
    """The USB bus type."""

    STAR_BUS_PCIE = 3
    """The PCI Express (PCIe) bus type."""

    STAR_BUS_TCP = 4
    """The TCP/IP bus type, used by Ethernet devices."""

    STAR_BUS_CPCI = 5
    """The cPCI bus type."""

    STAR_BUS_VIRTUAL = 255
    """The bus type for virtual devices."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_DEVICE_TYPE(IntEnum):
    """The different device types that are supported/handled by STAR-System."""

    STAR_DEVICE_UNKNOWN = 0
    """The "unknown" device type."""

    STAR_DEVICE_PCI = 1
    """The STAR-Dundee SpaceWire PCI-2 and cPCI device type."""

    STAR_DEVICE_ROUTER_USB = 2
    """The STAR-Dundee SpaceWire Router-USB device type."""

    STAR_DEVICE_USB_BRICK = 3
    """The STAR-Dundee SpaceWire-USB Brick device type."""

    STAR_DEVICE_LINK_ANALYSER = 4
    """The STAR-Dundee SpaceWire Link Analyser device type."""

    STAR_DEVICE_CONFORMANCE_TESTER = 5
    """The STAR-Dundee SpaceWire Conformance Tester device type."""

    STAR_DEVICE_IP_TUNNEL = 6
    """The STAR-Dundee SpaceWire IP-Tunnel device type."""

    STAR_DEVICE_ROUTER_MK2S = 7
    """The STAR-Dundee SpaceWire Router Mk2S device type."""

    STAR_DEVICE_PCI_MK2 = 8
    """The STAR-Dundee SpaceWire PCI Mk2 device type."""

    STAR_DEVICE_BRICK_MK2 = 9
    """The STAR-Dundee SpaceWire Brick Mk2 device type."""

    STAR_DEVICE_LINK_ANALYSER_MK2 = 10
    """The STAR-Dundee SpaceWire Link Analyser Mk2 device type."""

    STAR_DEVICE_PCIE = 11
    """The STAR-Dundee SpaceWire PCI Express device type."""

    STAR_DEVICE_RTC = 12
    """The STAR-Dundee SpaceWire RTC device type."""

    STAR_DEVICE_EGSE = 13
    """The STAR-Dundee SpaceWire EGSE device type."""

    STAR_DEVICE_CPCI_MK2 = 14
    """The STAR-Dundee SpaceWire cPCI Mk2 device type."""

    STAR_DEVICE_SPLT = 15
    """The STAR-Dundee SpaceWire Physical Layer Tester device type."""

    STAR_DEVICE_STAR_FIRE = 16
    """The STAR-Dundee STAR Fire device type."""

    STAR_DEVICE_WBS_II = 17
    """The STAR-Dundee Wide Band Spectrometer II device type."""

    STAR_DEVICE_RECORDER = 18
    """The STAR-Dundee SpaceWire Recorder device type."""

    STAR_DEVICE_BRICK_MK3 = 19
    """The STAR-Dundee SpaceWire Brick Mk3 device type."""

    STAR_DEVICE_TRAFFIC_GENERATOR = 20
    """The Shimafuji Traffic Generator device type."""

    STAR_DEVICE_PXI_INTERFACE = 21
    """The STAR-Dundee SpaceWire PXI Interface device type."""

    STAR_DEVICE_PXI_RMAP = 22
    """The STAR-Dundee SpaceWire PXI RMAP device type."""

    STAR_DEVICE_PXI_ROUTER_8 = 23
    """The STAR-Dundee SpaceWire PXI 8 port Router device type."""

    STAR_DEVICE_PXI_ROUTER_12 = 24
    """The STAR-Dundee SpaceWire PXI 12 port Router device type."""

    STAR_DEVICE_SPFIPCIE = 25
    """The STAR-Dundee SpaceFibre PCI Express device type."""

    STAR_DEVICE_STAR_FIRE_MK3 = 26
    """The STAR-Dundee STAR Fire Mk3 device type."""

    STAR_DEVICE_PCI_MK3 = 27
    """The STAR-Dundee SpaceWire PCI Mk3 device type."""

    STAR_DEVICE_LINK_ANALYSER_MK3 = 28
    """The STAR-Dundee SpaceWire Link Analyser Mk3 device type."""

    STAR_DEVICE_CONFORMANCE_TESTER_MK2 = 29
    """The STAR-Dundee SpaceWire Conformance Tester Mk2 device type."""

    STAR_DEVICE_EGSE_MK2 = 30
    """The STAR-Dundee SpaceWire EGSE Mk2 device type."""

    STAR_DEVICE_GBE_BRICK = 31
    """The STAR-Dundee SpaceWire GbE Brick device type."""

    STAR_DEVICE_STAR_ULTRA_PCIE = 32
    """The STAR-Dundee STAR-Ultra PCIe device type."""

    STAR_DEVICE_PXI_INTERFACE_MK2 = 33
    """The STAR-Dundee SpaceWire PXI Interface Mk2 device type."""

    STAR_DEVICE_PXI_RMAP_MK2 = 34
    """The STAR-Dundee SpaceWire PXI RMAP Mk2 device type."""

    STAR_DEVICE_PXI_ROUTER_MK2 = 35
    """The STAR-Dundee SpaceWire PXI Router Mk2 device type."""

    STAR_DEVICE_BRICK_MK4 = 36
    """The STAR-Dundee SpaceWire Brick Mk4 device type."""

    STAR_DEVICE_RECORDER_MK2 = 37
    """The STAR-Dundee SpaceWire Recorder Mk2 device type."""

    STAR_DEVICE_PCIE_MK2 = 38
    """The STAR-Dundee SpaceWire PCIe Mk2 device type."""

    # "Special" values
    STAR_DEVICE_CONFIG_SUPPORTED = 0x00fffffb
    """A device which is capable of being configured."""

    STAR_DEVICE_CONFIG_NOT_SUPPORTED = 0x00fffffc
    """A device which is not capable of being configured."""

    STAR_DEVICE_TX_RX_SUPPORTED = 0x00fffffd
    """A device which is capable of both transmitting and receiving packets."""

    STAR_DEVICE_TX_RX_NOT_SUPPORTED = 0x00fffffe
    """A device which is not capable of transmitting and receiving packets."""

    STAR_DEVICE_ALL = 0x00ffffff
    """All devices."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)


class STAR_DEVICE_CHIP_TYPE(IntEnum):
    """The different device chip types (IDs) that are supported/handled by STAR-System."""

    CFG_CID_ROUTER_ASIC = 0
    """SpaceWire Router ASIC and IP."""

    CFG_CID_ROUTER_USB = 1
    """Original SpaceWire Router-USB."""

    CFG_CID_USB_BRICK = 2
    """SpaceWire-USB Brick."""

    CFG_CID_FEIC = 4
    """The FEIC chip."""

    CFG_CID_ROUTER_USB_2 = 5
    """New SpaceWire Router-USB."""

    CFG_CID_PCIMK2 = 7
    """SpaceWire PCI Mk2."""

    CFG_CID_PCIE = 8
    """SpaceWire PCIe."""

    CFG_CID_RTC_OLD = 9
    """SpaceWire RTC."""

    CFG_CID_EGSE = 11
    """SpaceWire EGSE."""

    CFG_CID_STAR_FIRE = 12
    """STAR Fire."""

    CFG_CID_WBS_II = 14
    """WBS II."""

    CFG_CID_SPLT = 15
    """SpaceWire Physical Layer Tester."""

    CFG_CID_ROUTER_MK2S = 16
    """SpaceWire Router Mk2S."""

    CFG_CID_BRICK_MK2 = 17
    """SpaceWire Brick Mk2."""

    CFG_CID_RTC = 18
    """SpaceWire RTC (STAR-System)."""

    CFG_CID_BRICK_MK3 = 19
    """SpaceWire Brick Mk3."""

    CFG_CID_HPPDSP = 20
    """HPPDSP."""

    CFG_CID_PXI_INTFC = 21
    """SpaceWire PXI Interface."""

    CFG_CID_PXI_RMAP = 22
    """SpaceWire PXI RMAP."""

    CFG_CID_PXI_ROUTER_8 = 23
    """SpaceWire PXI 8 Port Router."""

    CFG_CID_PXI_ROUTER_12 = 24
    """SpaceWire PXI 12 Port Router."""

    CFG_CID_SPFI_PXI_ROUTER = 25
    """SpaceFibre PXI Router."""

    CFG_CID_STAR_FIRE_MK3 = 26
    """STAR Fire Mk3."""

    CFG_CID_SPFI_PCIE = 27
    """SpaceWire PCI Mk3 **** NOTE : re-assigned chip ID, needs name change ****."""

    CFG_CID_GBE_BRICK = 28
    """SpaceWire GbE Brick - based on Brick Mk3."""

    CFG_CID_PXI_INTFC_MK2 = 29
    """SpaceWire PXI Interface Mk2."""

    CFG_CID_PXI_RMAP_MK2 = 30
    """SpaceWire PXI RMAP Mk2."""

    CFG_CID_PXI_ROUTER_MK2 = 31
    """SpaceWire PXI Router Mk2."""

    CFG_CID_BRICK_MK4 = 32
    """SpaceWire Brick Mk4."""

    CFG_CID_PCIE_MK2 = 33
    """SpaceWire PCIe Mk2."""

    CFG_CID_VHISSI = 0x80
    """VHiSSI."""

    CFG_CID_CASTOR = 0x81
    """CASTOR."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)


class STAR_CFG_DEVICE_TYPE(IntEnum):
    """Device types permitted within the network discovery register."""

    STAR_CFG_DEVICE_TYPE_ROUTER = 0
    """Router device."""

    STAR_CFG_DEVICE_TYPE_UNKNOWN = 1
    """Unknown device type."""

    STAR_CFG_DEVICE_TYPE_INVALID = 2
    """Invalid device type."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)


class STAR_CFG_TIMEOUT_MODE(IntEnum):
    """Timeout mode used by the router. This affects how blocked packets will be handled."""

    STAR_CFG_TIMEOUT_MODE_BLOCKING = 0
    """Blocking allowed.
       When blocking mode is enabled packets will wait forever to be routed
       unless the packet is routed to a port that is not started. In this case
       the packet will be discarded."""

    STAR_CFG_TIMEOUT_MODE_WATCHDOG = 1
    """Watchdog timer mode.
       When watchdog mode is enabled packets which are waiting to be routed at
       source ports will be discarded after the timeout period. Packet tails
       will also be discarded if the packet becomes blocked for the timeout
       period. In this case the packet will be ended with an EEP."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CFG_PORT_TIMEOUT(IntEnum):
    """The different time periods of port timeout."""

    STAR_CFG_PORT_TIMEOUT_100US = 0
    """60-80 microseconds [us]."""

    STAR_CFG_PORT_TIMEOUT_1MS = 1
    """~1.3 milliseconds [ms]."""

    STAR_CFG_PORT_TIMEOUT_10MS = 2
    """~10 milliseconds [ms]."""

    STAR_CFG_PORT_TIMEOUT_100MS = 3
    """~82 milliseconds [ms]."""

    STAR_CFG_PORT_TIMEOUT_1S = 4
    """~1.3 seconds [s]."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CFG_BRICK_MK3_PULSE_FREQ(IntEnum):
    """Defines frequencies that can be used by the global pulse generator."""

    STAR_CFG_BRICK_MK3_PULSE_FREQ_1 = 0
    """1 Hz."""

    STAR_CFG_BRICK_MK3_PULSE_FREQ_10 = 1
    """10 Hz."""

    STAR_CFG_BRICK_MK3_PULSE_FREQ_100 = 2
    """100 Hz."""

    STAR_CFG_BRICK_MK3_PULSE_FREQ_1000 = 3
    """1 KHz."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD(IntEnum):
    """Timestamps can be generated by either an external trigger signal or by an
       internal pulse generator. This enum defines different methods of
       timestamping that are available."""

    STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD_NONE = 0
    """No timestamp method."""

    STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD_EXTERNAL_TRIGGER = 1
    """External trigger used for timestamp sync."""

    STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD_PULSE_GENERATOR = 2
    """Internal pulse generator used for timestamp sync."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_DRIVER_TYPE(IntEnum):
    """Available driver types."""

    STAR_DRIVER_INVALID = 0
    """Invalid driver."""

    STAR_DRIVER_TYPE_USB = 1
    """USB driver."""

    STAR_DRIVER_TYPE_PCI = 2
    """PCI driver."""

    STAR_DRIVER_TYPE_TCPIP = 4
    """TCP/IP driver."""

    STAR_DRIVER_TYPE_VIRTUAL = 5
    """Virtual driver."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class SPW_ACTION(IntEnum):
    """Actions which can be preformed at specified periodic intervals."""

    SPW_TRANSMIT_PACKET = 0
    """Transmit a SpaceWire packet."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class SPW_ERROR(IntEnum):
    """Errors that can be injected onto the SpaceWire link."""

    SPW_ERROR_DISCONNECT = 1
    """Causes the SpaceWire link to disconnect.
       The link enters ErrorReset and the Data/Strobe outputs transition LOW."""

    SPW_ERROR_PARITY = 2
    """Inserts a parity error on the next SpaceWire character to be transmitted
       by flipping the parity bit."""

    SPW_ERROR_ESCAPE = 3
    """Transmits two escape characters in sequence."""

    SPW_ERROR_INSERT_FCT = 4
    """Sends an FCT character. This can be used to force FCT errors on the
       SpaceWire link."""

    SPW_ERROR_SUPPRESS_FCT = 5
    """Discards the next FCT character to be transmitted on the link. This can
       be used to simulate the loss of an FCT character."""

    SPW_ERROR_INCREMENT_CREDIT = 6
    """Increments the transmit credit available to send data by 8. This can be
       used to force a data overflow in the opposite end of the link, as too
       much data will be transmitted."""

    SPW_ERROR_DECREMENT_CREDIT = 7
    """Decrements the transmit credit count by 1. This can be used to reduce the
       rate at which data can be transmitted."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CFG_SPW_LINK_STATE(IntEnum):
    """The state of the interface state machine in the SpaceWire link."""

    STAR_CFG_SPW_LINK_STATE_ERROR_RESET = 0
    """Error Reset."""

    STAR_CFG_SPW_LINK_STATE_ERROR_WAIT = 1
    """Error Wait."""

    STAR_CFG_SPW_LINK_STATE_READY = 2
    """Ready."""

    STAR_CFG_SPW_LINK_STATE_STARTED = 3
    """Started."""

    STAR_CFG_SPW_LINK_STATE_CONNECTING = 4
    """Connecting."""

    STAR_CFG_SPW_LINK_STATE_RUN = 5
    """Run."""

    STAR_CFG_SPW_LINK_STATE_INVALID = 6
    """Invalid value."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_CFG_PORT_TYPE(IntEnum):
    """Port types for Routing devices."""

    STAR_CFG_PORT_TYPE_CONFIGURATION = 0
    """Configuration port."""

    STAR_CFG_PORT_TYPE_LINK = 1
    """SpaceWire Link port."""

    STAR_CFG_PORT_TYPE_EXTERNAL = 2
    """External port."""

    STAR_CFG_PORT_TYPE_INVALID = 3
    """Invalid value. This should never occur."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_TIMESTAMP_TYPE(IntEnum):
    """An enum used to define the different types of timestamps that can be received."""

    STAR_TIMESTAMP_TYPE_DATA = 0
    """Timestamp for data."""

    STAR_TIMESTAMP_TYPE_LINK_STATE = 1
    """Timestamp for link state event."""

    STAR_TIMESTAMP_TYPE_LINK_SPEED = 2
    """Timestamp for link speed event."""

    STAR_TIMESTAMP_TYPE_TIMECODE = 3
    """Timestamp for time-code."""

    STAR_TIMESTAMP_TYPE_ERROR = 4
    """Timestamp for error in data."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_TIMESTAMP_DIRECTION(IntEnum):
    """An enum used to define the direction of a timestamp."""

    STAR_TIMESTAMP_DIRECTION_TRANSMIT = 0
    """Timestamp is applied to transmitted data."""

    STAR_TIMESTAMP_DIRECTION_RECEIVE = 1
    """Timestamp is applied to received data."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_RECEIVE_MASK(IntEnum):
    """Flags used to determine what kind of stream items
       to receive on a receive operation."""

    STAR_RECEIVE_PACKETS = 1 << 0
    """STAR_SPACEWIRE_PACKET. See this structure in STAR_structures.py."""

    STAR_RECEIVE_CHUNKS = 1 << 1
    """STAR_DATA_CHUNK. See this structure in STAR_structures.py."""

    STAR_RECEIVE_TIMECODES = 1 << 2
    """STAR_TIMECODE. See this structure in STAR_structures.py."""

    STAR_RECEIVE_FCTS = 1 << 3
    """Flow control characters. Note that transmitting and receiving FCTs is not
       currently supported."""

    STAR_RECEIVE_NULL = 1 << 4
    """Null characters. Note that transmitting and receiving Nulls is not
       currently supported."""

    STAR_RECEIVE_LINK_STATE_EVENTS = 1 << 5
    """STAR_LINK_STATE_EVENT. See this structure in STAR_structures.py."""

    STAR_RECEIVE_LINK_SPEED_EVENTS = 1 << 6
    """STAR_LINK_SPEED_EVENT. See this structure in STAR_structures.py."""

    STAR_RECEIVE_TIMESTAMP_EVENTS = 1 << 7
    """STAR_TIMESTAMP_EVENT. See this structure in STAR_structures.py."""

    STAR_RECEIVE_BROADCAST_MESSAGES = 1 << 8
    """STAR_BROADCAST_MESSAGE. See this structure in STAR_structures.py."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_STREAM_ITEM_TYPE(IntEnum):
    """The different objects that are represented as stream items.
       Used by STAR_STREAM_ITEM to show what kind of item it is wrapping."""

    STAR_STREAM_ITEM_TYPE_SPACEWIRE_PACKET = 0
    """Packet, see STAR_SPACEWIRE_PACKET in STAR_structures.py."""

    STAR_STREAM_ITEM_TYPE_TIMECODE = 1
    """Time-code, see STAR_TIMECODE in STAR_structures.py."""

    STAR_STREAM_ITEM_TYPE_LINK_STATE_EVENT = 2
    """A change in the state of a link, see STAR_LINK_STATE_EVENT in STAR_structures.py."""

    STAR_STREAM_ITEM_TYPE_DATA_CHUNK = 3
    """Contiguous chunk of data within a single packet, see STAR_DATA_CHUNK in STAR_structures.py."""

    STAR_STREAM_ITEM_TYPE_LINK_SPEED_EVENT = 4
    """A change in the speed of a link, see STAR_LINK_SPEED_EVENT in STAR_structures.py."""

    STAR_STREAM_ITEM_TYPE_ERROR_INJECT = 5
    """An error injection control word, see STAR_ERROR_IN_DATA_INJECT in STAR_structures.py."""

    STAR_STREAM_ITEM_TYPE_TIMESTAMP_EVENT = 6
    """Timestamp of the last data received on the link, see STAR_TIMESTAMP_EVENT in STAR_structures.py."""

    STAR_STREAM_ITEM_TYPE_BROADCAST_MESSAGE = 7
    """SpaceFibre broadcast message, see STAR_BROADCAST_MESSAGE in STAR_structures.py."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_ERROR_IN_DATA_TYPE(IntEnum):
    """The types of error that may be injected into the data in a packet."""

    STAR_ERROR_IN_DATA_PARITY = 0
    """Parity error."""

    STAR_ERROR_IN_DATA_DISCONNECT = 1
    """Disconnect error."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class STAR_BROADCAST_MESSAGE_STATUS_FLAG(IntEnum):
    """The status flag of the Broadcast message."""

    STAR_BROADCAST_MESSAGE_STATUS_FLAG_LATE = 0x01
    """The LATE flag of a broadcast message status field."""

    STAR_BROADCAST_MESSAGE_STATUS_FLAG_DELAYED = 0x02
    """The DELAYED flag of a broadcast message status field."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class RMAP_TARGET_STATUS(IntEnum):
    """The status of the RMAP target."""

    TARGET_STATUS_SUCCESS = 0
    TARGET_STATUS_GENERAL_ERROR = 1
    TARGET_STATUS_HEADER_EOP_ERROR = 2
    TARGET_STATUS_HEADER_EEP_ERROR = 3
    TARGET_STATUS_PID_ERROR = 4
    TARGET_STATUS_REPLY_ERROR = 5
    TARGET_STATUS_HEADER_CRC_ERROR = 6
    TARGET_STATUS_HEADER_EEP_AFTER_CRC = 7
    TARGET_STATUS_PACKET_TYPE_ERROR = 8
    TARGET_STATUS_COMMAND_TYPE_ERROR = 9
    TARGET_STATUS_RMW_DATALEN_ERROR = 10
    TARGET_STATUS_CARGO_TOO_LARGE = 11
    TARGET_STATUS_KEY_ERROR = 12
    TARGET_STATUS_LOGICAL_ADDR_ERROR = 13
    TARGET_STATUS_AUTHORISED_ERROR = 14
    TARGET_STATUS_VERIFY_BUFFER_OVERRUN = 15
    TARGET_STATUS_DATA_CRC_ERROR = 16
    TARGET_STATUS_BUS_ERROR = 17
    TARGET_STATUS_DATA_EOP_ERROR = 18
    TARGET_STATUS_DATA_EEP_ERROR = 19
    TARGET_STATUS_DATA_EEP_AFTER_CRC = 20

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class TARGET_AUTH_MODE(IntEnum):
    """Method of authorising incoming RMAP commands."""

    TARGET_AUTH_MODE_MANUAL = 0
    """When set to manual, each incoming command must be authorised or rejected by software."""

    TARGET_AUTH_MODE_AUTOMATIC = 1
    """When set to automatic, each incoming command is automatically authorised or rejected
       based on the authorised parameter values."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class IF_MODE(IntEnum):
    """Control whether or not the RMAP target is enabled for a port."""

    IF_MODE_RMAP_DISABLED = 0
    """When RMAP is disabled, the port acts as a normal SpaceWire interface."""

    IF_MODE_RMAP_ENABLED = 1
    """When RMAP is enabled, the port acts as an RMAP target."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class REJECTION_REASON(IntEnum):
    """Reason for rejecting a waiting RMAP command."""

    REJECTION_REASON_LOGICAL_ADDRESS = 0
    REJECTION_REASON_KEY = 1
    REJECTION_REASON_PROTOCOL_ID = 2
    REJECTION_REASON_OTHER = 3

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class NOTIF_TYPE(IntEnum):
    """Types of notifications."""

    NOTIF_TYPE_NONE = 0
    """No notifications."""

    NOTIF_TYPE_AUTH_REQUEST = 1
    """Authorisation request notification."""

    NOTIF_TYPE_CMD_COMPLETE = 4
    """Command complete notification."""

    NOTIF_TYPE_ALL = 5
    """All notifications."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)
        
class RMAP_TARGET_COMMANDS(IntEnum):
    """Types of notifications."""

    NONE = 0

    READ = (1 << 0)

    READ_INCREMENT = (1 << 1)

    READ_MODIFY_WRITE = (1 << 2)

    WRITE = (1 << 3)
    
    WRITE_INCREMENT = (1 << 4)
    
    WRITE_WITH_REPLY = (1 << 5)
    
    WRITE_INCREMENT_WITH_REPLY = (1 << 6)
    
    VERIFIED_WRITE = (1 << 7)
    
    VERIFIED_WRITE_INCREMENT = (1 << 8)
    
    VERIFIED_WRITE_WITH_REPLY = (1 << 9)
    
    VERIFIED_WRITE_INCREMENT_WITH_REPLY = (1 << 10)
    
    ALL_COMMANDS = 0x7FF

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)