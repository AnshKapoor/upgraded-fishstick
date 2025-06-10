"""Functions used to configure the triggers and subsystems.

Brief:\n
    Functions used to configure the triggers and subsystems.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

# Load C API
import os
from ctypes import *
from typing import Tuple

from gspy_egse.gui.STAR_system import GENERIC_TRIGGERING_LIB, STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.STAR_enums import STAR_OPERATION_RESULT
from gspy_egse.gui.STAR_system.STAR_structures import STAR_TRIGGER_MATRIX
from gspy_egse.gui.STAR_system.triggering_types import TRIGGER_TYPE, TRIGGER_INPUT_MODE

systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    try:
        generic_triggering_lib = windll.LoadLibrary(GENERIC_TRIGGERING_LIB)
    except Exception:
        generic_triggering_lib = None
        print(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

elif systemType == "posix":
    try:
        generic_triggering_lib = cdll.LoadLibrary(GENERIC_TRIGGERING_LIB)
    except Exception:
        generic_triggering_lib = None
        print(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)


class TriggeringConfiguration(object):

    @staticmethod
    def disableCounterAutoReload(deviceId, timer) -> bool:
        """Disables auto reload for a specific counter.
           When disabled, the counter will not automatically reload with its reload value when
           the counter reaches zero.

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to disable auto reload for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableCounterAutoReload.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableCounterAutoReload.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableCounterAutoReload(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def enableCounterAutoReload(deviceId, timer) -> bool:
        """Enables auto reload for a specific counter.
           When enabled, the counter will automatically reload with its reload value when the
           counter reaches zero.\n

            Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to enable auto reload for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableCounterAutoReload.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableCounterAutoReload.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableCounterAutoReload(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterAutoReloadEnabled(deviceId, timer) -> Tuple[bool, bool]:
        """Gets whether auto reload is enabled for a specific counter.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if auto reload is enabled
        for given counter, False if auto reload is disabled for given counter.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to get auto reload enabled for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Create pointer to unsigned int, this is common in all device function calls
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterAutoReloadEnabled.argtypes = [c_uint32, c_uint32,
                                                                                   POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterAutoReloadEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterAutoReloadEnabled(
            c_uint32(deviceId), c_uint32(timer), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def disableCounterLoadZero(deviceId, timer) -> bool:
        """Disables load zero for a specific counter.
           When disabled, reload triggered events occur even when the counter is not zero.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to disable load zero for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableCounterLoadZero.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableCounterLoadZero.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableCounterLoadZero(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def enableCounterLoadZero(deviceId, timer) -> bool:
        """Enables load zero for a specific counter.
           When enabled, reload triggered events only occur when the counter is zero.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to enable load zero for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableCounterLoadZero.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableCounterLoadZero.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableCounterLoadZero(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterLoadZeroEnabled(deviceId, timer) -> Tuple[bool, bool]:
        """Gets whether load zero is enabled for a specific counter.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if load zero is enabled
        for given counter, False if load zero is disabled for given counter.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to get load zero enabled for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n

            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterLoadZeroEnabled.argtypes = [c_uint32, c_uint32,
                                                                                 POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterLoadZeroEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterLoadZeroEnabled(
            c_uint32(deviceId), c_uint32(timer), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def disableCounterStartMode(deviceId, timer) -> bool:
        """Disables start mode for a specific counter.\n
           When disabled, the counter will not wait for a start action to occur before any counting or
           reloading can take place.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to disable start mode for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableCounterStartMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableCounterStartMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableCounterStartMode(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def enableCounterStartMode(deviceId, timer) -> bool:
        """Enables start mode for a specific counter.
           When enabled, the counter will wait for a start action to occur before any counting or
           reloading can take place. When the counter reaches zero, the counter may be reloaded but
           no counting or reloading can take place until the next start action occurs.\n

        Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to enable start mode for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableCounterStartMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableCounterStartMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableCounterStartMode(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterStartModeEnabled(deviceId, timer) -> Tuple[bool, bool]:
        """Gets whether start mode is enabled for a specific counter.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if start mode is enabled
        for given counter, False if start mode is disabled for given counter.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to get counter start mode for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterStartModeEnabled.argtypes = [c_uint32, c_uint32,
                                                                                  POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterStartModeEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterStartModeEnabled(
            c_uint32(deviceId), c_uint32(timer), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def disableCounterStartStopMode(deviceId, timer) -> bool:
        """Disables start stop mode for a specific counter.\n
           When disabled, the counter will not wait for a start action to occur before any counting or
           reloading can take place.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to disable start stop mode for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableCounterStartStopMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableCounterStartStopMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableCounterStartStopMode(c_uint32(deviceId),
                                                                                 c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def enableCounterStartStopMode(deviceId, timer) -> bool:
        """Enables start stop mode for a specific counter.
           When enabled, the counter will wait for a start action to occur before any counting or
           reloading can take place. The counter will continue to count and reload until a stop action
           occurs.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to enable start stop mode for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableCounterStartStopMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableCounterStartStopMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableCounterStartStopMode(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterStartStopModeEnabled(deviceId, timer) -> Tuple[bool, bool]:
        """Gets whether start stop mode is enabled for a specific counter.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if start stop mode is
        enabled for given counter, False if start stop mode is disabled for given counter.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to get counter start stop mode for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterStartStopModeEnabled.argtypes = [c_uint32, c_uint32,
                                                                                      POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterStartStopModeEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterStartStopModeEnabled(
            c_uint32(deviceId), c_uint32(timer), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def disableCounterTriggerCount(deviceId, timer) -> bool:
        """Disables trigger count for a specific counter.\n
           When disabled, the counter will be decremented every clock cycle.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to disable trigger count for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableCounterTriggerCount.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableCounterTriggerCount.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableCounterTriggerCount(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def enableCounterTriggerCount(deviceId, timer) -> bool:
        """Enables trigger count for a specific counter.
           When enabled, the counter will only be decremented when a count action occurs.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to enable trigger count for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableCounterTriggerCount.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableCounterTriggerCount.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableCounterTriggerCount(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterTriggerCountEnabled(deviceId, timer) -> Tuple[bool, bool]:
        """Gets whether trigger count is enabled for a specific counter.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if trigger count is
        enabled for given counter, False if trigger count is disabled for given counter.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to get trigger count enabled for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterTriggerCountEnabled.argtypes = [c_uint32, c_uint32,
                                                                                     POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterTriggerCountEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterTriggerCountEnabled(
            c_uint32(deviceId), c_uint32(timer), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def forceCounterReload(deviceId, timer) -> bool:
        """Force the reload of a specific counter.\n

        Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to force reload on/of.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_forceCounterReload.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_forceCounterReload.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_forceCounterReload(c_uint32(deviceId), c_uint32(timer))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def disableExtTriggerEdgeDetectMode(deviceId, extTrigger) -> bool:
        """Disables edge detect mode for a specific external trigger.\n
           When disabled, the trigger will always be set when the input trigger is high.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableExtTriggerEdgeDetectMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableExtTriggerEdgeDetectMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableExtTriggerEdgeDetectMode(
            c_uint32(deviceId), c_uint32(extTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def enableExtTriggerEdgeDetectMode(deviceId, extTrigger) -> bool:
        """Enables edge detect mode for a specific external trigger.\n
           When enabled, the trigger will be set on the rising edge of the input trigger signal.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableExtTriggerEdgeDetectMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableExtTriggerEdgeDetectMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableExtTriggerEdgeDetectMode(
            c_uint32(deviceId), c_uint32(extTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getExtTriggerEdgeDetectModeEnabled(deviceId, extTrigger) -> Tuple[bool, bool]:
        """Gets whether edge detect mode is enabled/disabled for a specific external trigger.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if external trigger edge
        detect mode is enabled for given external trigger, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to get trigger edge
                              detect mode enabled for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerEdgeDetectModeEnabled.argtypes = [c_uint32, c_uint32,
                                                                                          POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerEdgeDetectModeEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getExtTriggerEdgeDetectModeEnabled(
            c_uint32(deviceId), c_uint32(extTrigger), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def enableExtTriggerInvert(deviceId, extTrigger) -> bool:
        """Enables invert for a specific external trigger.\n
           When enabled, the input trigger signal is inverted before the detection mechanism.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to enable invert mode for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableExtTriggerInvert.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableExtTriggerInvert.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableExtTriggerInvert(c_uint32(deviceId),
                                                                            c_uint32(extTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def disableExtTriggerInvert(deviceId, extTrigger) -> bool:
        """Disables invert for a specific external trigger.\n
           When disabled, the input trigger signal is not modified before the detection mechanism.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to disable invert for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableExtTriggerInvert.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableExtTriggerInvert.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableExtTriggerInvert(c_uint32(deviceId),
                                                                             c_uint32(extTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getExtTriggerInvertEnabled(deviceId, extTrigger) -> Tuple[bool, bool]:
        """Gets whether invert is enabled for a specific external trigger.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if external trigger invert
        is enabled for given external trigger, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to get trigger invert enabled for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerInvertEnabled.argtypes = [c_uint32, c_uint32,
                                                                                  POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerInvertEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getExtTriggerInvertEnabled(
            c_uint32(deviceId), c_uint32(extTrigger), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def enableExtTriggerOutput(deviceId, extTrigger) -> bool:
        """Enables output for a specific external trigger.\n

           When enabled, the external trigger's output action causes the trigger output signal to be pulsed
           for a duration specified by the extend duration value.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to enable trigger output for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableExtTriggerOutput.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableExtTriggerOutput.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableExtTriggerOutput(c_uint32(deviceId),
                                                                            c_uint32(extTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def disableExtTriggerOutput(deviceId, extTrigger) -> bool:
        """Disables output for a specific external trigger.\n
           When disabled, the external trigger's output action does not cause the trigger output signal to be pulsed.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to disable trigger output for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableExtTriggerOutput.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableExtTriggerOutput.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableExtTriggerOutput(c_uint32(deviceId),
                                                                             c_uint32(extTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getExtTriggerOutputEnabled(deviceId, extTrigger) -> Tuple[bool, bool]:
        """Gets whether output is enabled for a specific external trigger.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if external trigger output
        is enabled for given external trigger, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to get trigger output enabled for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Create pointer to unsigned int.
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerOutputEnabled.argtypes = [c_uint32, c_uint32,
                                                                                  POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerOutputEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getExtTriggerOutputEnabled(
            c_uint32(deviceId), c_uint32(extTrigger), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def getExtTriggerExtend(deviceId, extTrigger) -> Tuple[bool, int]:
        """Gets the extend duration for a specific external trigger.\n
           The extend duration is the duration, in cycles, of the trigger output signal pulse when a
           trigger output action occurs.\n

           Returns a tuple: True if the function completes correctly, False otherwise and the value of the
           external trigger extend duration.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        # Create pointer to unsigned int
        extendValue = c_uint32(0)
        pExtendValue = pointer(extendValue)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerExtend.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerExtend.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getExtTriggerExtend(
            c_uint32(deviceId), c_uint32(extTrigger), pExtendValue)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(extendValue.value)

    @staticmethod
    def getExtTriggerInputEvents(deviceId, extTrigger, internalTrigger) -> Tuple[bool, int]:
        """ Gets the input events from an external trigger which will cause an internal trigger to be set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the
        external trigger input events.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to get input events from.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the external trigger input events
        inputEventsMask = c_uint32(0)
        pInputEventsMask = pointer(inputEventsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerInputEvents.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                                POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getExtTriggerInputEvents(
            c_uint32(deviceId), c_uint32(extTrigger), c_uint32(internalTrigger), pInputEventsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(inputEventsMask.value)

    @staticmethod
    def getExtTriggerOutputActions(deviceId, extTrigger, internalTrigger) -> Tuple[bool, int]:
        """ Gets the output actions from an external trigger that are caused by an internal trigger being set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the external trigger
        output actions.

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to get input events from.
            internalTrigger (int): Number of the internal trigger that triggers the output actions.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the output actions
        # for the specified ext. trigger
        outputActionsMask = c_uint32(0)
        pOutputActionsMask = pointer(outputActionsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerOutputActions.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                                  POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getExtTriggerOutputActions.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getExtTriggerOutputActions(
            c_uint32(deviceId), c_uint32(extTrigger), c_uint32(internalTrigger), pOutputActionsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(outputActionsMask.value)

    @staticmethod
    def enablePortTransmitPacketMode(deviceId, port) -> bool:
        """Enables packet transmit mode for a specific port.\n
           When enabled, packets are only transmitted when a transmit packet action occurs.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enablePortTransmitPacketMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enablePortTransmitPacketMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enablePortTransmitPacketMode(c_uint32(deviceId),
                                                                                  c_uint32(port))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def disablePortTransmitPacketMode(deviceId, port) -> bool:
        """Disables packet transmit mode for a specific port.\n
           When disabled, packets do not wait for a transmit packet action to occur before transmission.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disablePortTransmitPacketMode.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disablePortTransmitPacketMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disablePortTransmitPacketMode(c_uint32(deviceId),
                                                                                   c_uint32(port))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getPortTransmitPacketModeEnabled(deviceId, port) -> Tuple[bool, bool]:
        """Gets whether packet transmit mode is enabled for a specific port.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if transmit packet mode
        is enabled for given port, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port to get transmit packet mode enabled/disabled for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getPortTransmitPacketModeEnabled.argtypes = [c_uint32, c_uint32,
                                                                                        POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getPortTransmitPacketModeEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getPortTransmitPacketModeEnabled(
            c_uint32(deviceId), c_uint32(port), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def getPortInputEvents(deviceId, port, internalTrigger) -> Tuple[bool, int]:
        """ Gets the input events from a port which will cause an internal trigger to be set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the
        port input events.

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port to get input events from/for.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the port input events
        inputEventsMask = c_uint32(0)
        pInputEventsMask = pointer(inputEventsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getPortInputEvents.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                          POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getPortInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getPortInputEvents(
            c_uint32(deviceId), c_uint32(port), c_uint32(internalTrigger), pInputEventsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(inputEventsMask.value)

    @staticmethod
    def getPortOutputActions(deviceId, port, internalTrigger) -> Tuple[bool, int]:
        """ Gets the output actions from a port that are caused by an internal trigger being set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the port
        output actions.

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port to get input events from/for.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the port output actions
        outputActionsMask = c_uint32(0)
        pOutputActionsMask = pointer(outputActionsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getPortOutputActions.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                            POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getPortOutputActions.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getPortOutputActions(
            c_uint32(deviceId), c_uint32(port), c_uint32(internalTrigger), pOutputActionsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(outputActionsMask.value)

    @staticmethod
    def enableTrigger(deviceId, internalTrigger) -> bool:
        """Enables a specific internal trigger.\n
           When enabled, the trigger can be set by its input events and cause output actions to occur.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger to enable.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enableTrigger.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enableTrigger.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enableTrigger(c_uint32(deviceId), c_uint32(internalTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def disableTrigger(deviceId, internalTrigger) -> bool:
        """Disables a specific internal trigger.\n
           When disabled, the trigger is not set by its input events and does not cause output actions to occur.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger to disable.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disableTrigger.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disableTrigger.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disableTrigger(c_uint32(deviceId), c_uint32(internalTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def forceTrigger(deviceId, internalTrigger) -> bool:
        """Force the triggering of a specific internal trigger.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger to force the triggering of.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_forceTrigger.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_forceTrigger.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_forceTrigger(c_uint32(deviceId), c_uint32(internalTrigger))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getTriggerEnabled(deviceId, internalTrigger) -> Tuple[bool, bool]:
        """Gets whether a trigger is enabled.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if given internal trigger
        is enabled, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTriggerEnabled.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getTriggerEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getTriggerEnabled(
            c_uint32(deviceId), c_uint32(internalTrigger), pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def getTriggerInputEvents(deviceId, causeTrigger, internalTrigger) -> Tuple[bool, int]:
        """ Gets the input events for an internal trigger which will cause another internal trigger to be set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the
        given internal trigger input events.\n

        Args:\n
            deviceId (int): The ID of the device.
            causeTrigger (int): Internal trigger to get input events from.
            internalTrigger (int): Internal trigger which is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                causeTrigger was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(causeTrigger) != int:
            raise TypeError("causeTrigger must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the trigger input events mask
        triggerInputEventsMask = c_uint32(0)
        pTriggerInputEventsMask = pointer(triggerInputEventsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTriggerInputEvents.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                             POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getTriggerInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getTriggerInputEvents(
            c_uint32(deviceId), c_uint32(causeTrigger), c_uint32(internalTrigger), pTriggerInputEventsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(triggerInputEventsMask.value)

    @staticmethod
    def setTriggerInputEvents(deviceId, causeTrigger, internalTrigger, eventsMask) -> bool:
        """Sets the input events for an internal trigger which will cause another internal trigger to be set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            causeTrigger (int): Internal trigger to set input events for.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            eventsMask (int): Mask describing the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                causeTrigger was not an int.\n
                internalTrigger was not an int.\n
                eventsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(causeTrigger) != int:
            raise TypeError("causeTrigger must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(eventsMask) != int:
            raise TypeError("eventsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setTriggerInputEvents.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setTriggerInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setTriggerInputEvents(
            c_uint32(deviceId), c_uint32(causeTrigger), c_uint32(internalTrigger), c_uint32(eventsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getTriggerInputMode(deviceId, internalTrigger) -> Tuple[bool, TRIGGER_INPUT_MODE]:
        """Gets the input mode for a specific internal trigger.\n

           Returns a tuple: True if the function completes correctly, False otherwise and the trigger input mode
           for the given internal trigger.\n

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to int representing the TRIGGER_INPUT_MODE enum value
        triggerInputModeVal = c_int32(0)
        pTriggerInputModeVal = pointer(triggerInputModeVal)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTriggerInputMode.argtypes = [c_uint32, c_uint32, POINTER(c_int32)]
        generic_triggering_lib.TRIGGER_CFG_getTriggerInputMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getTriggerInputMode(
            c_uint32(deviceId), c_uint32(internalTrigger), pTriggerInputModeVal)

        # Create TRIGGER_INPUT_MODE enum from returned value
        try:
            triggerInputMode = TRIGGER_INPUT_MODE(triggerInputModeVal.value)
        except ValueError:
            raise STARAPIError("The returned trigger input mode value was invalid.")

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, triggerInputMode

    @staticmethod
    def setTriggerInputMode(deviceId, internalTrigger, mode) -> bool:
        """Sets the input mode for a specific internal trigger.\n
           If set to `STAR_system.triggering_types.TRIGGER_INPUT_MODE.TRIGGER_INPUT_MODE_AND`, the trigger occurs when all source input events occur.\n
           If set to `STAR_system.triggering_types.TRIGGER_INPUT_MODE.TRIGGER_INPUT_MODE_OR`, the trigger occurs when any source input events occur.\n

           Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            mode (STAR_system.triggering_types.TRIGGER_INPUT_MODE): Trigger input mode. See enum for valid values.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                causeTrigger was not an int.\n
                internalTrigger was not an int.\n
                mode was not an TRIGGER_INPUT_MODE.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if isinstance(mode, TRIGGER_INPUT_MODE) is False:
            raise TypeError("mode must be an TRIGGER_INPUT_MODE.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setTriggerInputMode.argtypes = \
            [c_uint32, c_uint32, TRIGGER_INPUT_MODE]
        generic_triggering_lib.TRIGGER_CFG_setTriggerInputMode.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setTriggerInputMode(
            c_uint32(deviceId), c_uint32(internalTrigger), mode)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getTriggerInvertMask(deviceId, internalTrigger, triggerType) -> Tuple[bool, int]:
        """ Gets the invert mask for a trigger type for a specific internal trigger.\n
        The invert mask for a trigger type determines if a source of input events should have its signal
        inverted before reaching the internal trigger.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the trigger invert mask.

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger that is affected by
                                   the input events.
            triggerType (STAR_system.triggering_types.TRIGGER_TYPE): Type of the trigger. See enum for valid values.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
                triggerType was not a TRIGGER_TYPE.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if isinstance(triggerType, TRIGGER_TYPE) is False:
            raise TypeError("triggerType must be an TRIGGER_TYPE.")

        # Create pointer to unsigned int that represents the trigger invert mask
        triggerInvertMask = c_uint32(0)
        pTriggerInvertMask = pointer(triggerInvertMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTriggerInvertMask.argtypes = [c_uint32, c_uint32, TRIGGER_TYPE,
                                                                            POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getTriggerInvertMask.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getTriggerInvertMask(
            c_uint32(deviceId), c_uint32(internalTrigger), triggerType, pTriggerInvertMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(triggerInvertMask.value)

    @staticmethod
    def setTriggerInvertMask(deviceId, internalTrigger, triggerType, invertMask) -> bool:
        """Sets the invert mask for a trigger type for a specific internal trigger.\n
           The invert mask for a trigger type determines if a source of input events should have its signal
           inverted before reaching the internal trigger.\n

        Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            triggerType (STAR_system.triggering_types.TRIGGER_TYPE): Type of the trigger. See enum for valid values.
            invertMask (int): Invert mask.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
                triggerType was not a TRIGGER_TYPE.\n
                invertMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if isinstance(triggerType, TRIGGER_TYPE) is False:
            raise TypeError("triggerType must be an TRIGGER_TYPE.")

        if type(invertMask) != int:
            raise TypeError("invertMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setTriggerInvertMask.argtypes = [c_uint32, c_uint32, TRIGGER_TYPE, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setTriggerInvertMask.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setTriggerInvertMask(
            c_uint32(deviceId), c_uint32(internalTrigger), triggerType, c_uint32(invertMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getTriggerAndMask(deviceId, internalTrigger, triggerType) -> Tuple[bool, int]:
        """ Gets the AND/OR mask for a trigger type for a specific internal trigger.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the trigger mask.

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.
            triggerType (STAR_system.triggering_types.TRIGGER_TYPE): Type of the trigger. See enum for valid values.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
                triggerType was not a TRIGGER_TYPE.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if isinstance(triggerType, TRIGGER_TYPE) is False:
            raise TypeError("triggerType must be an TRIGGER_TYPE.")

        # Create pointer to unsigned int that represents the trigger mask
        triggerMask = c_uint32(0)
        pTriggerMask = pointer(triggerMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTriggerAndMask.argtypes = [c_uint32, c_uint32, TRIGGER_TYPE,
                                                                         POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getTriggerAndMask.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getTriggerAndMask(
            c_uint32(deviceId), c_uint32(internalTrigger), triggerType, pTriggerMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(triggerMask.value)

    @staticmethod
    def setTriggerAndMask(deviceId, internalTrigger, triggerType, mask) -> bool:
        """ Sets the AND/OR mask for a trigger type for a specific internal trigger.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.
            triggerType (STAR_system.triggering_types.TRIGGER_TYPE): Type of the trigger. See enum for valid values.
            mask (int): AND/OR mask.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                internalTrigger was not an int.\n
                triggerType was not a TRIGGER_TYPE.\n
                mask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if isinstance(triggerType, TRIGGER_TYPE) is False:
            raise TypeError("triggerType must be an TRIGGER_TYPE.")

        if type(mask) != int:
            raise TypeError("mask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setTriggerAndMask.argtypes = [c_uint32, c_uint32, TRIGGER_TYPE, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setTriggerAndMask.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setTriggerAndMask(
            c_uint32(deviceId), c_uint32(internalTrigger), triggerType, c_uint32(mask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterInputEvents(deviceId, counter, internalTrigger) -> Tuple[bool, int]:
        """ Gets the input events from a counter which will cause an internal trigger to be set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the
        counter input events.\n

        Args:\n
            deviceId (int): The ID of the device.
            counter (int): Number of the counter to get input events from.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                counter was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(counter) != int:
            raise TypeError("counter must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the counter input events
        inputEventsMask = c_uint32(0)
        pInputEventsMask = pointer(inputEventsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterInputEvents.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                             POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterInputEvents(
            c_uint32(deviceId), c_uint32(counter), c_uint32(internalTrigger), pInputEventsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(inputEventsMask.value)

    @staticmethod
    def setCounterInputEvents(deviceId, counter, internalTrigger, eventsMask) -> bool:
        """ Sets the input events for a counter which will cause an internal trigger to be set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            counter (int): Number of the counter to get input events from.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.
            eventsMask (int): Mask of the counter input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                counter was not an int.\n
                internalTrigger was not an int.\n
                eventsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(counter) != int:
            raise TypeError("counter must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(eventsMask) != int:
            raise TypeError("eventsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setCounterInputEvents.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setCounterInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setCounterInputEvents(
            c_uint32(deviceId), c_uint32(counter), c_uint32(internalTrigger), c_uint32(eventsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterOutputActions(deviceId, counter, internalTrigger) -> Tuple[bool, int]:
        """ Gets the output actions from a counter that are caused by an internal trigger being set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the counter
            output actions.\n

        Args:\n
            deviceId (int): The ID of the device.
            counter (int): Number of the counter to get input events from.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                counter was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(counter) != int:
            raise TypeError("counter must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the counter output actions
        outputActionsMask = c_uint32(0)
        pOutputActionsMask = pointer(outputActionsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterOutputActions.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                               POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterOutputActions.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterOutputActions(
            c_uint32(deviceId), c_uint32(counter), c_uint32(internalTrigger), pOutputActionsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(outputActionsMask.value)

    @staticmethod
    def setCounterOutputActions(deviceId, counter, internalTrigger, actionsMask) -> bool:
        """ Sets the output actions for a counter that are caused by an internal trigger being set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            counter (int): Number of the counter to get input events from.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.
            actionsMask (int): Mask of the counter output actions.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                counter was not an int.\n
                internalTrigger was not an int.\n
                actionsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(counter) != int:
            raise TypeError("counter must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(actionsMask) != int:
            raise TypeError("actionsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setCounterOutputActions.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setCounterOutputActions.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setCounterOutputActions(
            c_uint32(deviceId), c_uint32(counter), c_uint32(internalTrigger), c_uint32(actionsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterReloadValue(deviceId, timer) -> Tuple[bool, int]:
        """Gets the reload value for a specific counter.\n
           The reload value is the value that will be loaded into the counter when a reload occurs.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the counter reload value
        for the given counter.\n

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to get counter reload value for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Create pointer to unsigned int
        reloadValue = c_uint32(0)
        pReloadValue = pointer(reloadValue)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterReloadValue.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterReloadValue.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterReloadValue(c_uint32(deviceId), c_uint32(timer),
                                                                           pReloadValue)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(reloadValue.value)

    @staticmethod
    def setCounterReloadValue(deviceId, timer, reloadValue) -> bool:
        """Sets the reload value for a specific counter.\n
           The reload value is the value that will be loaded into the counter when a reload occurs.\n

           Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to set counter reload value for.
            reloadValue (int): The reload value of the counter.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
                reloadValue was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        if type(reloadValue) != int:
            raise TypeError("reloadValue must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setCounterReloadValue.argtypes = [c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setCounterReloadValue.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setCounterReloadValue(
            c_uint32(deviceId), c_uint32(timer), c_uint32(reloadValue))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def setExtTriggerExtend(deviceId, extTrigger, extendValue) -> bool:
        """Sets the extend duration for a specific external trigger.\n
           The extend duration is the duration, in cycles, of the trigger output signal pulse when a
           trigger output action occurs.\n

           Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to set extend value for.
            extendValue (int): Extend duration in cycles.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
                extendValue was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        if type(extendValue) != int:
            raise TypeError("extendValue must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setExtTriggerExtend.argtypes = [c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setExtTriggerExtend.restype = c_int32

        success = generic_triggering_lib.TRIGGER_CFG_setExtTriggerExtend(
            c_uint32(deviceId), c_uint32(extTrigger), c_uint32(extendValue))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def setExtTriggerInputEvents(deviceId, extTrigger, internalTrigger, eventsMask) -> bool:
        """Sets the input events for an external trigger which will cause an internal trigger to be set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to set input events for.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            eventsMask (int): Mask describing the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
                internalTrigger was not an int.\n
                eventsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(eventsMask) != int:
            raise TypeError("eventsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setExtTriggerInputEvents.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setExtTriggerInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setExtTriggerInputEvents(
            c_uint32(deviceId), c_uint32(extTrigger), c_uint32(internalTrigger), c_uint32(eventsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def setExtTriggerOutputActions(deviceId, extTrigger, internalTrigger, actionsMask) -> bool:
        """Sets the output actions for an external trigger that are caused by an internal trigger being set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            extTrigger (int): Number of the external trigger to set input events for.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            actionsMask (int): Mask describing the output actions.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                extTrigger was not an int.\n
                internalTrigger was not an int.\n
                actionsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(extTrigger) != int:
            raise TypeError("extTrigger must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(actionsMask) != int:
            raise TypeError("actionsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setExtTriggerOutputActions.argtypes = \
            [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setExtTriggerOutputActions.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setExtTriggerOutputActions(
            c_uint32(deviceId), c_uint32(extTrigger), c_uint32(internalTrigger), c_uint32(actionsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def setPortInputEvents(deviceId, port, internalTrigger, eventsMask) -> bool:
        """Sets the input events for a port which will cause an internal trigger to be set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port to set input events for.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            eventsMask (int): Mask describing the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
                internalTrigger was not an int.\n
                eventsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(eventsMask) != int:
            raise TypeError("eventsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setPortInputEvents.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setPortInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setPortInputEvents(
            c_uint32(deviceId), c_uint32(port), c_uint32(internalTrigger), c_uint32(eventsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def setPortOutputActions(deviceId, port, internalTrigger, actionsMask) -> bool:
        """Sets the output actions for a port that are caused by an internal trigger being set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port to set output actions for.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            actionsMask (int): Mask describing the output actions.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
                internalTrigger was not an int.\n
                actionsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(actionsMask) != int:
            raise TypeError("actionsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setPortOutputActions.argtypes = \
            [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setPortOutputActions.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setPortOutputActions(
            c_uint32(deviceId), c_uint32(port), c_uint32(internalTrigger), c_uint32(actionsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getCounterValue(deviceId, timer) -> Tuple[bool, int]:
        """Gets the counter value for a specific counter.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the counter value
            for the given counter.\n

        Args:\n
            deviceId (int): The ID of the device.
            timer (int): Number of the counter to get counter value for/of.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timer was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timer) != int:
            raise TypeError("timer must be an int.")

        # Create pointer to unsigned int
        counterValue = c_uint32(0)
        pCounterValue = pointer(counterValue)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getCounterValue.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getCounterValue.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getCounterValue(c_uint32(deviceId), c_uint32(timer),
                                                                     pCounterValue)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(counterValue.value)

    @staticmethod
    def getTimeCodeInputEvents(deviceId, timeCode, internalTrigger) -> Tuple[bool, int]:
        """ Gets the input events from a time-code engine which will cause an internal trigger to be set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the given
        time-code engine input events.\n

        Args:\n
            deviceId (int): The ID of the device.
            timeCode (int): Number of the time-code engine.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timeCode was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timeCode) != int:
            raise TypeError("timeCode must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the time-code engine input events
        inputEventsMask = c_uint32(0)
        pInputEventsMask = pointer(inputEventsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTimeCodeInputEvents.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                              POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getTimeCodeInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getTimeCodeInputEvents(
            c_uint32(deviceId), c_uint32(timeCode), c_uint32(internalTrigger), pInputEventsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(inputEventsMask.value)

    @staticmethod
    def setTimeCodeInputEvents(deviceId, timeCode, internalTrigger, eventsMask) -> bool:
        """Sets the input events for a time-code engine which will cause an internal trigger to be set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            timeCode (int): Number of the time-code engine to set the input events for.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            eventsMask (int): Mask describing the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timeCode was not an int.\n
                internalTrigger was not an int.\n
                eventsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timeCode) != int:
            raise TypeError("timeCode must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(eventsMask) != int:
            raise TypeError("eventsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setTimeCodeInputEvents.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setTimeCodeInputEvents.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setTimeCodeInputEvents(
            c_uint32(deviceId), c_uint32(timeCode), c_uint32(internalTrigger), c_uint32(eventsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getTimeCodeOutputActions(deviceId, timeCode, internalTrigger) -> Tuple[bool, int]:
        """ Gets the output actions from a time-code engine that are caused by an internal trigger being set.\n

        Returns a tuple: True if the function completes correctly, False otherwise and the mask of the given
        time-code engine output actions.\n

        Args:\n
            deviceId (int): The ID of the device.
            timeCode (int): Number of the time-code engine.
            internalTrigger (int): Number of the internal trigger that is affected by the input events.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timeCode was not an int.\n
                internalTrigger was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timeCode) != int:
            raise TypeError("timeCode must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        # Create pointer to unsigned int that represents the mask of the time-code engine output actions
        outputActionsMask = c_uint32(0)
        pOutputActionsMask = pointer(outputActionsMask)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTimeCodeOutputActions.argtypes = [c_uint32, c_uint32, c_uint32,
                                                                                POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getTimeCodeOutputActions.restype = c_int32

        success = generic_triggering_lib.TRIGGER_CFG_getTimeCodeOutputActions(
            c_uint32(deviceId), c_uint32(timeCode), c_uint32(internalTrigger), pOutputActionsMask)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, int(outputActionsMask.value)

    @staticmethod
    def setTimeCodeOutputActions(deviceId, timeCode, internalTrigger, actionsMask) -> bool:
        """Sets the output actions for a time-code engine that are caused by an internal trigger being set.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            timeCode (int): Number of the time-code engine to set the input events for.
            internalTrigger (int): Number of the internal trigger which is affected by the input events.
            actionsMask (int): Mask describing the output actions.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                timeCode was not an int.\n
                internalTrigger was not an int.\n
                actionsMask was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(timeCode) != int:
            raise TypeError("timeCode must be an int.")

        if type(internalTrigger) != int:
            raise TypeError("internalTrigger must be an int.")

        if type(actionsMask) != int:
            raise TypeError("actionsMask must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_setTimeCodeOutputActions.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_setTimeCodeOutputActions.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_setTimeCodeOutputActions(
            c_uint32(deviceId), c_uint32(timeCode), c_uint32(internalTrigger), c_uint32(actionsMask))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def enablePortSpill(deviceId, port) -> bool:

        """Enables spilling for a specific port.\n
           While enabled AND the port has transmit packet mode enabled, queued packets are spilled.\n

          Note: This function is currently only supported by Brick Mk3 devices
          with FPGA versions v1.05e15 and v1.00e09, respectively.\n

          Returns True if the function completes correctly, False otherwise.

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of port to enable spilling on.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_enablePortSpill.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_enablePortSpill.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_enablePortSpill(c_uint32(deviceId), c_uint32(port))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def disablePortSpill(deviceId, port) -> bool:
        """Disables spilling for a specific port.\n

          Note: This function is currently only supported by Brick Mk3 devices
          with FPGA versions v1.05e15 and v1.00e09, respectively.\n

          Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of port to disable spilling on.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_disablePortSpill.argtypes = [c_uint32, c_uint32]
        generic_triggering_lib.TRIGGER_CFG_disablePortSpill.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_disablePortSpill(c_uint32(deviceId), c_uint32(port))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getPortSpillEnabled(deviceId, port) -> Tuple[bool, bool]:
        """Gets whether packet transmit mode is enabled for a specific port.\n

        Returns a tuple: True if the function completes correctly, False otherwise and True if port spill
        is enabled for the given port, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.
            port (int): Number of the port to get spill enabled attribute for.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
                port was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        if type(port) != int:
            raise TypeError("port must be an int.")

        # Create pointer to unsigned int
        enabled = c_uint32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getPortSpillEnabled.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        generic_triggering_lib.TRIGGER_CFG_getPortSpillEnabled.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_getPortSpillEnabled(c_uint32(deviceId), c_uint32(port),
                                                                         pEnabled)

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value, bool(enabled.value)

    @staticmethod
    def reset(deviceId) -> bool:
        """Resets the triggering configuration to its default state.\n

        Returns True if the function completes correctly, False otherwise.\n

        Args:\n
            deviceId (int): The ID of the device.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_reset.argtypes = [c_uint32]
        generic_triggering_lib.TRIGGER_CFG_reset.restype = c_int32

        # Returns 1 in case the function succeeds (executes correctly)
        success = generic_triggering_lib.TRIGGER_CFG_reset(c_uint32(deviceId))

        return success == STAR_OPERATION_RESULT.STAR_SUCCESS.value

    @staticmethod
    def getTriggerMatrix(deviceId) -> STAR_TRIGGER_MATRIX:
        """Returns the trigger matrix for the given device type.\n

        Args:\n
            deviceId (int): The ID of the device.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getTriggerMatrix.argtypes = [c_uint32]
        generic_triggering_lib.TRIGGER_CFG_getTriggerMatrix.restype = STAR_TRIGGER_MATRIX

        triggerMatrix = generic_triggering_lib.TRIGGER_CFG_getTriggerMatrix(c_uint32(deviceId))

        return triggerMatrix

    @staticmethod
    def getDeviceClockRate(deviceId) -> int:
        """Returns the clock rate used by the triggering system for the specified device type.\n

        Args:\n
            deviceId (int): The ID of the device.

        Raises:\n
            STARAPIError:\n
                The STAR-API Triggering library could not be loaded.\n
                This functionality is not supported on the specified device.\n
            TypeError:\n
                deviceId was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if generic_triggering_lib is None:
            raise STARAPIError(STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR)

        if type(deviceId) != int:
            raise TypeError("deviceId must be an int.")

        # Set argument types and return type of the C function
        generic_triggering_lib.TRIGGER_CFG_getDeviceClockRate.argtypes = [c_uint32]
        generic_triggering_lib.TRIGGER_CFG_getDeviceClockRate.restype = c_int32

        clockRate = generic_triggering_lib.TRIGGER_CFG_getDeviceClockRate(c_uint32(deviceId))

        return int(clockRate)
