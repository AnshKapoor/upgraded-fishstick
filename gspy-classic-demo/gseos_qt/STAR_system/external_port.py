"""Represents an external port on a device.

Brief:\n
    Represents an external port on a device.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
from ctypes import *

from STAR_system import CONFIG_LIB, STAR_CONFIG_API_LIB_LOAD_ERROR_STR
from STAR_system.port import Port
from STAR_system.STAR_exceptions import STARAPIError, StatusCode
from STAR_system.STAR_structure_classes import ExternalPortErrors, ExternalPortStatus
from STAR_system.STAR_structures import STAR_CFG_EXTERNAL_PORT_ERRORS, STAR_CFG_EXTERNAL_PORT_STATUS
from STAR_system.STAR_enums import STAR_CONFIG_OP_RESULT

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


class ExternalPort(Port):
    """Represents an external port on a device.
    
    Attributes:\n
        owningDeviceID (int): The ID of the device which owns the port.
        portNumber (int): The port number.
    """

    def __init__(self, owningDeviceID, portNumber):
        """Constructor:\n
            Initialises a `STAR_system.external_port.ExternalPort` object.

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

    def getExternalPortErrors(self) -> ExternalPortErrors:
        """Gets and returns any errors present on an external port. The errors are returned in the form
        of an `STAR_system.STAR_structure_classes.ExternalPortErrors` object.

        Errors on a port are latched until cleared with `STAR_system.port.Port.clearPortErrors`.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the port status control.\n
                The C API failed to get external port error info.\n
            TypeError:\n
                Errors from ExternalPortErrors class.\n
            ValueError:\n
                Errors from ExternalPortErrors class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            portStatusControl = self.getPortStatusControl()
        except STARAPIError:
            raise

        pErrorsStruct = pointer(STAR_CFG_EXTERNAL_PORT_ERRORS())

        # Set argument types and return type of the C function
        config_lib.CFG_getExternalPortErrors.argtypes = [c_uint32, POINTER(STAR_CFG_EXTERNAL_PORT_ERRORS)]
        config_lib.CFG_getExternalPortErrors.restype = c_int32

        status = config_lib.CFG_getExternalPortErrors(portStatusControl, pErrorsStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        errorsStruct = pErrorsStruct.contents
        # The STAR_CFG_EXTERNAL_PORT_ERRORS struct uses ctypes.c_chars to store
        # its data. These are interpreted as the python bytes data type and so
        # must be converted to ints / bools as appropriate.
        errorCount = int.from_bytes(errorsStruct.errorCount, byteorder="big")
        packetAddressError = bool(int.from_bytes(errorsStruct.packetAddress, byteorder="big"))
        portTimeoutError = bool(int.from_bytes(errorsStruct.portTimeout, byteorder="big"))

        try:
            errors = ExternalPortErrors(errorCount, packetAddressError, portTimeoutError)
        except (TypeError, ValueError):
            raise

        return errors

    def getExternalPortStatus(self) -> ExternalPortStatus:
        """Gets and returns the status of the external port.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the port status control.\n
                The C API failed to get external port status info.\n
            TypeError:\n
                Errors from ExternalPortStatus class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            portStatusControl = self.getPortStatusControl()
        except STARAPIError:
            raise

        pPortStatusStruct = pointer(STAR_CFG_EXTERNAL_PORT_STATUS())

        # Set argument types and return type of the C function
        config_lib.CFG_getExternalPortStatus.argtypes = [c_uint32, POINTER(STAR_CFG_EXTERNAL_PORT_STATUS)]
        config_lib.CFG_getExternalPortStatus.restype = c_int32

        cApiStatus = config_lib.CFG_getExternalPortStatus(portStatusControl, pPortStatusStruct)

        if cApiStatus < 0:
            raise STARAPIError(StatusCodes.getMessage(cApiStatus))

        portStatusStruct = pPortStatusStruct.contents

        # The STAR_CFG_EXTERNAL_PORT_ERRORS struct uses ctypes.c_chars to store
        # its data. These are interpreted as the python bytes data type and so
        # must be converted to bools.
        inputBufferEmpty = bool(int.from_bytes(portStatusStruct.inputBufferEmpty, byteorder="big"))
        inputBufferFull = bool(int.from_bytes(portStatusStruct.inputBufferFull, byteorder="big"))
        outputBufferEmpty = bool(int.from_bytes(portStatusStruct.outputBufferEmpty, byteorder="big"))
        outputBufferFull = bool(int.from_bytes(portStatusStruct.outputBufferFull, byteorder="big"))

        try:
            externalPortStatus = ExternalPortStatus(inputBufferEmpty, inputBufferFull,
                                                    outputBufferEmpty, outputBufferFull)
        except TypeError:
            raise

        return externalPortStatus


