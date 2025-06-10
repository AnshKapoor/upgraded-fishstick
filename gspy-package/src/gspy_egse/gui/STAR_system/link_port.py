"""Represents a SpaceWire link port on a device.

Brief:\n
    Represents a SpaceWire link port on a device.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

import os
from ctypes import *
from typing import Union

from gspy_egse.gui.STAR_system import CONFIG_LIB, STAR_CONFIG_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError, StatusCode
from gspy_egse.gui.STAR_system.STAR_enums import STAR_CONFIG_OP_RESULT, SPW_ACTION, SPW_ERROR, STAR_DEVICE_TYPE,\
                                   STAR_CFG_SPW_LINK_STATE
from gspy_egse.gui.STAR_system.STAR_structures import STAR_CFG_SPW_LINK_STATUS, STAR_CFG_SPW_LINK_ERRORS, STAR_CFG_BRICK_MK2_ERRORS
from gspy_egse.gui.STAR_system.STAR_structure_classes import LinkStatus, LinkPortErrors
from gspy_egse.gui.STAR_system.device import Device
from gspy_egse.gui.STAR_system.port import Port

StatusCodes = StatusCode()

# Load C API
systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    try:
        config_lib = windll.LoadLibrary(CONFIG_LIB)
    except Exception:
        config_lib = None
        print(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

elif systemType == "posix":
    try:
        config_lib = cdll.LoadLibrary(CONFIG_LIB)
    except Exception:
        config_lib = None
        print(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)


class LinkPort(Port):
    """Represents a link port on a device.
    
    Attributes:\n
        owningDeviceID (int): The ID of the device which owns the port.
        portNumber (int): The port number.
    """

    def __init__(self, owningDeviceID, portNumber):
        """Constructor:\n
            Initialises a `STAR_system.link_port.LinkPort` object.

        Args:\n
            owningDeviceID (int): The ID of the device which owns the port.
            portNumber (int): The port number.

        Raises:\n
            TypeError:\n
                Errors from Port class.\n
            ValueError:\n
                Errors from Port class.\n
        """
        super().__init__(owningDeviceID, portNumber)


    def getTimeCodeEventsOnPortEnabled(self) -> bool:
        """Gets and returns whether time-code events are enabled on the port.

        Returns True if time-code events are enabled on this port, False otherwise.

        This method is compatible with PCIe and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether time-code events are enabled or not.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimeCodeEventsOnPortEnabled.argtypes = [c_uint32, c_uint8, POINTER(c_int32)]
        config_lib.CFG_getTimeCodeEventsOnPortEnabled.restype = c_int32

        status = config_lib.CFG_getTimeCodeEventsOnPortEnabled(c_uint32(self.owningDeviceID),
                                                               c_uint8(self.portNumber), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def enableTimeCodeEventsOnPort(self):
        """Selectively enables time-code events on the channel attached to the port.

        This method is compatible with PCIe and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable time-code events on the port.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableTimeCodeEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_enableTimeCodeEventsOnPort.restype = c_int32

        status = config_lib.CFG_enableTimeCodeEventsOnPort(c_uint32(self.owningDeviceID),
                                                           c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableTimeCodeEventsOnPort(self):
        """Selectively disables time-code events on the channel attached to this port.

        This method is compatible with PCIe devices and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable time-code events on the port.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableTimeCodeEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_disableTimeCodeEventsOnPort.restype = c_int32

        status = config_lib.CFG_disableTimeCodeEventsOnPort(c_uint32(self.owningDeviceID),
                                                            c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def startPeriodicAction(self, count, action):
        """Starts a periodic action on the port.

        To stop a periodic action use `STAR_system.link_port.LinkPort.stopPeriodicAction`.\n

        Periodic actions make use of the same on-board registers as error
        injection, therefore error injection cannot be used when periodic
        actions are in progress.\n

        This method is only compatible with PCI Mk2 devices.

        Args:\n
            count (int): Number of device clock cycles between action
                repetitions. See `STAR_system.device.Device.getDeviceClockRate` for obtaining
                the device's clock rate.
            action (STAR_system.STAR_enums.SPW_ACTION): Action to be performed.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to start the periodic action.\n
            TypeError:\n
                count was not an int.
                action was not a SPW_ACTION.
            ValueError:\n
                count was negative.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(count) != int:
            raise TypeError("count must be int.")
        if isinstance(action, SPW_ACTION) is False:
            raise TypeError("action must be SPW_ACTION.")
        if count < 0:
            raise ValueError("count must be positive.")

        # Set argument types and return type of the C function
        config_lib.CFG_startPeriodicAction.argtypes = [c_uint32, c_uint8, c_uint32, SPW_ACTION]
        config_lib.CFG_startPeriodicAction.restype = c_int32

        status = config_lib.CFG_startPeriodicAction(c_uint32(self.owningDeviceID), c_uint8(self.portNumber),
                                                    c_uint32(count), action)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def stopPeriodicAction(self):
        """Stops a periodic actions on the port.

        Periodic actions are started by calling `STAR_system.link_port.LinkPort.startPeriodicAction`.

        This method is only compatible with PCI Mk2 devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to stop the periodic action.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_stopPeriodicAction.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_stopPeriodicAction.restype = c_int32

        status = config_lib.CFG_stopPeriodicAction(c_uint32(self.owningDeviceID), c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getSpaceWireLinkErrors(self) -> LinkPortErrors:
        """Gets any errors present on a SpaceWire link. The link port errors are returned in the form of
        a `STAR_system.STAR_structure_classes.LinkPortErrors` object.

        Errors on a port are latched until cleared with `STAR_system.port.Port.clearPortErrors`.

        This method is compatible with all devices.
         
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the port status control.\n
                The C API failed to get link error info.\n
            TypeError:\n
                Errors from LinkPortErrors class.\n
            ValueError:\n
                Errors from LinkPortErrors class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            portStatusControl = self.getPortStatusControl()
        except STARAPIError:
            raise

        # Create pointer to be used in the C function call as parameter
        pErrorsStruct = pointer(STAR_CFG_SPW_LINK_ERRORS())

        # Set argument types and return type of the C function
        config_lib.CFG_getSpaceWireLinkErrors.argtypes = [c_uint32, POINTER(STAR_CFG_SPW_LINK_ERRORS)]
        config_lib.CFG_getSpaceWireLinkErrors.restype = c_int32

        status = config_lib.CFG_getSpaceWireLinkErrors(portStatusControl, pErrorsStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        errorsStruct = pErrorsStruct.contents

        # The STAR_CFG_EXTERNAL_PORT_ERRORS struct uses ctypes.c_chars to store
        # its data. These are interpreted as the python bytes data type and so
        # must be converted to ints / bools as appropriate.
        errorCount = int.from_bytes(errorsStruct.errorCount, byteorder="big")
        packetAddressError = bool(int.from_bytes(errorsStruct.packetAddress, byteorder="big"))
        portTimeoutError = bool(int.from_bytes(errorsStruct.portTimeout, byteorder="big"))
        disconnectError = bool(int.from_bytes(errorsStruct.disconnect, byteorder="big"))
        parityError = bool(int.from_bytes(errorsStruct.parity, byteorder="big"))
        escapeError = bool(int.from_bytes(errorsStruct.escape, byteorder="big"))
        creditError = bool(int.from_bytes(errorsStruct.credit, byteorder="big"))
        characterSequenceError = bool(int.from_bytes(errorsStruct.characterSequence, byteorder="big"))

        try:
            errors = LinkPortErrors(errorCount, packetAddressError, portTimeoutError,
                                    disconnectError, parityError, escapeError,
                                    creditError, characterSequenceError)
        except (TypeError, ValueError):
            raise

        return errors

    def getSpaceWireLinkStatus(self) -> LinkStatus:
        """Gets and returns the status of a SpaceWire link.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the port status control.\n
                The C API failed to get link status info.\n
            TypeError:\n
                Errors from LinkStatus class.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            portStatusControl = self.getPortStatusControl()
        except STARAPIError:
            raise

        # Create pointer to be used in the C function call as parameter
        pLinkStatusStruct = pointer(STAR_CFG_SPW_LINK_STATUS())

        # Set argument types and return type of the C function
        config_lib.CFG_getSpaceWireLinkStatus.argtypes = [c_uint32, POINTER(STAR_CFG_SPW_LINK_STATUS)]
        config_lib.CFG_getSpaceWireLinkStatus.restype = c_int32

        cApiStatus = config_lib.CFG_getSpaceWireLinkStatus(portStatusControl, pLinkStatusStruct)

        if cApiStatus < 0:
            raise STARAPIError(StatusCodes.getMessage(cApiStatus))

        linkStatusStruct = pLinkStatusStruct.contents
        # The linkState returned by the C API is an int reference to an enum. We will convert it
        # to the correct Enum object

        linkState = STAR_CFG_SPW_LINK_STATE(linkStatusStruct.linkState)

        try:
            linkStatus = LinkStatus(linkStatusStruct.triState, linkStatusStruct.disable,
                                    linkStatusStruct.start, linkStatusStruct.autoStart,
                                    linkStatusStruct.running, linkState)
        except TypeError:
            raise

        return linkStatus

    def setSpaceWireLinkStatus(self, linkStatus):
        """Sets the state of a SpaceWire link.

        This method works with all devices.

        Args:\n
            linkStatus (STAR_system.STAR_structure_classes.LinkStatus): The new link status. Note that the linkState and
                running fields of the `STAR_system.STAR_structure_classes.LinkStatus` object are ignored by this method.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the link status.\n
            TypeError:\n
                linkStatus must be a LinkStatus object.
        """

        # The LinkStatus object must be converted to a STAR_CFG_SPW_LINK_STATE
        # structure so it can be accepted by the C API.

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if isinstance(linkStatus, LinkStatus) is False:
            raise TypeError("linkStatus must be a LinkStatus object.")

        linkStatusStruct = STAR_CFG_SPW_LINK_STATUS(linkStatus.triState, linkStatus.disable, linkStatus.start,
                                                    linkStatus.autoStart, linkStatus.running, linkStatus.linkState)
        pLinkStatusStruct = pointer(linkStatusStruct)

        # Set argument types and return type of the C function
        config_lib.CFG_setSpaceWireLinkStatus.argtypes = [c_uint32, c_uint8, POINTER(STAR_CFG_SPW_LINK_STATUS)]
        config_lib.CFG_setSpaceWireLinkStatus.restype = c_int32

        cApiStatus = config_lib.CFG_setSpaceWireLinkStatus(c_uint32(self.owningDeviceID),
                                                           c_uint8(self.portNumber), pLinkStatusStruct)

        if cApiStatus < 0:
            raise STARAPIError(StatusCodes.getMessage(cApiStatus))

    def startLink(self):
        """Starts a SpaceWire link by setting the start bit, and clearing the disable bit.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to start the link.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_startLink.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_startLink.restype = c_int32

        status = config_lib.CFG_startLink(c_uint32(self.owningDeviceID), c_uint8(self.portNumber))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def stopLink(self):
        """Stops a SpaceWire link by clearing the start bit, and setting the disable bit.

        If auto-start is enabled the link will start again as soon as it receives NULLs.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to stop the link.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_stopLink.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_stopLink.restype = c_int32

        status = config_lib.CFG_stopLink(c_uint32(self.owningDeviceID), c_uint8(self.portNumber))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableSpeedChangeEventsOnPort(self):
        """Selectively disables state change events on the port.

        Disabling speed change events will result in speed change event traffic 
        no longer being received on channel 0 when the link speed changes.\n

        This method is compatible with all device except the PCI Mk2.\n

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable speed change events.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableSpeedChangeEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_disableSpeedChangeEventsOnPort.restype = c_int32

        status = config_lib.CFG_disableSpeedChangeEventsOnPort(c_uint32(self.owningDeviceID), c_uint8(self.portNumber))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableSpeedChangeEventsOnPort(self):
        """Selectively enables speed change events on the port.

        Enabling speed change events will result in speed change event traffic 
        being received on channel 0 when the link speed changes.\n

        This method is compatible with all device except the PCI Mk2.\n

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable speed change events.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableSpeedChangeEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_enableSpeedChangeEventsOnPort.restype = c_int32

        status = config_lib.CFG_enableSpeedChangeEventsOnPort(c_uint32(self.owningDeviceID),
                                                              c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableStateChangeEventsOnPort(self):
        """Selectively enables state change events on the port.\n

        Enabling state change events will result in state change event traffic 
        being received on channel 0 when the link changes to running or 
        disconnected.\n

        This method is compatible with all device except the PCI Mk2.\n

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable state change events.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableStateChangeEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_enableStateChangeEventsOnPort.restype = c_int32

        status = config_lib.CFG_enableStateChangeEventsOnPort(c_uint32(self.owningDeviceID),
                                                              c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getSpeedChangeEventsOnPortEnabled(self):
        """Gets whether speed change events are enabled on the port.
        Returns true of the speed change events are enabled on the port, False otherwise.

        This method is compatible with all device except the PCI Mk2.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether speed change events are enabled or not on this port.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getSpeedChangeEventsOnPortEnabled.argtypes = [c_uint32, c_uint8, POINTER(c_int32)]
        config_lib.CFG_getSpeedChangeEventsOnPortEnabled.restype = c_int32

        status = config_lib.CFG_getSpeedChangeEventsOnPortEnabled(c_uint32(self.owningDeviceID),
                                                                  c_uint8(self.portNumber), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def getStateChangeEventsOnPortEnabled(self):
        """Gets whether state change events are enabled for the port.
        Returns True if state change events are enabled on this port, False otherwise.

        This method is compatible with all device except the PCI Mk2.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether state change events are enabled or not on this port.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getStateChangeEventsOnPortEnabled.argtypes = [c_uint32, c_uint8, POINTER(c_int32)]
        config_lib.CFG_getStateChangeEventsOnPortEnabled.restype = c_int32

        status = config_lib.CFG_getStateChangeEventsOnPortEnabled(c_uint32(self.owningDeviceID),
                                                                  c_uint8(self.portNumber), pEnabled)
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def injectError(self, error):
        """Immediately injects the specified error on the port.

        This method is compatible with the Brick Mk2/Mk3/Mk4, GbE Brick,
        Router Mk2S, PCI Mk2, PCIe, SPLT and PXI devices.

        Args:\n
            error (STAR_system.STAR_enums.SPW_ERROR): The type of error to inject.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to inject the error.\n
            TypeError:\n
                error was not a SPW_ERROR.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if isinstance(error, SPW_ERROR) is False:
            raise TypeError("error must be SPW_ERROR.")

        # Set argument types and return type of the C function
        config_lib.CFG_injectError.argtypes = [c_uint32, c_uint8, SPW_ERROR]
        config_lib.CFG_injectError.restype = c_int32

        status = config_lib.CFG_injectError(c_uint32(self.owningDeviceID), c_uint8(self.portNumber), error)
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def injectErrors(self, parityError, escapeError, insertFCT, suppressFCT, incrementCredit, decrementCredit,
                     disconnect):
        """Inject the specified errors on the port.

        This method is compatible with the Brick Mk2/Mk3/Mk4, GbE Brick and Router Mk2S.

        Args:\n
            parityError (bool): Whether or not to inject a parity error.
            escapeError (bool): Whether or not not inject an escape error.
            insertFCT (bool): Whether or not an extra FCT should be inserted to cause an error.
            suppressFCT (bool): Whether or not an FCT should be suppressed to cause an error.
            incrementCredit (bool): Whether or not credit should be incremented to cause an error.
            decrementCredit (bool): Whether or not credit should be decremented to cause an error.
            disconnect (bool): Whether a disconnect error should occur.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to inject errors.\n
            TypeError:\n
                One or more of the input arguments was not a bool.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        args = [parityError, escapeError, insertFCT, suppressFCT, incrementCredit, decrementCredit, disconnect]
        for arg in args:
            if type(arg) != bool:
                raise TypeError("All arguments must be bool.")

        # Convert boolean arguments to the correct cType
        cParityError = c_char(int(parityError))
        cEscapeError = c_char(int(escapeError))
        cInsertFCT = c_char(int(insertFCT))
        cSuppressFCT = c_char(int(suppressFCT))
        cIncrementCredit = c_char(int(incrementCredit))
        cDecrementCredit = c_char(int(decrementCredit))
        cDisconnect = c_char(int(disconnect))

        errorStruct = STAR_CFG_BRICK_MK2_ERRORS(cParityError, cEscapeError, cInsertFCT, cSuppressFCT,
                                                cIncrementCredit, cDecrementCredit, cDisconnect)

        # Create pointer to structure to be used in function call as argument
        pErrorStruct = pointer(errorStruct)

        # Set argument types and return type of the C function
        config_lib.CFG_injectErrors.argtypes = [c_uint32, c_uint8, POINTER(STAR_CFG_BRICK_MK2_ERRORS)]
        config_lib.CFG_injectErrors.restype = c_int32

        status = config_lib.CFG_injectErrors(c_uint32(self.owningDeviceID),
                                             c_uint8(self.portNumber), pErrorStruct)
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableStateChangeEventsOnPort(self):
        """Selectively disables state change events on the port.

        Disabling state change events will result in state change event traffic 
        no longer being received on channel 0 when the link changes to running or
        disconnected.\n

        This method is compatible with all device except the PCI Mk2.\n

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable state change events.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableStateChangeEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_disableStateChangeEventsOnPort.restype = c_int32

        status = config_lib.CFG_disableStateChangeEventsOnPort(c_uint32(self.owningDeviceID),
                                                               c_uint8(self.portNumber))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getMeasuredLinkSpeed(self) -> int:
        """Gets and returns the current link speed measured on this port.
        The link speed is in 100 Kbit/s units.

        This method is compatible with all device except the PCI Mk2.
        
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get link speed.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        linkSpeed = c_uint16(0)
        pLinkSpeed = pointer(linkSpeed)

        # Set argument types and return type of the C function
        config_lib.CFG_getMeasuredLinkSpeed.argtypes = [c_uint32, c_uint8, POINTER(c_uint16)]
        config_lib.CFG_getMeasuredLinkSpeed.restype = c_int32

        status = config_lib.CFG_getMeasuredLinkSpeed(c_uint32(self.owningDeviceID),
                                                     c_uint8(self.portNumber), pLinkSpeed)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return linkSpeed.value

    def disableRxTimestampEventsOnPort(self):
        """Selectively disables receive timestamp events on the port. Disabling
        receive timestamp events will result in no timestamp information being
        provided after the packet.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disabled receive timestamp events.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableRxTimestampEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_disableRxTimestampEventsOnPort.restype = c_int32

        status = config_lib.CFG_disableRxTimestampEventsOnPort(c_uint32(self.owningDeviceID),
                                                               c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableRxTimestampEventsOnPort(self):
        """Selectively enables receive timestamp events on the port.

        Enabling receive timestamp events will result in the timestamp that the
        last packet was received at to be provided as a `STAR_system.timestamp_event.TimestampEvent`.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable receive timestamp events.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableRxTimestampEventsOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_enableRxTimestampEventsOnPort.restype = c_int32

        status = config_lib.CFG_enableRxTimestampEventsOnPort(c_uint32(self.owningDeviceID),
                                                              c_uint8(self.portNumber))
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getRxTimestampEventsOnPortEnabled(self):
        """Gets and returns whether receive timestamp events are enabled on the port.\n

        Returns True if receive timestamp events are enabled on this port, False otherwise.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether or not timestamp events are enabled.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getRxTimestampEventsOnPortEnabled.argtypes = [c_uint32, c_uint8, POINTER(c_int32)]
        config_lib.CFG_getRxTimestampEventsOnPortEnabled.restype = c_int32

        status = config_lib.CFG_getRxTimestampEventsOnPortEnabled(c_uint32(self.owningDeviceID),
                                                                  c_uint8(self.portNumber), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def getTransmitSignallingRate(self) -> int:
        """Gets and returns the transmit bit rate for the link.
        The returned signalling rate is in Mbit/s.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the transmit signalling rate.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        signallingRate = c_uint32(0)
        pSignallingRate = pointer(signallingRate)

        # Set argument types and return type of the C function
        config_lib.CFG_getTransmitSignallingRate.argtypes = [c_uint32, c_uint8, POINTER(c_uint32)]
        config_lib.CFG_getTransmitSignallingRate.restype = c_int32

        status = config_lib.CFG_getTransmitSignallingRate(c_uint32(self.owningDeviceID),
                                                          c_uint8(self.portNumber), pSignallingRate)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return signallingRate.value

    def setTransmitSignallingRate(self, bitRateMbitSec):
        """Sets the transmit bit rate on the link.

        The transmit bit rate of the link is given in Mbit/s. The bit rate
        will be between 2 Mbit/s and 400 Mbit/s inclusive, although 400 Mbit/s
        may not be achievable with every device type.\n

        For the SpaceWire PXI 12 Port Router device, clocks are shared by pairs of
        links. For example, setting the transmit bit rate for link 1 will also
        affect link 2. Similarly, links 3 and 4, 5 and 6, 7 and 8, 9 and 10, and
        11 and 12 share clocks. Note that the odd-numbered link must be used to
        set the transmit clock frequency for each pair of links.\n

        This method is compatible with all devices. However, depending upon the
        capabilities of the device, an exact bit rate may not be achievable.\n

        Args:\n
            bitRateMbitSec (int): Transmit bit rate in Mbit/s.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the transmit signalling rate.\n
            TypeError:\n
                bitRateMbitSec was not an int.\n
            ValueError:\n
                bitRateMbitSec was negative.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(bitRateMbitSec) != int:
            raise TypeError("bitRateMbitSec must be in.")
        if bitRateMbitSec < 0:
            raise ValueError("bitRateMbitSec must be positive.")

        # Set argument types and return type of the C function
        config_lib.CFG_setTransmitSignallingRate.argtypes = [c_uint32, c_uint8, c_uint32]
        config_lib.CFG_setTransmitSignallingRate.restype = c_int32

        status = config_lib.CFG_setTransmitSignallingRate(c_uint32(self.owningDeviceID),
                                                          c_uint8(self.portNumber),
                                                          c_uint32(bitRateMbitSec))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
