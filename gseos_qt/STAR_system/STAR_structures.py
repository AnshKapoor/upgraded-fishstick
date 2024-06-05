"""Data structures used by STAR-System to efficiently pass data between the Python API and the C API.

Brief:\n
    Data structures used by STAR-System to efficiently pass data between
    the Python API and the C API. These are used internally by the API and are not
    intended to be used by the user.\n
    Note: The type of the attributes is always a pair in the format X / Z,
    where X is the C type and Z is the Python type equivalent.

Copyright:\n
    2021 STAR-Dundee Ltd.
"""

import os
from ctypes import *


class STAR_TIMESTAMP_EVENT(Structure):
    """A structure used to describe a timestamp on receipt of data on the link.

    Corresponds to `STAR_system.timestamp_event.TimestampEvent` class.

    Attributes:\n
        systemClockFrequency: (unsigned int / int) The system clock frequency of
            the device. Valid values are as follows:
            0: Timestamp for data.
            1: Timestamp for link state event.
            2: Timestamp for link speed event.
            3: Timestamp for time-code.
            4: Timestamp for error in data.
        type: (int / int) The type of data that the timestamp represents.
        direction: (int / int) Whether timestamp relates to transmitted or received
            data. Valid values are 0 for transmit and 1 for receive.
        startSyncPulseCount: (unsigned int / int) The number of synchronisation
            pulses when the start of the packet was transmitted or received.
        startClockCycleCount: (unsigned int / int) The number of clock cycles
            counted when the start of the packet was transmitted or received.
        startTotalCycleCount: (unsigned int / int) The number of clock cycles
            counted when the last synchronisation pulse before the start of the
            packet was received.
        endSyncPulseCount: (unsigned int / int) The number of synchronisation
            pulses when the end of the packet was transmitted or received.
        endClockCycleCount: (unsigned int / int) The number of clock cycles
            counted when the end of the packet was transmitted or received.
        endTotalCycleCount: (unsigned int / int) The number of clock cycles
            counted when the last synchronisation pulse before the end of the packet
            was received.
    """

    _fields_ = [
        ("systemClockFrequency", c_uint32),
        ("typeOfData", c_int32),
        ("direction", c_int32),
        ("startSyncPulseCount", c_uint32),
        ("startClockCycleCount", c_uint32),
        ("startTotalCycleCount", c_uint32),
        ("endSyncPulseCount", c_uint32),
        ("endClockCycleCount", c_uint32),
        ("endTotalCycleCount", c_uint32)]


class STAR_ERROR_IN_DATA_INJECT(Structure):
    """A structure used to describe an error in data control. Not all devices support this item type.\n

    Corresponds to `STAR_system.error_in_data.ErrorInData` class.

    Attributes:\n
        errorType: (int / int) Type of error to inject on a following data
            character. 0 - parity error, 1 - disconnect error
    """

    _fields_ = [
        ("errorType", c_int32)]


class STAR_LINK_STATE_EVENT(Structure):
    """A struct to hold link state event information.\n

    Corresponds to the `STAR_system.link_state_event.LinkStateEvent` class.

    Attributes:\n
        count: (unsigned char / int) The number of times that the event(s) has occurred.
        receiveCreditError: (unsigned int / int) Receive credit error.
        transmitCreditError: (unsigned int / int) Transmit credit error.
        escapeError: (unsigned int / int) Escape error.
        parityError: (unsigned int / int) Parity error.
        disconnectError: (unsigned int / int) Disconnect error.
        linkRunning: (unsigned int / int) link running
        port: (unsigned char / int) the port on which the event occurred.
    """

    # Bit-field implementations seem to be buggy on Linux OS so adding _pack_1 = 1 field solves this
    # Adding this on Windows OS breaks it though !!!
    systemType = os.name
    if systemType == "posix":
        _pack_ = 1

    _fields_ = [
        ("count", c_uint8),
        ("receiveCreditError", c_uint32, 1),
        ("transmitCreditError", c_uint32, 1),
        ("escapeError", c_uint32, 1),
        ("parityError", c_uint32, 1),
        ("disconnectError", c_uint32, 1),
        ("linkRunning", c_uint32, 1),
        ("port", c_uint8)]


class STAR_VERSION_INFO(Structure):
    """A struct to store version information. Strings are stored as bytes.\n

    Corresponds to the `STAR_system.STAR_structure_classes.VersionInformation` class.

    Attributes:\n
        name: (char* array / array of 1 character bytes) The name of the module.
        author: (char * array / array of 1 character bytes) The author of the module.
        major: (unsigned short / int) The major version number of this module.
        minor: (unsigned short / int) The minor version number of this module.
        edit: (unsigned short / int) The edit number of this module.
        patch: (unsigned short / int) The patch number of this module. Edit will be 0 if patch is non-zero.
    """

    _fields_ = [
        ("name", c_char * 256),
        ("author", c_char * 256),
        ("major", c_uint16),
        ("minor", c_uint16),
        ("edit", c_uint16),
        ("patch", c_uint16)]


class STAR_TIMECODE(Structure):
    """A struct used to describe a SpaceWire time-code.\n

    Corresponds to `STAR_system.time_code.TimeCode` class.

    Attributes:\n
        numSinceLastTx: (unsigned short / int) Count of the number of time-codes
            since the last time-code was transmitted.
        value: (unsigned char / int) The value of the time-code.
    """

    _fields_ = [
        ("numSinceLastTx", c_uint16),
        ("value", c_uint8)]


class STAR_STREAM_ITEM(Structure):
    """A wrapper for stream item objects. Corresponds to `STAR_system.stream_item.StreamItem` class.

    Attributes:\n
        itemType: (int / int) The type of stream item. See `STAR_system.STAR_enums.STAR_STREAM_ITEM_TYPE` for valid (integer) values.
        item: (void* / int)  A pointer to a stream item. This may be any of the following\n
        `STAR_system.STAR_structures.STAR_SPACEWIRE_PACKET`, `STAR_system.STAR_structures.STAR_DATA_CHUNK`,
        `STAR_system.STAR_structures.STAR_TIMECODE`, `STAR_system.STAR_structures.STAR_LINK_SPEED_EVENT`,
        `STAR_system.STAR_structures.STAR_LINK_STATE_EVENT`, `STAR_system.STAR_structures.STAR_TIMESTAMP_EVENT`,
        `STAR_system.STAR_structures.STAR_BROADCAST_MESSAGE`.
        pReceivedOperation: (void* / int)  Internal. The receive operation that the stream
            was received by, or NULL if it wasn't received by a receive operation.
        pNext: (void* / int) Internal. The next stream item in the list of stream
            items, if this is a receive operation stream item.
    """

    _fields_ = [
        ("itemType", c_int32),
        ("item", c_void_p),
        ("pReceivedOperation", c_void_p),
        ("pNext", c_void_p)]


class STAR_SPACEWIRE_ADDRESS(Structure):
    """A struct to store a SpaceWire address.

    Attributes:\n
        pPath: (void* / int) An array of SpaceWire path address elements.
        pathLength: (unsigned short / int) The length of the address.
    """

    _fields_ = [
        ("pPath", c_void_p),
        ("pathLength", c_uint16)]


class STAR_DATA_CHUNK(Structure):
    """A struct used to describe a chunk of contiguous SpaceWire data, within a single packet.\n

    Corresponds to `STAR_system.data_chunk.DataChunk` class.

    Attributes:\n
        pNext: (void* / int) A pointer to the next data chunk in the packet.
        pPrev: (void* / int) A pointer to the previous data chunk in the packet.
        data: (void* / int) A pointer to the data buffer itself.
        dataLength: (unsigned int / int) The length of data in the buffer.
        isStart: (int / int) Whether the chunk of data represents the start of a
            new packet or not.
        eop: (int / int) The type of end packet marker that this data chunk has,
            if any. See STAR_EOP_TYPE enum (integer) values for valid values.
    """

    _fields_ = [
        ("pNext", c_void_p),
        ("pPrev", c_void_p),
        ("data", c_void_p),
        ("dataLength", c_uint32),
        ("isStart", c_int32),
        ("eop", c_int32)]


class STAR_SPACEWIRE_PACKET(Structure):
    """A struct used to describe a SpaceWire packet.\n

    Corresponds to `STAR_system.packet.Packet` class.

    Attributes:\n
        address: (`STAR_system.STAR_structures.STAR_SPACEWIRE_ADDRESS` / int) The packet's address (optional).
            This member is provided for convenience only. There is no difference
            between specifying a packet with an address of [0xFE, 0xAB] and data of
            [0x01, 0x02, 0x03, 0x04] and specifying a packet with no explicit
            address and data of [0xFE, 0xAB, 0x01, 0x02, 0x03, 0x04].
        dataChunks: (void* / int) A pointer to the data that makes up the packet.
    """

    _fields_ = [
        ("address", POINTER(STAR_SPACEWIRE_ADDRESS)),
        ("dataChunks", POINTER(STAR_DATA_CHUNK))]


class STAR_LINK_SPEED_EVENT(Structure):
    """A struct used to describe a link speed change event.\n

    Corresponds to `STAR_system.link_speed_event.LinkSpeedEvent`.\n

    Not all devices support this item type, and receiving these types may need
    to be enabled separately.

    Attributes:\n
        linkSpeed: (unsigned int / int) The new link speed which has been adopted,
            represented in bit/s. Note that this value is approximate.
        port: (unsigned char / int) The port on which the event occurred.
    """

    _fields_ = [
        ("linkSpeed", c_uint32),
        ("port", c_uint8)]


class STAR_CFG_BRICK_MK2_ERRORS(Structure):
    """A struct used to indicate which errors should be generated when calling
     `STAR_system.link_port.LinkPort.injectErrors`.\n

     If the element is set to a non-zero value, an error of that type will be injected.

     Attributes:\n
        parityError: (char / 1 character bytes object) Whether a parity error should be injected.
        escapeError: (char / 1 character bytes object) Whether an escape error should be injected.
        insertFCT: (char / 1 character bytes object) Whether an extra FCT should be inserted to cause an error.
        suppressFCT: (char / 1 character bytes object) Whether an FCT should be suppressed to cause an error.
        incrementCredit: (char / 1 character bytes object) Whether credit should be incremented to cause an error.
        decrementCredit: (char / 1 character bytes object) Whether credit should be decremented to cause an error.
        Disconnect: (char / 1 character bytes object) Whether a disconnect error should occur.
    """

    _fields_ = [
        ("parityError", c_char),
        ("escapeError", c_char),
        ("insertFCT", c_char),
        ("suppressFCT", c_char),
        ("incrementCredit", c_char),
        ("decrementCredit", c_char),
        ("Disconnect", c_char)]


class STAR_CFG_CONFIG_PORT_ERRORS(Structure):
    """Errors that may be present on a device's configuration port.
    If a member of this struct is set, then the error it represents is present.\n

    Corresponds to `STAR_system.STAR_structure_classes.ConfigPortErrors` class.

    Attributes:\n
        errorCount: (char / 1 character bytes object) Count of errors present on the configuration port.
        portTimeoutError: (char / 1 character bytes object) The port timeout error bit is set when a
            timeout event is detected by the configuration port routing logic.
        invalidHeaderCRC: (char / 1 character bytes object) The Invalid header CRC bit is set when the
            header CRC is invalid.
        invalidDataCRC: (char / 1 character bytes object) The invalid data CRC is set when the data field
            of the packet is corrupted and the CRC does not match the internally generated CRC.
        invalidDestinationKey: (char / 1 character bytes object) The invalid destination key bit is set
            when the destination key in the command packet is invalid.
        commandNotImplemented: (char / 1 character bytes object) The command not implemented bit is set
            when the command code is a valid RMAP code but the command is not supported by the SpaceWire Router.
        invalidDataLength: (char / 1 character bytes object) The invalid data length bit is set when a
            data length error is detected.
        invalidRMWDataLength: (char / 1 character bytes object) The read modify write command data length
            is invalid. The expected length is 8.
        invalidDestinationLogicalAddress: (char / 1 character bytes object) The invalid destination
            logical address bit is set when the destination logical address in the
            command packet is not the default value of 254.
        earlyEOP: (char / 1 character bytes object) The early EOP bit is set when the command packet is
            terminated before the end of packet with an EOP.
        lateEOP: (char / 1 character bytes object) The late EOP bit is set when the command packet is not
            terminated correctly and trailing bytes are detected before the end of packet.
        earlyEEP: (char / 1 character bytes object) The early EEP bit is set when the command packet is
            terminated before the end of packet with an EEP.
        lateEEP: (char / 1 character bytes object) The late EEP bit is set when the command packet is not
            terminated correctly and trailing bytes are detected before the end of packet.
        verifyBufferOverrun: (char / 1 character bytes object) The verify buffer overrun error bit is set
            when a verified write command is performed and the data length is not 4.
        invalidRegisterAddress: (char / 1 character bytes object) The invalid register address bit is set
            when an unknown register address is given in the command packet or a 
            write is attempted to a read only register.
        unsupportedProtocol: (char / 1 character bytes object) The unsupported protocol error bit is set
            when a command packet is received with a protocol identifier which is
            not the RMAP protocol identifier (0x01).
        sourceLogicalAddressError: (char / 1 character bytes object) The source logical address error bit
            is set when an invalid source logical address is received.
        sourcePathAddressError: (char / 1 character bytes object) This bit is set when an invalid source
            address path is received. This error is not used for the SpW10X.
        cargoTooLarge: (char / 1 character bytes object) The RMAP command packet is too large.
        unusedRMAPCommandOrPacketType: (char / 1 character bytes object) The command code is an unused
            command code or the packet type is invalid.
    """

    _fields_ = [
        ("errorCount", c_char),
        ("portTimeoutError", c_char),
        ("invalidHeaderCRC", c_char),
        ("invalidDataCRC", c_char),
        ("invalidDestinationKey", c_char),
        ("commandNotImplemented", c_char),
        ("invalidDataLength", c_char),
        ("invalidRMWDataLength", c_char),
        ("invalidDestinationLogicalAddress", c_char),
        ("earlyEOP", c_char),
        ("lateEOP", c_char),
        ("earlyEEP", c_char),
        ("lateEEP", c_char),
        ("verifyBufferOverrun", c_char),
        ("invalidRegisterAddress", c_char),
        ("unsupportedProtocol", c_char),
        ("sourceLogicalAddressError", c_char),
        ("sourcePathAddressError", c_char),
        ("cargoTooLarge", c_char),
        ("unusedRMAPCommandOrPacketType", c_char)]


class STAR_CFG_EXTERNAL_PORT_ERRORS(Structure):
    """Errors that may be present on an external port.\n

    Corresponds to `STAR_system.STAR_structure_classes.ExternalPortErrors` class.

    Attributes:\n
        errorCount: (char / 1 character bytes object) Count of errors present on the external port.
        packetAddress: (char / 1 character bytes object) A packet was received with
            an invalid address, either due to an unknown port, or an invalid
            logical address. This is also generated when an empty packet is passed to the external port.
        portTimeout: (char / 1 character bytes object) The port has become blocked for a period of time.
            A packet could not be routed to a destination port before the port timeout occurred.
    """

    _fields_ = [
        ("errorCount", c_char),
        ("packetAddress", c_char),
        ("portTimeout", c_char)]


class STAR_CFG_EXTERNAL_PORT_STATUS(Structure):
    """Status of an external port.\n

    Corresponds to `STAR_system.STAR_structure_classes.ExternalPortStatus` class.

    Attributes:\n
        inputBufferEmpty: (char / 1 character bytes object) The external port input
            buffer is empty. The input buffer writes data to the SpaceWire router.
        inputBufferFull: (char / 1 character bytes object) The external port input buffer is full.
        outputBufferEmpty: (char / 1 character bytes object) The external output
            buffer is empty. The output buffer writes data to the external device
            connected to the external port.
        outputBufferFull: (char / 1 character bytes object) The external output port buffer is full.
    """

    _fields_ = [
        ("inputBufferEmpty", c_char),
        ("inputBufferFull", c_char),
        ("outputBufferEmpty", c_char),
        ("outputBufferFull", c_char)]


class STAR_CFG_SPW_LINK_ERRORS(Structure):
    """Errors that may be present on a SpaceWire link.\n

    Corresponds to `STAR_system.STAR_structure_classes.LinkPortErrors` class.

    Attributes:\n
        errorCount: (char / 1 character bytes object) Count of errors present on
            the link port.
        packetAddress: (char / 1 character bytes object) A packet was received with
            an invalid address, either due to an unknown port, or an invalid logical address.
        portTimeout: (char / 1 character bytes object) The port has become blocked
            for a period of time. A packet could not be routed to a destination
            port before the port timeout occurred.
        disconnect: (char / 1 character bytes object) A disconnect error occurred
            on the link. No activity occurred on the link for the disconnect timeout period.
        parity: (char / 1 character bytes object) A parity was detected on a
            character parity bit.
        escape: (char / 1 character bytes object) An invalid escape code was
            received on the link (ESC-ESC, ESC-EOP, or ESC-EEP).
        credit: (char / 1 character bytes object) A credit error occurred on the link.
        characterSequence: (char / 1 character bytes object) A character sequence
            error occurred on the link. This indicates a time-code or data
            character was received before the first FCT.
    """

    _fields_ = [
        ("errorCount", c_char),
        ("packetAddress", c_char),
        ("portTimeout", c_char),
        ("disconnect", c_char),
        ("parity", c_char),
        ("escape", c_char),
        ("credit", c_char),
        ("characterSequence", c_char)]


class STAR_CFG_SPW_LINK_STATUS(Structure):
    """Status of a SpaceWire link.\n

    Corresponds to `STAR_system.STAR_structure_classes.LinkStatus` class.

    Attributes:\n
        triState: (char/int / bool) When set, the SpaceWire link LVDS drivers are in tri-state mode.
        disable: (char/int / bool) When set the SpaceWire link will be disabled as
            defined in the SpaceWire standard. The SpaceWire port will not start
            and will not respond to any attempt to make a connection by the other end of the link.
        start: (char/int / bool) When set the SpaceWire link will initiate start-up as
            defined in the SpaceWire standard. The SpaceWire port will try to make
            a connection with the other end of the link.
        autoStart: (char/int / bool) When set the SpaceWire link will auto-start as
            defined in the SpaceWire standard. The SpaceWire port will wait until
            the other end of the link tries to make a connection (sending NULLs)
            and will then automatically start.
        running: (char/int / bool) Set when the SpaceWire interface state machine is
            in the Run state.
        linkState: (int / int) State of the interface state machine. See
            `STAR_system.STAR_enums.STAR_CFG_SPW_LINK_STATE` enum for valid (integer) values.
    """

    _fields_ = [
        ("triState", c_bool),
        ("disable", c_bool),
        ("start", c_bool),
        ("autoStart", c_bool),
        ("running", c_bool),
        ("linkState", c_int32)]


class STAR_CFG_DEVICE_IDENTIFIER_INFO(Structure):
    """Information obtained from a device's identifier register, identifying
    the router's version and type.

    Corresponds to `STAR_system.STAR_structure_classes.DeviceIdentifierInformation` class.

    Attributes:\n
        manufacturerID: (unsigned short / int) Manufacturer ID number.
        chipType: (unsigned char / int) Identity code for the SpaceWire chip from the particular manufacturer.
        versionNum: (unsigned char / int) Device version number.
    """

    _fields_ = [
        ("manufacturerID", c_uint16),
        ("chipType", c_uint8),
        ("versionNum", c_uint8)]


class STAR_CFG_NETWORK_DISCOVERY_INFO(Structure):
    """Information obtained from a device's network discovery register, that can
    be used to determine the network layout.\n

    Corresponds to `STAR_system.STAR_structure_classes.NetworkDiscoveryInformation` class.

    Attributes:\n
        deviceType: (int / int) Type of device. See integer values in `STAR_system.STAR_enums.STAR_CFG_DEVICE_TYPE`.
        returnPort: (unsigned char / int) Indicates the input port number which was
            used to access the network discovery register.
        runningPortsMask: (unsigned int / int) Bitmask of ports which are in the
            run state. Bit 1 corresponds to port 1.
        runningPortsCount: (unsigned char / int) Count of running ports.
        portCount: (unsigned char / int) Count of the number of ports the device has.
    """

    _fields_ = [
        ("deviceType", c_int32),
        ("returnPort", c_uint8),
        ("runningPortsMask", c_uint32),
        ("runningPortsCount", c_uint8),
        ("portCount", c_uint8)]


class STAR_CFG_FPGA_INFO(Structure):
    """Hardware version, and synthesis date of the FPGA code.\n

    Corresponds to `STAR_system.STAR_structure_classes.HardwareInfo` class.

    Attributes:\n
        major: (unsigned char / int) Major version number.
        minor: (unsigned char / int) Minor version number.
        edit: (unsigned int / int) Version number edit.
        patch: (unsigned char / int) Version number patch.
        year: (unsigned int / int) Year value of time and date.
        month: (unsigned char / int) Month value of time and date.
        day: (unsigned char / int) Day value of time and date.
        hour: (unsigned char / int) Hour value of time and date.
        minute: (unsigned char / int) Minute value of time and date.
    """

    _fields_ = [
        ("major", c_uint8),
        ("minor", c_uint8),
        ("edit", c_uint16),
        ("patch", c_uint8),
        ("year", c_uint16),
        ("month", c_uint8),
        ("day", c_uint8),
        ("hour", c_uint8),
        ("minute", c_uint8)]

class STAR_CFG_ROUTER_GLOBAL_STATE(Structure):
    """Global router settings.\n

    Corresponds to `STAR_system.STAR_structure_classes.RouterGlobalState` class.

    Attributes:\n
        timeoutMode: (int / int) Timeout mode. See `STAR_system.STAR_enums.STAR_CFG_TIMEOUT_MODE` enum for valid (integer) values.
        timeoutPeriod: (int / int) Timeout period. See `STAR_system.STAR_enums.STAR_CFG_PORT_TIMEOUT` enum for valid (integer) values.
        disableOnSilence: (char / 1-character bytes object) If true, links will be disabled after the
            timeout period when data transfer completes.
        startOnRequest: (char / 1-character bytes object) If true, links will be automatically
            started when they have data to transfer. If the link cannot be started
            packets are discarded after the timeout period.
        enableSelfAddressing: (char / 1-character bytes object) If true, a packet can be routed out of
            the port on which it arrived on. This is for debugging purposes. If this
            is false and a packet is to be routed through the same port, an address
            error is reported and the packet is discarded. If false, and a group
            adaptive routing packet is received (a packet which can be routed
            through two or more ports, dependent on the group adaptive routing
            table contents) which can be routed through the port it arrived on then
            the packet is routed through one of the other ports and not the port
            on which the packet arrived on. An address error is not reported.
    """

    _fields_ = [
        ("timeoutMode", c_int32),
        ("timeoutPeriod", c_int32),
        ("disableOnSilence", c_char),
        ("startOnRequest", c_char),
        ("enableSelfAddressing", c_char)]


class STAR_CFG_GAR_ENTRY(Structure):
    """A routing table entry.\n

    Corresponds to `STAR_system.STAR_structure_classes.RoutingTableEntry` class.

    Attributes:\n
        portMask: (unsigned int / int) Bitmask of output ports the logical address
            will arbitrate for. Valid bits set are 1 through 28. Bit 1 corresponds
            to port 1. It is not possible to access the configuration port (0)
            through logical address.
        priority: (char/int / bool) Packets with the logical address for this entry
            with the priority bit set will be granted access to a particular
            output port in preference to packets whose logical addresses in the
            routing table have their priority bit set to zero.
        deleteHeader: (char/int / bool) When set the leading header byte of the
            input packet will be removed before it is transferred to the output
            port.
        invalidAddress: (char/int / bool) When set this indicates that the
            corresponding logical address is invalid. In this case, any packets
            arriving at the router with an invalid address are silt and an
            address error is reported in the port status register.
    """

    _fields_ = [
        ("portMask", c_uint32),
        ("priority", c_bool),
        ("deleteHeader", c_bool),
        ("invalidAddress", c_bool)]


class STAR_TRIGGER_MATRIX(Structure):
    """Triggering matrix structure.

        Attributes:\n
            extTriggers: (unsigned int) The number of external triggers present in a device that can be used
                                        for triggering functionality purposes.
            counters: (unsigned int) The number of counters/timers present in a device that can be used
                                     for triggering functionality purposes.
            ports: (unsigned int) The number of ports present in a device that can be used for triggering
                                  functionality purposes.
            timeCodes: (unsigned int) The number of time-code engines present in a device that can be
                                      used for triggering functionality purposes.
            triggers: (unsigned int) The number of internal triggers present in a device that can be
                                      used for triggering functionality purposes.
        """

    _fields_ = [
        ("extTriggers", c_uint32),
        ("counters", c_uint32),
        ("ports", c_uint32),
        ("timeCodes", c_uint32),
        ("triggers", c_uint32)]


class STAR_IP_ADDRESS_TYPE(Structure):
    """STAR IP address type structure.

        Attributes:\n
            IPVersion: (STAR_IP_VERSION_TYPE) The Internet Protocol version.
            IPAddress: (c_void_p) Pointer to the buffer containing the IP address. The length is determined by
                                  the IP version (IPv4 = 4 bytes, IPv6 = 16 bytes).
        """
    _fields_ = [
        ("IPVersion", c_uint32),
        ("IPAddress", c_void_p)]


class STAR_BROADCAST_MESSAGE(Structure):
    """STAR Broadcast message structure.

        Attributes:\n
            channel: (unsigned char) The broadcast message's channel (BC field).
            type: (unsigned char) The broadcast message's type (B_TYPE field).
            status: (unsigned char) The broadcast message's status (STATUS field).
            dataWord1: (unsigned int) The broadcast message's first data word.
            dataWord2: (unsigned int) The broadcast message's second data word.
        """
    _fields_ = [
        ("channel", c_uint8),
        ("type", c_uint8),
        ("status", c_uint8),
        ("dataWord1", c_uint32),
        ("dataWord2", c_uint32)]

class RMAP_COMMAND_PARAMETERS(Structure):
    """Parameters of an RMAP command.

        Attributes:\n
            targetLogicalAddress (unsignd char): Target logical address.
            command (unsignd char): Command.
            key (unsignd char): Key.
            protocolId (unsignd char): Protocol ID.
            extendedAddress (unsignd char): Extended address.
            dataLength (int): Data length.
            address (int): Address.
            initiatorLogicalAddress (int): Initiator logical address.
            transactionId (int): Transaction ID.
        """
    _fields_ = [
        ("targetLogicalAddress", c_uint8),
        ("command", c_uint8),
        ("key", c_uint8),
        ("protocolId", c_uint8),
        ("extendedAddress", c_uint8),
        ("dataLength", c_uint32),
        ("address", c_uint32),
        ("initiatorLogicalAddress", c_uint8),
        ("transactionId", c_uint16)]

