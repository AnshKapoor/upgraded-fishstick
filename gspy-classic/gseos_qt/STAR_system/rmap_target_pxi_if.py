"""RMAP Target (PXI Interface) functions.

Brief:\n
	RMAP Target (PXI Interface) functions.

Copyright:\n
	2022 STAR-Dundee Ltd
"""

# Load relevant C APIs
import os
import types
import numpy as np
from ctypes import *
from inspect import signature

from STAR_system import STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR, RMAP_TARGET_LIB
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_enums import RMAP_TARGET_STATUS, TARGET_AUTH_MODE, IF_MODE, REJECTION_REASON, NOTIF_TYPE,\
    STAR_OPERATION_RESULT
from STAR_system.STAR_structure_classes import RMAPCommandParameters
from STAR_system.STAR_structures import RMAP_COMMAND_PARAMETERS

systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    try:
        rmap_target_pxi_if_lib = windll.LoadLibrary(RMAP_TARGET_LIB)
    except Exception:
        rmap_target_pxi_if_lib = None
        print(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

elif systemType == "posix":
    try:
        rmap_target_pxi_if_lib = cdll.LoadLibrary(RMAP_TARGET_LIB)
    except Exception:
        rmap_target_pxi_if_lib = None
        print(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

class RMAPTargetPXIInterface(object):

    def __init__(self, deviceID):
        """Constructor:\n
            Initialises the `STAR_system.rmap_target_pxi_if.RMAPTargetPXIInterface`.

        Args:\n
            deviceID (int): The ID of the device.

        Raises:\n
            TypeError:\n
                deviceID was not int.
            ValueError:\n
                deviceID was negative.
        """
        if type(deviceID) != int:
            raise TypeError("deviceID must be int.")
        if deviceID < 0:
            raise ValueError("deviceID cannot be negative.")

        self.deviceID = deviceID

        # Keep a list with the callback functions (with context) for command complete notification (1 for each target)
        self._commandCompleteListenerFunctionWithContextCCallbacks = [None, None, None, None]
        
        # Keep a list with the callback functions (without context) for command complete notification (1 for each target)
        self._commandCompleteListenerFunctionWithoutContextCCallbacks = [None, None, None, None]
        
        # Keep a list with the callback functions (with context) for authorisation request notification (1 for each target)
        self._authorisationRequestListenerFunctionWithContextCCallbacks = [None, None, None, None]

        # Keep a list with the callback functions (without context) for authorisation request notification (1 for each target)
        self._authorisationRequestListenerFunctionWithoutContextCCallbacks = [None, None, None, None]

        # Keep a list with the memory addresses for the command complete notification contexts (1 for each target)
        self._commandCompleteNotificationContexts = [None, None, None, None]

        # Keep a list with the memory addresses for the authorisation request contexts (1 for each target)
        self._authorisationRequestNotificationContexts = [None, None, None, None]

    def getStatus(self, target) -> RMAP_TARGET_STATUS:
        """Gets the RMAP target status for a specific target.\n

        Args:\n
            target (int): The target to get status from.

        Raises:\n
            STARAPIError:\n
                Could not get target status.
                Returned target status value is invalid.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointer that will be used as an input parameter for the C library function call
        status = c_int32(0)
        pStatus = pointer(status)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getStatus.argtypes = [c_uint32, c_uint32, POINTER(c_int32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getStatus.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getStatus(c_uint32(self.deviceID), c_uint32(target), pStatus)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get the target status.")

        # Try to create enum from the returned value
        try:
            targetStatusEnum = RMAP_TARGET_STATUS(status.value)
        except ValueError:
            raise STARAPIError("Returned target status value was invalid.")

        return targetStatusEnum

    def setAddressOffset(self, target, offset):
        """Sets the address offset for a specific target.
           The address offset determines where the target's memory region begins.\n

        Args:\n
            target (int): The target to set address offset for.
            offset (int): Address offset in MBytes.

        Raises:\n
            STARAPIError:\n
                Could not set address offset.
            TypeError:\n
                target is not an int.\n
                offset is not an int.\n
            ValueError:\n
                target was negative.\n
                offset was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(offset) != int:
            raise TypeError("offset must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if offset < 0:
            raise ValueError("offset must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAddressOffset.argtypes = [c_uint32, c_uint32, c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAddressOffset.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAddressOffset(c_uint32(self.deviceID), c_uint32(target),
                                                                             c_uint32(offset))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set address offset.")

    def getAddressOffset(self, target) -> int:
        """Gets the address offset for a specific target.
           The address offset determines where the target's memory region begins.\n

        Args:\n
            target (int): The target to get address offset from.

        Raises:\n
            STARAPIError:\n
                Could not get address offset.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointer that will be used as an input parameter for the C library function call
        offset = c_uint32(0)
        pOffset = pointer(offset)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAddressOffset.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAddressOffset.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAddressOffset(c_uint32(self.deviceID), c_uint32(target),
                                                                             pOffset)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get address offset.")

        return int(offset.value)

    def setAuthControlMode(self, target, mode):
        """Sets the authorisation control mode for a specific target.
           Authorisation can be set to either `STAR_system.STAR_enums.TARGET_AUTH_MODE_MANUAL` or
           `STAR_system.STAR_enums.TARGET_AUTH_MODE_AUTOMATIC`.\n
           When set to `STAR_system.STAR_enums.TARGET_AUTH_MODE_MANUAL`, the authorisation of RMAP commands is done
           manually by the user application.\n
           When set to `STAR_system.STAR_enums.TARGET_AUTH_MODE_AUTOMATIC`, the authorisation of RMAP commands is
           done automatically using the expected parameter fields.\n

        Args:\n
            target (int): The target to set authorisation control mode for.
            mode (`STAR_system.STAR_enums.TARGET_AUTH_MODE`): The authorisation control mode.

        Raises:\n
            STARAPIError:\n
                Could not set authorisation control mode.
            TypeError:\n
                target is not an int.\n
                mode is not an STAR_system.STAR_enums.TARGET_AUTH_MODE.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if isinstance(mode, TARGET_AUTH_MODE) is False:
            raise TypeError("mode must be an TARGET_AUTH_MODE.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthControlMode.argtypes = [c_uint32, c_uint32, TARGET_AUTH_MODE]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthControlMode.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthControlMode(c_uint32(self.deviceID), c_uint32(target),
                                                                               mode)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set authorisation control mode.")

    def getAuthControlMode(self, target) -> TARGET_AUTH_MODE:
        """Gets the authorisation control mode for a specific target.
           Authorisation can be set to either `STAR_system.STAR_enums.TARGET_AUTH_MODE_MANUAL` or
           `STAR_system.STAR_enums.TARGET_AUTH_MODE_AUTOMATIC`.\n
           When set to `STAR_system.STAR_enums.TARGET_AUTH_MODE_MANUAL`, the authorisation of RMAP commands is done
           manually by the user application.\n
           When set to `STAR_system.STAR_enums.TARGET_AUTH_MODE_AUTOMATIC`, the authorisation of RMAP commands is
           done automatically using the expected parameter fields.\n

        Args:\n
            target (int): The target to get authorisation control mode from.

        Raises:\n
            STARAPIError:\n
                Could not get authorisation control mode.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointer that will be used as an input parameter for the C library function call
        authorisationControlMode = c_int32(0)
        pAuthorisationControlMode = pointer(authorisationControlMode)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthControlMode.argtypes = [c_uint32, c_uint32,
                                                                                 POINTER(c_int32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthControlMode.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthControlMode(c_uint32(self.deviceID), c_uint32(target),
                                                                               pAuthorisationControlMode)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get authorisation control mode.")

        # Try to create enum from returned value
        try:
            targetAuthModeEnum = TARGET_AUTH_MODE(authorisationControlMode.value)
        except ValueError:
            raise STARAPIError("Returned authorisation mode value was invalid.")

        return targetAuthModeEnum

    def setAuthLogicalAddressRange(self, target, lowest, highest):
        """Sets the authorised target logical address range for a specific target.\n

        Args:\n
            target (int): The target to set authorisation logical address range for.
            lowest (int): Lowest target logical address authorised.
            highest (int): Highest target logical address authorised.

        Raises:\n
            STARAPIError:\n
                Could not set authorisation address range.
            TypeError:\n
                target is not an int.\n
                lowest is not an int.\n
                highest is not an int.\n
            ValueError:\n
                target was negative.\n
                lowest was negative.\n
                highest was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(lowest) != int:
            raise TypeError("lowest must be an int.")
        if type(highest) != int:
            raise TypeError("highest must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if lowest < 0:
            raise ValueError("lowest must be non-negative.")
        if highest < 0:
            raise ValueError("highest must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthLogicalAddressRange.argtypes = [c_uint32, c_uint32, c_uint8,
                                                                                         c_uint8]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthLogicalAddressRange.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthLogicalAddressRange(c_uint32(self.deviceID),
                                                                                       c_uint32(target), c_uint8(lowest),
                                                                                       c_uint8(highest))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set authorisation address range.")

    def getAuthLogicalAddressRange(self, target) -> [int, int]:
        """Gets the authorised target logical address range from a specific target.\n
        
        The lowest logical address is the first element of the returned tuple,
        the highest logical address is the second element of the returned tuple.\n

        Args:\n
            target (int): The target to get authorisation logical address range from.

        Raises:\n
            STARAPIError:\n
                Could not get authorisation logical address range.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointers that will be used as an input parameter for the C library function call
        lowestAddress = c_uint32(0)
        pLowestAddress = pointer(lowestAddress)

        highestAddress = c_uint32(0)
        pHighestAddress = pointer(highestAddress)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthLogicalAddressRange.argtypes = [c_uint32, c_uint32,
                                                                                         POINTER(c_uint32), POINTER(c_uint32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthLogicalAddressRange.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthLogicalAddressRange(c_uint32(self.deviceID),
                                                                                       c_uint32(target),
                                                                                       pLowestAddress, pHighestAddress)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get authorisation logical address range.")

        return int(lowestAddress.value), int(highestAddress.value)

    def setAuthProtocolId(self, target, protocolId):
        """Sets the authorised protocol ID for a specific target.\n

        Args:\n
            target (int): The target to set address offset for.
            protocolId (int): Authorised protocol ID.

        Raises:\n
            STARAPIError:\n
                Could not set authorisation protocol ID.
            TypeError:\n
                target is not an int.\n
                protocolId is not an int.\n
            ValueError:\n
                target was negative.\n
                protocolId was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(protocolId) != int:
            raise TypeError("protocolId must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if protocolId < 0 or protocolId > 255:
            raise ValueError("protocolId must be non-negative and less than 255.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthProtocolId.argtypes = [c_uint32, c_uint32, c_uint8]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthProtocolId.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthProtocolId(c_uint32(self.deviceID), c_uint32(target),
                                                                              c_uint8(protocolId))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set authorisation protocol ID.")

    def getAuthProtocolId(self, target) -> int:
        """Gets the authorised protocol ID from a specific target.\n

        Args:\n
            target (int): The target to get authorisation protocol ID from.

        Raises:\n
            STARAPIError:\n
                Could not get authorisation protocol ID.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointer that will be used as an input parameter for the C library function call
        authProtocolId = c_uint8(0)
        pAuthProtocolId = pointer(authProtocolId)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthProtocolId.argtypes = [c_uint32, c_uint32, POINTER(c_uint8)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthProtocolId.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthProtocolId(c_uint32(self.deviceID), c_uint32(target),
                                                                              pAuthProtocolId)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get authorisation protocol ID.")

        return int(authProtocolId.value)

    def setAuthCommands(self, target, commands):
        """Sets the authorised RMAP commands for a specific target.\n

        Args:\n
            target (int): The target to set address offset for.
            commands (int): Authorised commands mask.

        Raises:\n
            STARAPIError:\n
                Could not set authorisation protocol ID.
            TypeError:\n
                target is not an int.\n
                commands is not an int.\n
            ValueError:\n
                target was negative.\n
                commands was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(commands) != int:
            raise TypeError("commands must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if commands < 0:
            raise ValueError("commands must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthCommands.argtypes = [c_uint32, c_uint32, c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthCommands.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthCommands(c_uint32(self.deviceID), c_uint32(target),
                                                                            c_uint32(commands))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set authorisation commands.")

    def getAuthCommands(self, target) -> int:
        """Gets the authorised RMAP commands from a specific target.\n

        Args:\n
            target (int): The target to get authorised RMAP commands from.

        Raises:\n
            STARAPIError:\n
                Could not get authorised RMAP commands.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointer that will be used as an input parameter for the C library function call
        commands = c_uint32(0)
        pCommands = pointer(commands)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthCommands.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthCommands.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthCommands(c_uint32(self.deviceID), c_uint32(target),
                                                                            pCommands)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get authorisation commands.")

        return int(commands.value)

    def setAuthKeyRange(self, target, lowest, highest):
        """Sets the authorised key range for a specific target.\n

        Args:\n
            target (int): The target to set authorisation key range for.
            lowest (int): Lowest key authorised.
            highest (int): Highest key authorised.

        Raises:\n
            STARAPIError:\n
                Could not set authorisation key range.
            TypeError:\n
                target is not an int.\n
                lowest is not an int.\n
                highest is not an int.\n
            ValueError:\n
                target was negative.\n
                lowest was negative.\n
                highest was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(lowest) != int:
            raise TypeError("lowest must be an int.")
        if type(highest) != int:
            raise TypeError("highest must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if lowest < 0:
            raise ValueError("lowest must be non-negative.")
        if highest < 0:
            raise ValueError("highest must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthKeyRange.argtypes = [c_uint32, c_uint32, c_uint8, c_uint8]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthKeyRange.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthKeyRange(c_uint32(self.deviceID), c_uint32(target),
                                                                            c_uint8(lowest), c_uint8(highest))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set authorisation key range.")

    def getAuthKeyRange(self, target) -> [int, int]:
        """Gets the authorised key range from a specific target.\n

        The lowest key is the first element of the returned tuple,
        the highest key is the second element of the returned tuple.\n

        Args:\n
            target (int): The target to get authorised key range from.

        Raises:\n
            STARAPIError:\n
                Could not get authorised key range.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointers that will be used as an input parameter for the C library function call
        lowestKey = c_uint8(0)
        pLowestKey = pointer(lowestKey)

        highestKey = c_uint8(0)
        pHighestKey = pointer(highestKey)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthKeyRange.argtypes = [c_uint32, c_uint32,
                                                                              POINTER(c_uint8), POINTER(c_uint8)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthKeyRange.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthKeyRange(c_uint32(self.deviceID), c_uint32(target),
                                                                            pLowestKey, pHighestKey)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get authorisation key range.")

        return int(lowestKey.value), int(highestKey.value)

    def setAuthMemoryAddressRange(self, target, lowestBoundary, highestBoundary):
        """Sets the authorised memory address range for a specific target.\n

        Args:\n
            target (int): The target to set authorised memory address range for.
            lowestBoundary (int): Lowest memory address authorised.
            highestBoundary (int): Highest memory address authorised.

        Raises:\n
            STARAPIError:\n
                Could not set authorised address range.
            TypeError:\n
                target is not an int.\n
                lowestBoundary is not an int.\n
                highestBoundary is not an int.\n
            ValueError:\n
                target was negative.\n
                lowestBoundary was negative.\n
                highestBoundary was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(lowestBoundary) != int:
            raise TypeError("lowestBoundary must be an int.")
        if type(highestBoundary) != int:
            raise TypeError("highestBoundary must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if lowestBoundary < 0:
            raise ValueError("lowestBoundary must be non-negative.")
        if highestBoundary < 0:
            raise ValueError("highestBoundary must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthMemoryAddressRange.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                                        c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthMemoryAddressRange.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setAuthMemoryAddressRange(c_uint32(self.deviceID),
                                                                                      c_uint32(target),
                                                                                      c_uint32(lowestBoundary),
                                                                                      c_uint32(highestBoundary))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set authorisation memory address range.")

    def getAuthMemoryAddressRange(self, target) -> [int, int]:
        """Gets the authorised memory address range from a specific target.\n

        The low memory region is the first element of the returned tuple,
        the high memory region is the second element of the returned tuple.\n

        Args:\n
            target (int): The target to get authorised memory address range from.

        Raises:\n
            STARAPIError:\n
                Could not get authorised memory address range.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointers that will be used as an input parameter for the C library function call
        lowerBoundary = c_uint32(0)
        pLowerBoundary = pointer(lowerBoundary)

        upperBoundary = c_uint32(0)
        pUpperBoundary = pointer(upperBoundary)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthMemoryAddressRange.argtypes = [c_uint32, c_uint32,
                                                                                        POINTER(c_uint32),
                                                                                        POINTER(c_uint32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthMemoryAddressRange.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getAuthMemoryAddressRange(c_uint32(self.deviceID),
                                                                                      c_uint32(target),
                                                                                      pLowerBoundary, pUpperBoundary)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get authorisation memory address range.")

        return int(lowerBoundary.value), int(upperBoundary.value)

    def setInterfaceMode(self, port, mode):
        """Sets the RMAP interface mode for a specific port.\n

        Args:\n
            port (int): Number of the port (6 - 9).
            mode (`STAR_system.STAR_enums.IF_MODE`): Interface mode of the port.

        Raises:\n
            STARAPIError:\n
                Could not set interface mode.
            TypeError:\n
                port is not an int.\n
                mode is not an STAR_system.STAR_enums.IF_MODE.\n
            ValueError:\n
                port was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(port) != int:
            raise TypeError("target must be an int.")
        if isinstance(mode, IF_MODE) is False:
            raise TypeError("mode must be an IF_MODE.")
        if port < 0:
            raise ValueError("port must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setInterfaceMode.argtypes = [c_uint32, c_uint32, IF_MODE]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setInterfaceMode.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setInterfaceMode(c_uint32(self.deviceID), c_uint32(port),
                                                                             mode)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set interface mode.")

    def getInterfaceMode(self, port) -> IF_MODE:
        """Gets the RMAP interface mode for a specific port.\n

        Args:\n
            port (int): Number of the port (6 - 9).

        Raises:\n
            STARAPIError:\n
                Could not get interface mode.
                Returned interface mode value is invalid.
            TypeError:\n
                port is not an int.\n
            ValueError:\n
                port was negative.
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(port) != int:
            raise TypeError("port must be an int.")
        if port < 0:
            raise ValueError("port must be non-negative.")

        # Create pointer that will be used as an input parameter for the C library function call
        interfaceMode = c_int32(0)
        pInterfaceMode = pointer(interfaceMode)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getInterfaceMode.argtypes = [c_uint32, c_uint32, POINTER(c_int32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getInterfaceMode.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getInterfaceMode(c_uint32(self.deviceID), c_uint32(port),
                                                                             pInterfaceMode)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get the interface mode.")

        # Try to create enum from the returned value
        try:
            interfaceModeEnum = IF_MODE(interfaceMode.value)
        except ValueError:
            raise STARAPIError("Returned interface mode value was invalid.")

        return interfaceModeEnum

    def isAuthRequired(self, target) -> bool:
        """Gets whether or not there is an RMAP command waiting to be authorised.\n

        Args:\n
            target (int): The target to check whether authorisation is required.

        Raises:\n
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_isAuthRequired.argtypes = [c_uint32, c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_isAuthRequired.restype = c_int32

        # Note that 0 will be returned if the function call fails
        authRequired = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_isAuthRequired(c_uint32(self.deviceID), c_uint32(target))

        return bool(int(authRequired))

    def getWaitingCommand(self, target) -> RMAPCommandParameters:
        """Gets the parameters of the RMAP command waiting to be authorised.\n

        Args:\n
            target (int): The target to get the waiting RMAP command parameters from.

        Raises:\n
            STARAPIError:\n
                Could not get parameters of the RMAP command waiting to be authorised.
                Could not create object instance using returned values.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointer that will be passed to the C API function call
        pCommand = pointer(RMAP_COMMAND_PARAMETERS())

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getWaitingCommand.argtypes = [c_uint32, c_uint32,
                                                                                POINTER(RMAP_COMMAND_PARAMETERS)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getWaitingCommand.restype = c_int32

        # Note that 0 will be returned if the function call fails
        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getWaitingCommand(c_uint32(self.deviceID), c_uint32(target),
                                                                              pCommand)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get the parameters of the RMAP command waiting to be authorised.")

        RMAPCommandParamsStruct = pCommand.contents

        # Try object instance from returned structure
        try:
            RMAPCommandParamsObject = RMAPCommandParameters(RMAPCommandParamsStruct.targetLogicalAddress,
                                                            RMAPCommandParamsStruct.command,
                                                            RMAPCommandParamsStruct.key,
                                                            RMAPCommandParamsStruct.protocolId,
                                                            RMAPCommandParamsStruct.extendedAddress,
                                                            RMAPCommandParamsStruct.dataLength,
                                                            RMAPCommandParamsStruct.address,
                                                            RMAPCommandParamsStruct.initiatorLogicalAddress,
                                                            RMAPCommandParamsStruct.transactionId)
        except (TypeError, ValueError):
            raise STARAPIError("Could not create object instance from returned values.")

        return RMAPCommandParamsObject

    def authoriseWaitingCommand(self, target):
        """Authorises a waiting RMAP command.\n

        Args:\n
            target (int): The target to authorise a waiting RMAP command for.

        Raises:\n
            STARAPIError:\n
                Could not authorise a waiting RMAP command.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_authoriseWaitingCommand.argtypes = [c_uint32, c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_authoriseWaitingCommand.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_authoriseWaitingCommand(c_uint32(self.deviceID),
                                                                                    c_uint32(target))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not authorise waiting command.")

    def rejectWaitingCommand(self, target, reason):
        """Rejects a waiting RMAP command.\n

        Args:\n
            target (int): The target to reject a waiting RMAP command for.
            reason (`STAR_system.STAR_enums.REJECTION_REASON`): Reason for rejecting the waiting RMAP command.

        Raises:\n
            STARAPIError:\n
                Could not reject waiting command.
            TypeError:\n
                target is not an int.\n
                reason is not a REJECTION_REASON.\n
            ValueError:\n
                target was negative.
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if isinstance(reason, REJECTION_REASON) is False:
            raise TypeError("reason must be an REJECTION_REASON.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_rejectWaitingCommand.argtypes = [c_uint32, c_uint32, REJECTION_REASON]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_rejectWaitingCommand.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_rejectWaitingCommand(c_uint32(self.deviceID),
                                                                                 c_uint32(target), reason)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not reject waiting command.")

    def setEnabledNotifications(self, target, notifications):
        """Set the notifications that are enabled for a target.\n

        Args:\n
            target (int): The target to set enabled notifications for.
            notifications (int): Enabled notifications mask.

        Raises:\n
            STARAPIError:\n
                Could not set the notifications that are enabled for the target.
            TypeError:\n
                target is not an int.\n
                notifications is not an int.\n
            ValueError:\n
                target was negative.\n
                notifications was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(notifications) != int:
            raise TypeError("notifications must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if notifications < 0:
            raise ValueError("notifications must be non-negative.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setEnabledNotifications.argtypes = [c_uint32, c_uint32, c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setEnabledNotifications.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_setEnabledNotifications(c_uint32(self.deviceID),
                                                                                    c_uint32(target),
                                                                                    c_uint32(notifications))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not set the notifications that are enabled for the target.")

    def getEnabledNotifications(self, target) -> int:
        """Gets the notifications that are enabled for a target.\n

        Args:\n
            target (int): The target to get enabled notifications from.

        Raises:\n
            STARAPIError:\n
                Could not get enabled notifications from.
            TypeError:\n
                target is not an int.\n
            ValueError:\n
                target was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")

        # Create pointer that will be used as an input parameter for the C library function call
        notifications = c_uint32(0)
        pNotifications = pointer(notifications)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getEnabledNotifications.argtypes = [c_uint32, c_uint32,
                                                                                      POINTER(c_uint32)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getEnabledNotifications.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_getEnabledNotifications(c_uint32(self.deviceID),
                                                                                    c_uint32(target), pNotifications)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not get enabled notifications.")

        return int(notifications.value)

    def registerNotificationListener(self, target, notificationType, listenerFunction):
        """Register a notification listener function.\n

        Args:\n
            target (int): The target to register a notification listener function for.
            notificationType (`STAR_system.STAR_enums.NOTIF_TYPE`): Type of notification to register the listener function for.
            listenerFunction (function): The notification listener function.

        Raises:\n
            STARAPIError:\n
                Could not register the notification listener function.
            TypeError:\n
                target is not an int.\n
                notificationType is not a NOTIF_TYPE.\n
                listenerFunction is not a function.\n
            ValueError:\n
                target was negative or greater than 3.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if isinstance(notificationType, NOTIF_TYPE) is False:
            raise TypeError("notificationType must be an NOTIF_TYPE.")
        if isinstance(listenerFunction, types.FunctionType) is False and isinstance(listenerFunction, types.MethodType) is False:
            raise TypeError("listenerFunction must be a function.")
        if target < 0 or target > 3:
            raise ValueError("target must be non-negative and be less than 4.")

        # Get CFUNCTYPE function (without context)
        try:
            cTypeCallbackFunction = self.getCtypesCallbackWithoutContextFunction(listenerFunction)
            
            # Save the callback function to the correct list of notification functions
            if notificationType is NOTIF_TYPE.NOTIF_TYPE_AUTH_REQUEST:
                self._authorisationRequestListenerFunctionWithoutContextCCallbacks[target] = cTypeCallbackFunction
            elif notificationType is NOTIF_TYPE.NOTIF_TYPE_CMD_COMPLETE:
                self._commandCompleteListenerFunctionWithoutContextCCallbacks[target] = cTypeCallbackFunction
            else:
                raise STARAPIError("Incorrect notification type provided.")
        except ValueError:
            raise

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_registerNotificationListener.argtypes = [c_uint32, c_uint32,
                                                                                           NOTIF_TYPE,
                                                                                           type(cTypeCallbackFunction)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_registerNotificationListener.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_registerNotificationListener(c_uint32(self.deviceID),
                                                                                         c_uint32(target),
                                                                                         notificationType,
                                                                                         cTypeCallbackFunction)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not register notification listener function.")

    def registerNotificationListenerWithContext(self, target, notificationType, listenerFunction, context):
        """Register a notification listener function.\n

        Args:\n
            target (int): The target to register a notification listener function for.
            notificationType (`STAR_system.STAR_enums.NOTIF_TYPE`): Type of notification to register the listener function for.
            listenerFunction (function): The notification listener function.

        Raises:\n
            STARAPIError:\n
                Could not register the notification listener function.
            TypeError:\n
                target is not an int.\n
                notificationType is not a NOTIF_TYPE.\n
                listenerFunction is not a function.\n
            ValueError:\n
                target was negative or greater than 3.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if isinstance(notificationType, NOTIF_TYPE) is False:
            raise TypeError("notificationType must be an NOTIF_TYPE.")
        if isinstance(listenerFunction, types.FunctionType) is False and isinstance(listenerFunction, types.MethodType) is False:
            raise TypeError("listenerFunction must be a function.")
        if target < 0 or target > 3:
            raise ValueError("target must be non-negative and less than 4.")

        cContext = c_int32(context)
        pCContext = pointer(cContext)
        pVoidCContext = cast(pCContext, c_void_p)

        # Get CFUNCTYPE function (with context)
        try:
            cTypeCallbackFunction = self.getCtypesCallbackWithContextFunction(listenerFunction)
            
            # Save the callback function to the correct list of notification functions
            if notificationType is NOTIF_TYPE.NOTIF_TYPE_AUTH_REQUEST:
                self._authorisationRequestListenerFunctionWithContextCCallbacks[target] = cTypeCallbackFunction
                self._authorisationRequestNotificationContexts[target] = pVoidCContext
            elif notificationType is NOTIF_TYPE.NOTIF_TYPE_CMD_COMPLETE:
                self._commandCompleteListenerFunctionWithContextCCallbacks[target] = cTypeCallbackFunction
                self._commandCompleteNotificationContexts[target] = pVoidCContext
            else:
                raise STARAPIError("Incorrect notification type provided.")
            
        except ValueError:
            raise

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_registerNotificationListenerWithContext.argtypes =\
            [c_uint32, c_uint32, NOTIF_TYPE, type(cTypeCallbackFunction), c_void_p]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_registerNotificationListenerWithContext.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_registerNotificationListenerWithContext(
            c_uint32(self.deviceID), c_uint32(target), notificationType, cTypeCallbackFunction,
            pVoidCContext)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not register notification listener function.")

    def unregisterNotificationListener(self, target, notificationType):
        """Unregister a notification listener function.\n

        Args:\n
            target (int): The target to unregister a notification listener function for.
            notificationType (`STAR_system.STAR_enums.NOTIF_TYPE`): Type of notification to unregister the listener function for.

        Raises:\n
            STARAPIError:\n
                Could not unregister the notification listener function.
            TypeError:\n
                target is not an int.\n
                notificationType is not a NOTIF_TYPE.\n
            ValueError:\n
                target was negative or greater than 3.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if isinstance(notificationType, NOTIF_TYPE) is False:
            raise TypeError("notificationType must be an NOTIF_TYPE.")
        if target < 0 or target > 3:
            raise ValueError("target must be non-negative and less than 4.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_unregisterNotificationListener.argtypes = [c_uint32, c_uint32,
                                                                                             NOTIF_TYPE]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_unregisterNotificationListener.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_unregisterNotificationListener(c_uint32(self.deviceID),
                                                                                           c_uint32(target),
                                                                                           notificationType)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not unregister notification listener function.")

        # Set the entry in the list of callback functions to None
        if notificationType is NOTIF_TYPE.NOTIF_TYPE_AUTH_REQUEST:
            self._authorisationRequestListenerFunctionWithoutContextCCallbacks[target] = None
        elif notificationType is NOTIF_TYPE.NOTIF_TYPE_CMD_COMPLETE:
            self._commandCompleteListenerFunctionWithoutContextCCallbacks[target] = None
        elif notificationType is NOTIF_TYPE.NOTIF_TYPE_ALL:
            self._authorisationRequestListenerFunctionWithoutContextCCallbacks[target] = None
            self._commandCompleteListenerFunctionWithoutContextCCallbacks[target] = None
        else:
            raise STARAPIError("Incorrect notification type provided.")

    def unregisterNotificationListenerWithContext(self, target, notificationType):
        """Unregister a notification listener function.\n

        Args:\n
            target (int): The target to unregister a notification listener function for.
            notificationType (`STAR_system.STAR_enums.NOTIF_TYPE`): Type of notification to unregister the listener function for.

        Raises:\n
            STARAPIError:\n
                Could not unregister the notification listener function (with context).
            TypeError:\n
                target is not an int.\n
                notificationType is not a NOTIF_TYPE.\n
            ValueError:\n
                target was negative or greater than 3.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if isinstance(notificationType, NOTIF_TYPE) is False:
            raise TypeError("notificationType must be an NOTIF_TYPE.")
        if target < 0 or target > 3:
            raise ValueError("target must be non-negative and less than 4.")

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_unregisterNotificationListenerWithContext.argtypes = [c_uint32,
                                                                                                        c_uint32,
                                                                                                        NOTIF_TYPE]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_unregisterNotificationListenerWithContext.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_unregisterNotificationListenerWithContext(
            c_uint32(self.deviceID), c_uint32(target), notificationType)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not unregister notification listener function (with context).")

        # Set the entry in the list of callback functions to None
        if notificationType is NOTIF_TYPE.NOTIF_TYPE_AUTH_REQUEST:
            self._authorisationRequestListenerFunctionWithContextCCallbacks[target] = None
            self._authorisationRequestNotificationContexts[target] = None
        elif notificationType is NOTIF_TYPE.NOTIF_TYPE_CMD_COMPLETE:
            self._commandCompleteListenerFunctionWithContextCCallbacks[target] = None
            self._commandCompleteNotificationContexts[target] = None
        elif notificationType is NOTIF_TYPE.NOTIF_TYPE_ALL:
            self._authorisationRequestListenerFunctionWithContextCCallbacks[target] = None
            self._commandCompleteListenerFunctionWithContextCCallbacks[target] = None
            self._authorisationRequestNotificationContexts[target] = None
            self._commandCompleteNotificationContexts[target] = None
        else:
            raise STARAPIError("Incorrect notification type provided.")

    def startReceivingNotifications(self):
        """Start receiving notifications for the device.\n

        Raises:\n
            STARAPIError:\n
                Could not start receiving notifications.
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_startReceivingNotifications.argtypes = [c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_startReceivingNotifications.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_startReceivingNotifications(c_uint32(self.deviceID))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not start receiving notifications.")

    def stopReceivingNotifications(self):
        """Stop receiving notifications for the device.\n

        Raises:\n
            STARAPIError:\n
                Could not stop receiving notifications.
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_stopReceivingNotifications.argtypes = [c_uint32]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_stopReceivingNotifications.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_stopReceivingNotifications(c_uint32(self.deviceID))

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not stop receiving notifications.")

    def readMemory(self, target, address, length) -> list:
        """Reads an area of RMAP target memory.\n

        Args:\n
            target (int): The target to read memory from.
            address (int): The address in the target to read from.
            length (int): The length to read.

        Raises:\n
            STARAPIError:\n
                Could not read memory.
            TypeError:\n
                target is not an int.\n
                address is not an int.\n
                length is not an int.\n
            ValueError:\n
                target was negative.\n
                address was negative.\n
                length was negative.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(address) != int:
            raise TypeError("address must be an int.")
        if type(length) != int:
            raise TypeError("length must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if address < 0:
            raise ValueError("address must be non-negative.")
        if length < 0:
            raise ValueError("length must be non-negative.")

        # Set up an array holding the memory bytes
        cBuffer = (c_uint8 * length)()
        cBufferPointer = pointer(cBuffer)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_readMemory.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32,
                                                                         POINTER(c_uint8 * length)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_readMemory.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_readMemory(c_uint32(self.deviceID), c_uint32(target),
                                                                       c_uint32(address), c_uint32(length),
                                                                       cBufferPointer)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not read memory.")

        # Convert the C type array to list
        memoryBytesList = np.frombuffer(cBuffer, dtype=np.uint8, count=length).tolist()

        return memoryBytesList

    def writeMemory(self, target, address, data):
        """Writes an area of RMAP target memory from a user-supplied list of bytes.\n

        Args:\n
            target (int): The target to write memory to.
            address (int): The address in the target to write to.
            data (list): The data to write.

        Raises:\n
            STARAPIError:\n
                Could not write to memory.
            TypeError:\n
                target is not an int.\n
                address is not an int.\n
                data is not a list.\n
            ValueError:\n
                target was negative.\n
                address was negative.\n
                any element in data is not an int.\n
        """

        # Make sure to protect against invalid RMAP Target PXI Interface library
        if rmap_target_pxi_if_lib is None:
            raise STARAPIError(STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR)

        if type(target) != int:
            raise TypeError("target must be an int.")
        if type(address) != int:
            raise TypeError("address must be an int.")
        if type(data) != list:
            raise TypeError("data must be a list.")
        for elem in data:
            if type(elem) != int:
                raise TypeError("every element in data must be an int.")
        if target < 0:
            raise ValueError("target must be non-negative.")
        if address < 0:
            raise ValueError("address must be non-negative.")

        # Get length of data
        dataLength = len(data)

        # Create a C type array holding the data bytes
        cBuffer = (c_uint8 * dataLength)()

        for i in range(dataLength):
            cBuffer[i] = data[i]

        # Create pointer to the C type array
        cBufferPointer = pointer(cBuffer)

        # Set argument types and return type of the C function
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_writeMemory.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32,
                                                                         POINTER(c_uint8 * dataLength)]
        rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_writeMemory.restype = c_int32

        success = rmap_target_pxi_if_lib.RMAP_TARGET_PXI_IF_writeMemory(c_uint32(self.deviceID), c_uint32(target),
                                                                       c_uint32(address), c_uint32(dataLength),
                                                                       cBufferPointer)

        # Check the status
        if success == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Could not write to memory.")

    @staticmethod
    def getCtypesCallbackWithoutContextFunction(function) -> CFUNCTYPE:
        """Creates a CFUNCTYPE object using the provided function.

        Raises:\n
            ValueError:\n
                Function must have 2 arguments.\n
        """

        sig = signature(function)

        # Number of arguments
        argCount = str(sig).count(",")

        if argCount == 1:
            return CFUNCTYPE(None, c_uint32, c_void_p)(function)
        else:
            raise ValueError("Call-back function must have 2 arguments.")

    @staticmethod
    def getCtypesCallbackWithContextFunction(function) -> CFUNCTYPE:
        """Creates a CFUNCTYPE object using the provided function.

        Raises:\n
            ValueError:\n
                Function must have 4 arguments.\n
        """

        sig = signature(function)

        # Number of arguments
        argCount = str(sig).count(",")

        if argCount == 3:
            return CFUNCTYPE(None, c_uint32, c_uint32, c_void_p, c_void_p)(function)
        else:
            raise ValueError("Call-back function must have 4 arguments.")

