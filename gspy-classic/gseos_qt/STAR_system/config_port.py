"""Represents a configuration port on a device.

Brief:\n
    Represents a configuration port on a device.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
from ctypes import *

from STAR_system import CONFIG_LIB, STAR_CONFIG_API_LIB_LOAD_ERROR_STR
from STAR_system.STAR_exceptions import StatusCode, STARAPIError
from STAR_system.port import Port
from STAR_system.STAR_structures import STAR_CFG_CONFIG_PORT_ERRORS
from STAR_system.STAR_structure_classes import ConfigPortErrors
from STAR_system.STAR_enums import STAR_CONFIG_OP_RESULT

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

StatusCodes = StatusCode()


class ConfigPort(Port):
    """Represents a configuration port on a device.
    
    Attributes:\n
        owningDeviceID (int): The ID of the device which owns the port.
        portNumber (int): The port number.
    """

    def __init__(self, owningDeviceID, portNumber):
        """Constructor:\n
            Initialises a `STAR_system.config_port.ConfigPort` object.

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

    def getConfigPortErrors(self) -> ConfigPortErrors:
        """Gets any errors present on the config port.
        Returns a `STAR_system.STAR_structure_classes.ConfigPortErrors` object.

        These are errors that arise when malformed or invalid configuration 
        commands are sent to the configuration port.

        Errors on the configuration port are latched until cleared with 
        `STAR_system.port.Port.clearPortErrors`.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get config port error info.\n
            TypeError:\n
                Errors from ConfigPortError class.
            ValueError:\n
                Errors from ConfigPortError class.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Get port status control
        portStatusControl = self.getPortStatusControl()

        # Create pointer to structure to be used in function call as argument
        pErrorsStruct = pointer(STAR_CFG_CONFIG_PORT_ERRORS())

        # Set argument types and return type of the C function
        config_lib.CFG_getConfigPortErrors.argtypes = [c_uint32, POINTER(STAR_CFG_CONFIG_PORT_ERRORS)]
        config_lib.CFG_getConfigPortErrors.restype = c_int32

        status = config_lib.CFG_getConfigPortErrors(c_uint32(portStatusControl), pErrorsStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        # Get the contents of the structure from the pointer
        errorsStruct = pErrorsStruct.contents

        try:
            configPortErrors = ConfigPortErrors(int.from_bytes(errorsStruct.errorCount, byteorder="big"),
                                                bool(int.from_bytes(errorsStruct.portTimeoutError, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.invalidHeaderCRC, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.invalidDataCRC, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.invalidDestinationKey, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.commandNotImplemented, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.invalidDataLength, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.invalidRMWDataLength, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.invalidDestinationLogicalAddress, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.earlyEOP, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.lateEOP, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.earlyEEP, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.lateEEP, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.verifyBufferOverrun, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.invalidRegisterAddress, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.unsupportedProtocol, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.sourceLogicalAddressError, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.sourcePathAddressError, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.cargoTooLarge, byteorder="big")),
                                                bool(int.from_bytes(errorsStruct.unusedRMAPCommandOrPacketType, byteorder="big")))
        except (TypeError, ValueError):
            raise

        return configPortErrors


