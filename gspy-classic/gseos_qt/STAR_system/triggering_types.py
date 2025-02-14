"""Contains the enums used throughout the Python triggering API.

Brief:\n
    Enums used in the STAR-System Triggering API function calls.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

from enum import IntEnum


class EXT_TRIGGER_EVENT(IntEnum):
    """External trigger events."""

    EXT_TRIGGER_EVENT_NONE = 0
    """No events."""

    EXT_TRIGGER_EVENT_IN = 1
    """Event occurs when the external trigger has received input."""

    EXT_TRIGGER_EVENT_ALL = 1
    """All events."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class EXT_TRIGGER_ACTION(IntEnum):
    """External trigger actions."""

    EXT_TRIGGER_ACTION_NONE = 0
    """No actions."""

    EXT_TRIGGER_ACTION_OUT = 1
    """Output the external trigger."""

    EXT_TRIGGER_ACTION_ALL = 1
    """All actions."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class COUNTER_EVENT(IntEnum):
    """Counter events."""

    COUNTER_EVENT_NONE = 0
    """No events."""

    COUNTER_EVENT_COUNT = 1
    """Event occurs when the counter decrements."""

    COUNTER_EVENT_ZERO_SINGLE = 2
    """Event occurs when the counter reaches zero (once)."""

    COUNTER_EVENT_ZERO = 4
    """Event is active while the counter is equal to zero."""

    COUNTER_EVENT_RELOAD = 8
    """.Event occurs when the counter reloads."""

    COUNTER_EVENT_ALL = 15
    """All events."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class COUNTER_ACTION(IntEnum):
    """Counter actions."""

    COUNTER_ACTION_NONE = 0
    """No actions."""

    COUNTER_ACTION_COUNT = 1
    """Decrement the counter."""

    COUNTER_ACTION_RELOAD = 2
    """Reload the counter."""

    COUNTER_ACTION_START = 4
    """Start the counter."""

    COUNTER_ACTION_STOP = 8
    """Stop the counter."""

    COUNTER_ACTION_ALL = 15
    """All actions."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class PORT_EVENT(IntEnum):
    """Port events."""

    PORT_EVENT_NONE = 0
    """No events."""

    PORT_EVENT_RX_SOP = 1
    """Event occurs when the port receives an SOP"""

    PORT_EVENT_RX_EOP = 2
    """Event occurs when the port receives an EOP."""

    PORT_EVENT_RX_EEP = 4
    """Event occurs when the port receives an EEP."""

    PORT_EVENT_TX_SOP = 8
    """Event occurs when the port transmits an SOP."""

    PORT_EVENT_TX_EOP = 16
    """Event occurs when the port transmits an EOP."""

    PORT_EVENT_TX_PKT_PENDING = 32
    """Event is active when the port has a packet queued for transmission."""

    PORT_EVENT_RUNNING = 64
    """Event is active when the link attached to the port is running."""

    PORT_EVENT_PARITY_ERROR = 128
    """Event occurs when the port detects a parity error."""

    PORT_EVENT_ESCAPE_ERROR = 256
    """Event occurs when the port detects an escape error."""

    PORT_EVENT_CREDIT_ERROR = 512
    """Event occurs when the port detects a credit error."""

    PORT_EVENT_DISCONNECT = 1024
    """Event occurs when the port disconnects."""

    PORT_EVENT_RX_TIME_CODE = 2048
    """Event occurs when the port receives a time-code."""

    PORT_EVENT_TX_TIME_CODE = 4096
    """Event occurs when the port transmits a time-code."""

    PORT_EVENT_ALL_PCIE = 4095
    """All events PCIE."""

    PORT_EVENT_ALL = 8191
    """All events."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class PORT_ACTION(IntEnum):
    """Port actions."""

    PORT_ACTION_NONE = 0
    """No actions."""

    PORT_ACTION_TRANSMIT_PKT = 1
    """Transmit a pending packet."""

    PORT_ACTION_DISCONNECT = 2
    """Disconnect the port."""

    PORT_ACTION_PARITY_ERROR = 4
    """Inject a parity error."""

    PORT_ACTION_ESCAPE_ERROR = 8
    """Inject an escape error."""

    PORT_ACTION_INSERT_FCT = 16
    """Insert an FCT."""

    PORT_ACTION_SUPPRESS_FCT = 32
    """Suppress the next FCT to be transmitted."""

    PORT_ACTION_INCR_CREDIT = 64
    """Increment credit."""

    PORT_ACTION_DECR_CREDIT = 128
    """Decrement credit."""

    PORT_ACTION_STOP_RECEPTION = 256
    """Stop reception."""

    PORT_ACTION_DISABLE_LVDS = 512
    """Disable LVDS drivers."""

    PORT_ACTION_ALL_PCIE = 777
    """All actions PCIE."""

    PORT_ACTION_ALL = 1023
    """All actions."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class TIME_CODE_EVENT(IntEnum):
    """Time-code events."""

    TIME_CODE_EVENT_NONE = 0
    """No events."""

    TIME_CODE_EVENT_TICK = 1
    """Event occurs when the next valid time-code is received."""

    TIME_CODE_EVENT_ALL = 1
    """All events."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class TIME_CODE_ACTION(IntEnum):
    """Time-code actions."""

    TIME_CODE_ACTION_NONE = 0
    """No actions."""

    TIME_CODE_ACTION_TX = 1
    """Transmit a time-code."""

    TIME_CODE_ACTION_ALL = 1
    """All actions."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class TRIGGER_EVENT(IntEnum):
    """Internal trigger events."""

    TRIGGER_EVENT_NONE = 0
    """No events."""

    TRIGGER_EVENT_IN = 1
    """Event occurs when the internal trigger has received input."""

    TRIGGER_EVENT_ALL = 1
    """All events."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class TRIGGER_INPUT_MODE(IntEnum):
    """Internal trigger input modes."""

    TRIGGER_INPUT_MODE_OR = 0
    """Trigger is a sum of its inputs."""

    TRIGGER_INPUT_MODE_AND = 1
    """Trigger is a product of its inputs."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class TRIGGER_TYPE(IntEnum):
    """Trigger types."""

    TRIGGER_TYPE_EXT_TRIGGER = 0
    """External trigger type."""

    TRIGGER_TYPE_COUNTER = 1
    """Counter trigger type."""

    TRIGGER_TYPE_PORT = 2
    """Port trigger type."""

    TRIGGER_TYPE_TIME_CODE = 3
    """Time-code trigger type."""

    TRIGGER_TYPE_TRIGGER = 4
    """Internal trigger type."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)

class TRIGGER_DEVICE(IntEnum):
    """Trigger devices."""

    TRIGGER_DEVICE_INVALID = 0
    """Invalid trigger device."""

    TRIGGER_DEVICE_BRICK_MK3 = 1
    """Brick Mk3 trigger device."""

    TRIGGER_DEVICE_PXI_IF = 2
    """PXI Interface trigger device."""

    TRIGGER_DEVICE_PXI_ROUTER = 3
    """PXI Router trigger device."""

    TRIGGER_DEVICE_PCIE_IF = 4
    """PCIe Interface trigger device."""

    TRIGGER_DEVICE_PCIE_MK2 = 5
    """PCIe MK2 Interface trigger device."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)
