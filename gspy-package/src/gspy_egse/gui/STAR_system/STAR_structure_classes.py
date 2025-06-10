"""Container classes for use with STAR-system.

Brief:\n
    Container classes for use with STAR-system.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

from gspy_egse.gui.STAR_system.STAR_enums import STAR_CFG_DEVICE_TYPE, STAR_CFG_TIMEOUT_MODE, STAR_CFG_PORT_TIMEOUT,\
                                   STAR_CFG_SPW_LINK_STATE


class VersionInformation(object):
    """A container to store version information for a module.
     
    Attributes:\n
        name (str): The name of the module.
        author (str): The author of the module.
        major (int): The major version number of the module.
        minor (int): The minor version number of the module.
        edit (int): The edit number of the module.
        patch (int): The patch number of this module. Edit will be 0 if patch is non-zero.
    """

    def __init__(self, name, author, major, minor, edit, patch):
        """Initialises `STAR_system.STAR_structure_classes.VersionInformation` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.VersionInformation` class attributes.

        Raises:\n
            TypeError:\n
                name or author is not a str.\n
                Any other argument is not an int.\n
            ValueError:\n
                Any int argument is negative.\n
        """

        if type(name) != str:
            raise TypeError("name must be str.")
        if type(author) != str:
            raise TypeError("author must be str.")
        if type(major) != int:
            raise TypeError("major must be int.")
        if type(minor) != int:
            raise TypeError("minor must be int.")
        if type(edit) != int:
            raise TypeError("edit must be int.")
        if type(patch) != int:
            raise TypeError("patch must be int.")

        if major < 0:
            raise ValueError("Major version number cannot be negative.")
        if minor < 0:
            raise ValueError("Minor version number cannot be negative.")
        if edit < 0:
            raise ValueError("Edit number cannot be negative.")
        if patch < 0:
            raise ValueError("Patch number cannot be negative.")

        self.name = name
        self.author = author
        self.major = major
        self.minor = minor
        self.edit = edit
        self.patch = patch

class DeviceIdentifierInformation(object):
    """A Container of information obtained from a device's identifier register,
    identifying the router's version and type.

    Holds the same data as the `STAR_system.STAR_structures.STAR_CFG_DEVICE_IDENTIFIER_INFO` structure, except that
    this class also includes deviceType as a string and manufacturer name as a string.

    Attributes:\n
        deviceType (str): The device type.
        manufacturerID (int): The manufacturer ID number (STAR-Dundee: 1).
        manufacturerName (str): The manufacturer's name.
        chipType (int): The identity code for the SpaceWire chip from the particular manufacturer.
        versionNumber (int): The device version number.
    """

    def __init__(self, deviceType, manufacturerID, manufacturerName, chipType, versionNumber):
        """Initialises a `STAR_system.STAR_structure_classes.DeviceIdentifierInformation` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.DeviceIdentifierInformation` class attributes.

        Raises:\n
            TypeError:\n
                deviceType of manufacturerName is not a str.\n
                manufacturerID, chipType, or versionNumber is not an int.\n
            ValueError:\n
                manufacturerID is negative.\n
                versionNumber is negative.\n
        """

        if type(deviceType) != str:
            raise TypeError("deviceType must be str.")
        if type(manufacturerID) != int:
            raise TypeError("manufacturerID must be int.")
        if type(manufacturerName) != str:
            raise TypeError("manufacturerName must be str.")
        if type(chipType) != int:
            raise TypeError("chipType must be int.")
        if type(versionNumber) != int:
            raise TypeError("versionNumber must be int.")
        if manufacturerID < 0:
            raise ValueError("manufacturerID cannot be negative.")
        if versionNumber < 0:
            raise ValueError("versionNumber cannot be negative.")

        self.deviceType = deviceType
        self.manufacturerID = manufacturerID
        self.manufacturerName = manufacturerName
        self.chipType = chipType
        self.versionNumber = versionNumber


class NetworkDiscoveryInformation(object):
    """ A container for information obtained from a device's network discovery register.

    This information can be used to determine the network layout.

    This class holds the same information as the `STAR_system.STAR_structures.STAR_CFG_NETWORK_DISCOVERY_INFO` structure,
    except deviceType in this class is a `STAR_system.STAR_enums.STAR_CFG_DEVICE_TYPE` whereas in `STAR_system.STAR_structures.STAR_CFG_NETWORK_DISCOVERY_INFO`
    it is an int which maps into the `STAR_system.STAR_enums.STAR_CFG_DEVICE_TYPE` enum.

    Attributes:\n
        deviceType (STAR_system.STAR_enums.STAR_CFG_DEVICE_TYPE): The type of device.
        returnPort (int): Indicates the input port which was used to access the network discovery register.
        runningPortsMask (int): A bitmask of ports which are in the run state. Bit 1 corresponds to port 1.
        runningPortsCount (int): A count of running ports.
        portCount (int): The number of ports the device has.
    """
    
    def __init__(self, deviceType, returnPort, runningPortsMask, runningPortsCount, portCount):
        """Initialises a `STAR_system.STAR_structure_classes.NetworkDiscoveryInformation` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.NetworkDiscoveryInformation` class attributes.

        Raises:\n
            TypeError:\n
                deviceType is not a STAR_CFG_DEVICE_TYPE.\n
                Any other argument is not an int.\n
            ValueError:\n
                Any of the int parameters are negative.\n
        """

        if isinstance(deviceType, STAR_CFG_DEVICE_TYPE) is False:
            raise TypeError("deviceType must be STAR_CFG_DEVICE_TYPE.")
        if type(returnPort) != int:
            raise TypeError("returnPort must be int.")
        if type(runningPortsMask) != int:
            raise TypeError("runningPortsMask must be int.")
        if type(runningPortsCount) != int:
            raise TypeError("runningPortsCount must be int.")
        if type(portCount) != int:
            raise TypeError("portCount must be int.")

        if returnPort < 0:
            raise ValueError("returnPort cannot be negative.")
        if runningPortsMask < 0:
            raise ValueError("runningPortsMask cannot be negative.")
        if runningPortsCount < 0:
            raise ValueError("runningPortsCount cannot be negative.")
        if portCount < 0:
            raise ValueError("portCount cannot be negative.")

        self.deviceType = deviceType
        self.returnPort = returnPort
        self.runningPortsMask = runningPortsMask
        self.runningPortsCount = runningPortsCount
        self.portCount = portCount


class RoutingTableEntry(object):
    """A routing table entry.

    Holds the same data as a `STAR_system.STAR_structures.STAR_CFG_GAR_ENTRY` structure.

    Attributes:\n
        portMask (int): A bitmask of output ports the logical address will arbitrate for.
            Valid bits set are 1 through 28. It is not possible to access the configuration
            port (0) through logical addresses.
        priority (bool): Packets with the logical address for this entry with the
            priority bit set will be granted access to a particular output port in
            preference to packets whose logical addresses in the routing table have their
            priority bit set to zero.
        deleteHeader (bool): When set, the leading header byte of the input packet will
            be removed before it is transferred to the output port.
        invalidAddress (bool): When set, this indicates that the corresponding logical
            address is invalid. In any case, any packets arriving at the router with an
            invalid address are split and an address is reported in the port status register.
    """
    
    def __init__(self, portMask, priority, deleteHeader, invalidAddress):
        """Initialises a `STAR_system.STAR_structure_classes.RoutingTableEntry` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.RoutingTableEntry` class attributes.

        Raises:\n
            TypeError:\n
                portMask is not an int.\n
                priority, deleteHeader, or invalidAddress is not a bool.\n
            ValueError:\n
                portMask is negative.\n
        """

        if type(portMask) != int:
            raise TypeError("portMask must be int.")
        if type(priority) != bool:
            raise TypeError("priority must be bool.")
        if type(deleteHeader) != bool:
            raise TypeError("deleteHeader must be bool.")
        if type(invalidAddress) != bool:
            raise TypeError("invalidAddress must be bool.")
        if portMask < 0:
            raise ValueError("portMask cannot be negative.")

        self.portMask = portMask
        self.priority = priority
        self.deleteHeader = deleteHeader
        self.invalidAddress = invalidAddress


class RouterGlobalState(object):
    """A container for global router settings.

    Holds the same data as the `STAR_system.STAR_structures.STAR_CFG_ROUTER_GLOBAL_STATE` structure.

    Attributes:\n
        timeoutMode (STAR_system.STAR_enums.STAR_CFG_TIMEOUT_MODE): The timeout mode. See enum for valid values.
        timeoutPeriod (STAR_system.STAR_enums.STAR_CFG_PORT_TIMEOUT): The timeout period. See enum for valid values.
        startOnRequest (bool): If true, links will be automatically started when they have
            data to transfer. If the link cannot be started packets are discarded after the
            timeout period.
        disableOnSilence (bool): If true, links will be disabled after the timeout period 
            when data transfer completes.
        enableSelfAddressing (bool): If true, a packet can be routed out of the port on 
            which it arrived on. This is for debugging purposes. If this is false and a 
            packet is to be routed through the same port, an address error is reported and 
            the packet is discarded. If false, and a group adaptive routing packet is 
            received (a packet which can be routed through two or more ports, dependent on 
            the group adaptive routing table contents) which can be routed through the port 
            it arrived on then the packet is routed through one of the other ports and not 
            the port on which the packet arrived on. An address error is not reported.
    """
    
    def __init__(self, timeoutMode, timeoutPeriod, startOnRequest, disableOnSilence, enableSelfAddressing):
        """Initialises a `STAR_system.STAR_structure_classes.RouterGlobalState` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.RouterGlobalState` class attributes.

        Raises:\n
            TypeError:\n
                timeoutMode is not a STAR_CFG_TIMEOUT_MODE.\n
                timeoutPeriod is not a STAR_CFG_PORT_TIMEOUT.\n
                startOnRequest, disableOnSilence or enableSelfAddressing is not a bool.\n
        """

        if isinstance(timeoutMode, STAR_CFG_TIMEOUT_MODE) is False:
            message = "timeoutMode must be STAR_CFG_TIMEOUT_MODE."
            message += "See enum for valid values."
            raise TypeError(message)
        if isinstance(timeoutPeriod, STAR_CFG_PORT_TIMEOUT) is False:
            message = "timeoutPeriod must be STAR_CFG_PORT_TIMEOUT. "
            message += "See enum for valid values."
            raise TypeError(message)
        if type(startOnRequest) != bool:
            raise TypeError("startOnRequest must be bool.")
        if type(disableOnSilence) != bool:
            raise TypeError("disableOnSilence must be bool.")
        if type(enableSelfAddressing) != bool:
            raise TypeError("enableSelfAddressing must be bool.")

        self.timeoutMode = timeoutMode
        self.timeoutPeriod = timeoutPeriod
        self.startOnRequest = startOnRequest
        self.disableOnSilence = disableOnSilence
        self.enableSelfAddressing = enableSelfAddressing


class ConfigPortErrors(object):
    """A container for errors that may be present on a device's configuration port.

    If an attribute of an instance of this class is set, then the error it
    represents is present.

    This class holds the same data as the `STAR_system.STAR_structures.STAR_CFG_CONFIG_PORT_ERRORS` structure.

    Attributes:\n
        errorCount (int): A count of errors present on the configuration port.
        portTimeoutError (bool): The port timeout error bit is set when a timeout
            event is detected by the configuration port routing logic.
        invalidHeaderCRC (bool): The invalid header CRC bit is set when the header
            CRC is invalid.
        invalidDataCRC (bool): The invalid data CRC is set when the data field of
            the packet is corrupted and the CRC does not match the internally
            generated CRC.
        invalidDestinationKey (bool): The invalid destination key bit is set when
            the destination key in the command packet is invalid.
        commandNotImplemented (bool): The command not implemented bit is set when
            the command code is a valid RMAP code but the command is not supported
            by the SpaceWire router.
        invalidDataLength (bool): The invalid data length bit is set when a data
            length error is detected.
        invalidRMWDataLength (bool): The read modify write command data length is
            invalid. The expected length is 8.
        invalidDestinationLogicalAddress (bool): The invalid destination logical
            address bit is set when the destination logical address in the command
            packet is not the default value of 254.
        earlyEOP (bool): The early EOP bit is set when the command packet is
            terminated before the end of packet with an EOP.
        lateEOP (bool): The late EOP bit is set when the command packet is not
            terminated correctly and trailing bytes are detected before the end of
            packet.
        earlyEEP (bool): The early EEP bit is set when the command packet is
            terminated before the end of packet with an EEP.
        lateEEP (bool): The late EEP bit is set when the command packet is not
            terminated correctly and trailing bytes are detected before the end of
            the packet.
        verifyBufferOverrun (bool): The verify buffer overrun error bit is set
            when a verified write command is performed and the data length is not 4.
        invalidRegisterAddress (bool): The invalid register address bit is set when
            an unknown register address is given in the command packet or a write
            is attempted to a read only register.
        unsupportedProtocol (bool): The unsupported protocol error bit is set when
            a command packet is received with a protocol identifier which is not
            the RMAP protocol identifier (0x01).
        sourceLogicalAddressError (bool): The source logical address error bit is
            set when an invalid source logical address is received.
        sourcePathAddressError (bool): This bit is set when an invalid source
            address path is received. This error is not used for the SpW-10X.
        cargoTooLarge (bool): The RMAP command packet is too large.
        unusedRMAPCommandOrPacketType (bool): The command code is an unused
            command code or the packet type is invalid.
    """

    def __init__(self, errorCount, portTimeoutError, invalidHeaderCRC,
                 invalidDataCRC, invalidDestinationKey, commandNotImplemented,
                 invalidDataLength, invalidRMWDataLength,
                 invalidDestinationLogicalAddress, earlyEOP, lateEOP, earlyEEP,
                 lateEEP, verifyBufferOverrun, invalidRegisterAddress,
                 unsupportedProtocol, sourceLogicalAddressError,
                 sourcePathAddressError, cargoTooLarge,
                 unusedRMAPCommandOrPacketType):
        """Initialises a config port errors object.

        Args:\n
            See `STAR_system.STAR_structure_classes.ConfigPortErrors` class attributes.

        Raises:\n
            TypeError:\n
                errorCount is not an int.\n
                Any other argument is not a bool.\n
            ValueError:\n
                errorCount is negative.\n
        """

        if type(errorCount) != int:
            raise TypeError("errorCount must be int.")
        if type(portTimeoutError) != bool:
            raise TypeError("portTimeoutError must be bool.")
        if type(invalidHeaderCRC) != bool:
            raise TypeError("invalidHeaderCRC must be bool.")
        if type(invalidDataCRC) != bool:
            raise TypeError("invalidDataCRC must be bool.")
        if type(invalidDestinationKey) != bool:
            raise TypeError("invalidDestinationKey must be bool.")
        if type(commandNotImplemented) != bool:
            raise TypeError("commandNotImplemented must be bool.")
        if type(invalidDataLength) != bool:
            raise TypeError("invalidDataLength must be bool.")
        if type(invalidRMWDataLength) != bool:
            raise TypeError("invalidRMWDataLength must be bool.")
        if type(invalidDestinationLogicalAddress) != bool:
            raise TypeError("invalidDestinationLogicalAddress must be bool.")
        if type(earlyEOP) != bool:
            raise TypeError("earlyEOP must be bool.")
        if type(lateEOP) != bool:
            raise TypeError("lateEOP must be bool.")
        if type(earlyEEP) != bool:
            raise TypeError("earlyEEP must be bool.")
        if type(lateEEP) != bool:
            raise TypeError("lateEEP must be bool.")
        if type(verifyBufferOverrun) != bool:
            raise TypeError("verifyBufferOverrun must be bool.")
        if type(invalidRegisterAddress) != bool:
            raise TypeError("invalidRegisterAddress must be bool.")
        if type(unsupportedProtocol) != bool:
            raise TypeError("unsupportedProtocol must be bool.")
        if type(sourceLogicalAddressError) != bool:
            raise TypeError("sourceLogicalAddressError must be bool.")
        if type(cargoTooLarge) != bool:
            raise TypeError("cargoTooLarge must be bool.")
        if type(unusedRMAPCommandOrPacketType) != bool:
            raise TypeError("unusedRMAPCommandOrPacketType must be bool.")
        if errorCount < 0:
            raise ValueError("Invalid errorCount. Error count cannot be negative.")

        self.errorCount = errorCount
        self.portTimeoutError = portTimeoutError
        self.invalidHeaderCRC = invalidHeaderCRC
        self.invalidDataCRC = invalidDataCRC
        self.invalidDestinationKey = invalidDestinationKey
        self.commandNotImplemented = commandNotImplemented
        self.invalidDataLength = invalidDataLength
        self.invalidRMWDataLength = invalidRMWDataLength
        self.invalidDestinationLogicalAddress = invalidDestinationLogicalAddress
        self.earlyEOP = earlyEOP
        self.lateEOP = lateEOP
        self.earlyEEP = earlyEEP
        self.lateEEP = lateEEP
        self.verifyBufferOverrun = verifyBufferOverrun
        self.invalidRegisterAddress = invalidRegisterAddress
        self.unsupportedProtocol = unsupportedProtocol
        self.sourceLogicalAddressError = sourceLogicalAddressError
        self.sourcePathAddressError = sourcePathAddressError
        self.cargoTooLarge = cargoTooLarge
        self.unusedRMAPCommandOrPacketType = unusedRMAPCommandOrPacketType


class ExternalPortErrors(object):
    """A container for errors that may be present on an external port.

    This class holds the same information as the `STAR_system.STAR_structures.STAR_CFG_EXTERNAL_PORT_ERRORS`
    structure.

    If an attribute of an instance of this class is set, then the error it
    represents is present.

    Attributes:\n
        errorCount (int): A count of errors present on the external port.
        packetAddress (bool): A packet was received with an invalid address, either
            due to an unknown port, or an invalid logical address. This is also
            generated when an empty packet is passed to the external port.
        portTimeout (bool): The port has become blocked for a period of time. A
            packet could not be routed to a destination port before the port
            timeout occurred.
    """

    def __init__(self, errorCount, packetAddress, portTimeout):
        """Initialises a `STAR_system.STAR_structure_classes.ExternalPortErrors` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.ExternalPortErrors` class attributes.

        Raises:\n
            TypeError:\n
                errorCount is not an int.\n
                packetAddress or portTimeout is not a bool.\n
            ValueError:\n
                errorCount is negative.\n
        """

        if type(errorCount) != int:
            raise TypeError("errorCount must be int.")
        if type(packetAddress) != bool:
            raise TypeError("packetAddress must be bool.")
        if type(portTimeout) != bool:
            raise TypeError("portTimeout must be bool.")
        if errorCount < 0:
            raise ValueError("Invalid errorCount. Error cannot be negative.")

        self.errorCount = errorCount
        self.packetAddress = packetAddress
        self.portTimeout = portTimeout


class ExternalPortStatus(object):
    """Container for the status of an external port.

    This class holds the same data as the `STAR_system.STAR_structures.STAR_CFG_EXTERNAL_PORT_STATUS`
    structure.

    Attributes:\n
        inputBufferEmpty (bool): True if the external port input buffer is empty.
            The input buffer writes data to the SpaceWire router.
        inputBufferFull (bool): True if the external port input buffer is full.
        outputBufferEmpty (bool): True if the external output buffer is emtpy.
            The output buffer writes data to the external device connected to the external port.
        outputBufferFull (bool): True if the external output port buffer is full.
    """

    def __init__(self, inputBufferEmpty, inputBufferFull, outputBufferEmpty, outputBufferFull):
        """Initialises a `STAR_system.STAR_structure_classes.ExternalPortStatus` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.ExternalPortStatus` class attributes.

        Raises:\n
            TypeError:\n
                Any of the arguments is not a bool.
        """

        if type(inputBufferEmpty) != bool:
            raise TypeError("inputBufferEmpty must be bool.")
        if type(inputBufferFull) != bool:
            raise TypeError("inputBufferFull must be bool.")
        if type(outputBufferEmpty) != bool:
            raise TypeError("outputBufferEmpty must be bool.")
        if type(outputBufferFull) != bool:
            raise TypeError("outputBufferFull must be bool.")

        self.inputBufferEmpty = inputBufferEmpty
        self.inputBufferFull = inputBufferFull
        self.outputBufferEmpty = outputBufferEmpty
        self.outputBufferFull = outputBufferFull


class LinkPortErrors(object):
    """A container for errors that may be present on a SpaceWire link.

    This class holds the same data as the `STAR_system.STAR_structures.STAR_CFG_SPW_LINK_ERRORS` structure.

    Attributes:\n
        errorCount (int): A count of errors present on the link port.
        packetAddress (bool): True if a packet was received with an invalid
            address, either due to an unknown port, or an invalid logical address.
        portTimeout (bool): True if the port has become blocked for a period of
            time. A packet could not be routed to a destination port before the
            port timeout occurred.
        disconnect (bool): True if a disconnect error occurred on the link. No
            activity occurred on the link for the disconnect timeout period.
        parity (bool): True if a parity was detected on a character parity bit.
        escape (bool): True if an invalid escape code was received on the link
            (ESC-ESC, ESC-EOP or ESC-EEP).
        credit (bool): True if a credit error occurred on the link.
        characterSequence (bool): True if a character sequence error occurred
            on the link. This indicates a time-code or data character was received
            before the first FCT.
    """

    def __init__(self, errorCount, packetAddress, portTimeout, disconnect, parity,
                 escape, credit, characterSequence):
        """Initialises a `STAR_system.STAR_structure_classes.LinkPortErrors` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.LinkPortErrors` class attributes.

        Raises:\n
            TypeError:\n
                errorCount is not an int.\n
                Any other argument is not a bool.\n
            ValueError:\n
                errorCount is negative.
        """

        if type(errorCount) != int:
            raise TypeError("errorCount must be int.")
        if type(packetAddress) != bool:
            raise TypeError("packetAddress must be bool.")
        if type(portTimeout) != bool:
            raise TypeError("portTimeout must be bool.")
        if type(disconnect) != bool:
            raise TypeError("disconnect must be bool.")
        if type(parity) != bool:
            raise TypeError("parity must be bool.")
        if type(escape) != bool:
            raise TypeError("escape must be bool.")
        if type(credit) != bool:
            raise TypeError("credit must be bool.")
        if type(characterSequence) != bool:
            raise TypeError("characterSequence must be bool.")
        if errorCount < 0:
            raise ValueError("Invalid errorCount. Error count cannot be negative.")

        self.errorCount = errorCount
        self.packetAddress = packetAddress
        self.portTimeout = portTimeout
        self.disconnect = disconnect
        self.parity = parity
        self.escape = escape
        self.credit = credit
        self.characterSequence = characterSequence


class LinkStatus(object):
    """A container for the status of a SpaceWire link.

    This class holds the same data as the `STAR_system.STAR_structures.STAR_CFG_SPW_LINK_STATUS` structure,
    except that in `STAR_system.STAR_structures.STAR_CFG_SPW_LINK_STATUS` the linkState field is an int, whereas here
    it is a `STAR_system.STAR_enums.STAR_CFG_SPW_LINK_STATE` enum.

    Attributes:\n
        triState (bool): When set, the SpaceWire link LVDS drivers are in tri-state
            mode.
        disable (bool): When set, the SpaceWire link will be disabled as defined
            in the SpaceWire standard. The SpaceWire port will not start and will
            not respond to any attempt to make a connection by the other end of
            the link.
        start (bool): When set, the SpaceWire link will initiate start-up as
            defined in the SpaceWire standard. The SpaceWire port will try to make
            a connection with the other end of the link.
        autoStart (bool): When set, the SpaceWire link will auto-start as defined
            in the SpaceWire standard. The SpaceWire port will wait until the other
            end of the link tries to make a connection (sending NULLs) and will
            then automatically start.
        running (bool): Set when the SpaceWire interface state machine is in the
            Run state.
        linkState (STAR_system.STAR_enums.STAR_CFG_SPW_LINK_STATE): The state of the interface state machine.
            See enum for valid values.
    """

    def __init__(self, triState, disable, start, autoStart, running, linkState):
        """Initialises `STAR_system.STAR_structure_classes.LinkStatus` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.LinkStatus` class attributes.

        Raises:\n
            TypeError:\n
                linkState is not a STAR_CFG_SPW_LINK_STATE.\n
                Any other attribute is not a bool.\n
        """

        if type(triState) != bool:
            raise TypeError("triState must be bool.")
        if type(disable) != bool:
            raise TypeError("disable must be bool.")
        if type(start) != bool:
            raise TypeError("start must be bool.")
        if type(autoStart) != bool:
            raise TypeError("autoStart must be bool.")
        if type(running) != bool:
            raise TypeError("running must be bool.")
        if isinstance(linkState, STAR_CFG_SPW_LINK_STATE) is False:
            message = "linkState must be STAR_CFG_SPW_LINK_STATE."
            message += " See enum for valid values."
            raise TypeError(message)

        self.triState = triState
        self.disable = disable
        self.start = start
        self.autoStart = autoStart
        self.running = running
        self.linkState = linkState	


class HardwareInfo(object):
    """A container for hardware information such as hardware version and synthesis
    data of the FPGA code.\n

    This class contains the same data as the `STAR_system.STAR_structures.STAR_CFG_FPGA_INFO` structure.

    Attributes:\n
        major (int): Major version number.
        minor (int): Minor version number.
        edit (int): Version number edit.
        patch (int): Version number patch.
        year (int): Year value of time and date.
        month (int): Month value of time and date.
        day (int): Day value of time and date.
        hour (int): Hour value of time and date.
        minute (int): Minute value of time and date.
    """

    def __init__(self, major, minor, edit, patch, year, month, day, hour, minute):
        """Initialises a `STAR_system.STAR_structure_classes.HardwareInfo` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.HardwareInfo` class attributes.

        Raises:\n
            TypeError:\n
                Any argument is not an int.\n
            ValueError:\n
                major, minor, edit or patch is negative.\n
                year is less than 1990.\n
                month is not in the range 1-12.\n
                day is not in the range 1-31.\n
                hour is not in the range 0-23.\n
                minute is not in the range 0-59.\n
        """

        if type(major) != int:
            raise TypeError("major must be int.")
        if type(minor) != int:
            raise TypeError("minor must be int.")
        if type(edit) != int:
            raise TypeError("edit must be int.")
        if type(patch) != int:
            raise TypeError("patch must be int.")
        if type(year) != int:
            raise TypeError("year must be int.")
        if type(month) != int:
            raise TypeError("month must be int.")
        if type(day) != int:
            raise TypeError("day must be int.")
        if type(hour) != int:
            raise TypeError("hour must be int.")
        if type(minute) != int:
            raise TypeError("minute must be int.")
        if major < 0:
            raise ValueError("Invalid major. Major version number cannot be negative.")
        if minor < 0:
            raise ValueError("Invalid minor. Minor version number cannot be negative.")
        if edit < 0:
            raise ValueError("Invalid edit. Edit cannot be negative.")
        if patch < 0:
            raise ValueError("Invalid patch. Patch cannot be negative.")
        if year < 1990:
            raise ValueError("Invalid year.")
        if month < 1 or month > 12:
            raise ValueError("Invalid month. Month must be in the range 1 to 12.")
        if day < 1 or day > 31:
            raise ValueError("Invalid day. Day must be in the range 1 to 31.")
        if hour < 0 or hour > 23:
            raise ValueError("Invalid hour. Hour must be in the range 0 to 23.")
        if minute < 0 or minute > 59:
            raise ValueError("Invalid minute. Minute must be in the range 0 to 59.")

        self.major = major
        self.minor = minor
        self.edit = edit
        self.patch = patch
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

class StarIpAddressType(object):
    """A container for STAR IP address type objects.

    This class holds the same data as the `STAR_system.STAR_structures.STAR_IP_ADDRESS_TYPE` structure.

    Attributes:\n
        IPVersion (int): Contains the IP protocol version.
        IPAddress (list): List containing the IP address bytes.
    """

    def __init__(self, IPVersion, IPAddress):
        """Initialises a `STAR_system.STAR_structure_classes.StarIpAddressType` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.StarIpAddressType` class attributes.

        Raises:\n
            TypeError:\n
                IPVersion is not an int.\n
                IPAddress is not a list.\n
                Any value in IPAddress is not an int.
            ValueError:\n
                IPVersion is negative or greater than 255.
                Any value in IPAddress is negative or greater than 255.
        """

        if type(IPVersion) != int:
            raise TypeError("IPVersion must be int.")
        if type(IPAddress) != list:
            raise TypeError("IPAddress must be a list.")
        if IPVersion < 0 or IPVersion > 255:
            raise ValueError("IPVersion must be positive and less than 255.")
        for addressByte in IPAddress:
            if type(addressByte) != int:
                raise TypeError("Every element in IPAddress must be an int.")
            if addressByte < 0 or addressByte > 255:
                raise ValueError("Every element in IPAddress must be an 8-bit value.")

        self.IPVersion = IPVersion
        self.IPAddress = IPAddress


class StarBroadcastMessage(object):
    """A container for STAR broadcast message objects.

    This class holds the same data as the `STAR_system.STAR_structures.STAR_BROADCAST_MESSAGE` structure.

    Attributes:\n
        channel: (unsigned char) The broadcast message's channel (BC field).
        type: (unsigned char) The broadcast message's type (B_TYPE field).
        status: (unsigned char) The broadcast message's status (STATUS field).
        dataWord1: (unsigned int) The broadcast message's first data word.
        dataWord2: (unsigned int) The broadcast message's second data word.
    """

    def __init__(self, channel, bType, status, dataWord1, dataWord2):
        """Initialises a `STAR_system.STAR_structure_classes.StarBroadcastMessage` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.StarBroadcastMessage` class attributes.

        Raises:\n
            TypeError:\n
                channel is not an int.\n
                bType is not an int.\n
                status is not an int.\n
                dataWord1 is not an int.\n
                dataWord2 is not an int.\n
            ValueError:\n
                channel is negative or greater than 255.
                bType is negative or greater than 255.
                status is negative or greater than 255.
                dataWord1 is negative.
                dataWord2 is negative.
        """
        if type(channel) != int:
            raise TypeError("channel must be an int.")
        if type(bType) != int:
            raise TypeError("bType must be an int.")
        if type(status) != int:
            raise TypeError("status must be an int.")
        if type(dataWord1) != int:
            raise TypeError("dataWord1 must be an int.")
        if type(dataWord2) != int:
            raise TypeError("dataWord2 must be an int.")

        if channel < 0 or channel > 255:
            raise ValueError("channel must be positive and less than 255.")
        if bType < 0 or bType > 255:
            raise ValueError("bType must be positive and less than 255.")
        if status < 0 or status > 255:
            raise ValueError("status must be positive and less than 255.")
        if dataWord1 < 0:
            raise ValueError("dataWord1 must be positive.")
        if dataWord2 < 0:
            raise ValueError("dataWord2 must be positive.")

        self.channel = channel
        self.bType = bType
        self.status = status
        self.dataWord1 = dataWord1
        self.dataWord2 = dataWord2

class RMAPCommandParameters(object):
    """Parameters of an RMAP command.\n

    This class contains the same data as the `STAR_system.STAR_structures.RMAP_COMMAND_PARAMETERS` structure.

    Attributes:\n
        targetLogicalAddress (int): Target logical address.
        command (int): Command.
        key (int): Key.
        protocolId (int): Protocol ID.
        extendedAddress (int): Extended address.
        dataLength (int): Data length.
        address (int): Address.
        initiatorLogicalAddress (int): Initiator logical address.
        transactionId (int): Transaction ID.
    """

    def __init__(self, targetLogicalAddress, command, key, protocolId, extendedAddress, dataLength, address,
                 initiatorLogicalAddress, transactionId):
        """Initialises a `STAR_system.STAR_structure_classes.RMAPCommandParameters` object.

        Args:\n
            See `STAR_system.STAR_structure_classes.RMAPCommandParameters` class attributes.

        Raises:\n
            TypeError:\n
                Any argument is not an int.\n
            ValueError:\n
                Any argument is negative.\n
                targetLogicalAddress is greater than 255.\n
                command is greater than 255.\n
                key is greater than 255.\n
                protocolId is greater than 255.\n
                extendedAddress is greater than 255.\n
                initiatorLogicalAddress is greater than 255.\n
        """

        if type(targetLogicalAddress) != int:
            raise TypeError("targetLogicalAddress must be int.")
        if type(command) != int:
            raise TypeError("command must be int.")
        if type(key) != int:
            raise TypeError("key must be int.")
        if type(protocolId) != int:
            raise TypeError("protocolId must be int.")
        if type(extendedAddress) != int:
            raise TypeError("extendedAddress must be int.")
        if type(dataLength) != int:
            raise TypeError("dataLength must be int.")
        if type(address) != int:
            raise TypeError("address must be int.")
        if type(initiatorLogicalAddress) != int:
            raise TypeError("initiatorLogicalAddress must be int.")
        if type(transactionId) != int:
            raise TypeError("transactionId must be int.")
        if targetLogicalAddress < 0 or targetLogicalAddress > 255:
            raise ValueError("Invalid targetLogicalAddress value."
                             " targetLogicalAddress cannot be negative nor be greater than 255.")
        if command < 0 or command > 255:
            raise ValueError("Invalid command value. command cannot be negative nor be greater than 255.")
        if key < 0 or key > 255:
            raise ValueError("Invalid key value. key cannot be negative nor be greater than 255.")
        if protocolId < 0 or protocolId > 255:
            raise ValueError("Invalid protocolId value. protocolId cannot be negative nor be greater than 255.")
        if extendedAddress < 0 or extendedAddress > 255:
            raise ValueError("Invalid extendedAddress value. "
                             "extendedAddress cannot be negative nor be greater than 255.")
        if initiatorLogicalAddress < 0 or initiatorLogicalAddress > 255:
            raise ValueError("Invalid initiatorLogicalAddress value. "
                             "initiatorLogicalAddress cannot be negative nor be greater than 255.")

        self.targetLogicalAddress = targetLogicalAddress
        self.command = command
        self.key = key
        self.protocolId = protocolId
        self.extendedAddress = extendedAddress
        self.dataLength = dataLength
        self.address = address
        self.initiatorLogicalAddress = initiatorLogicalAddress
        self.transactionId = transactionId
