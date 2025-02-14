"""Used to create a device call-back function.

Brief:\n
    Used to create a device call-back function.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

import os
import types
import dill

from ctypes import *
from inspect import signature

from STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from STAR_system.common import STARCommon
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_enums import STAR_OPERATION_RESULT

# Load C API
systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    try:
        star_lib = windll.LoadLibrary(STAR_LIB)
    except Exception:
        star_lib = None
        print(STAR_API_LIB_LOAD_ERROR_STR)

elif systemType == "posix":
    try:
        star_lib = cdll.LoadLibrary(STAR_LIB)
    except Exception:
        star_lib = None
        print(STAR_API_LIB_LOAD_ERROR_STR)


class DeviceListener(object):
    """Used to create device callback functions.
    
    Attributes:\n
        _callback (function): C-formatted version of the call-back function. This is kept as
            a reference so that as long as the `STAR_system.device_listener.DeviceListener` instance is alive,
            the call-back function will not be garbage collected.
        listenerID (int): The ID of the listener.
    """

    def __init__(self, callback, deviceID=None, driverID=None, contextObject=None, notifyForCurrent=False):
        """Constructor:\n
            Registers a call-back function that will be called whenever a device is added or removed.

        The user must keep a reference to the `STAR_system.device_listener.DeviceListener` instance to avoid the
        call-back being garbage collected, which will cause the program to crash when the call-back is called.

        Args:\n
            callback (function): The call-back function can have no arguments or the following signature\n
                callback(deviceListenerIdentifier, driverIdentifier, deviceIdentifier, deviceAdded, contextObject)\n
                where\n
                deviceListenerIdentifier is the device listener that this event corresponds to.\n
                driverIdentifier is the driver on which the device was added or removed.\n
                deviceIdentifier is the device which was added or removed.\n
                deviceAdded is whether the device has been added (1) or removed (0).\n
                contextObject is user-specific data that is provided when the channel listener is registered.\n
                Every parameter of the callback function is an int.
                These are automatically passed to the callback function when it is called.\n
            deviceID (int): Optional deviceID of the device to create the listener
                for. The call-back will only
                be called when the device with the specified ID is disconnected.
            driverID (int): Optional driverId of the driver to create a listener
                for. The call-back will only be called when a device with the
                specified driver is connected or disconnected. driverID and deviceID
                cannot both be not-None.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.
            notifyForCurrent (bool): Whether the function should be called for
                all existing devices to indicate that they've been added. Default
                value is False. notifyForCurrent is ignored when creating a listener
                for a specific device ID.
                
        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The call-back was not successfully registered.\n
                Could not pickle context object.\n
            TypeError:\n
                callback is not a function.\n
                deviceID is not None or an int.\n
                driverID is not None or an int.\n
                contextObject is not an object that can be pickled.\n
                notifyForCurrent is not bool.\n
            ValueError:\n
                Both of deviceID and driverID are not None.\n
                Raised by getCtypesCallbackFunction.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType) is False:
            raise TypeError("callback must be a function.")
        if deviceID is not None and type(deviceID) != int:
            raise TypeError("deviceID must be None or an int.")
        if driverID is not None and type(driverID) != int:
            raise TypeError("driverID must be None or an int.")
        if type(notifyForCurrent) != bool:
            raise TypeError("notifyForCurrent must be bool.")
        if deviceID is not None and driverID is not None:
            raise ValueError("At least one of deviceID and driverID must be None.")
        if dill.pickles(contextObject) is False:
            raise TypeError("contextObject must be an object that can be pickled.")

        try:
            c_callback = self.getCtypesCallbackFunction(callback)
        except ValueError:
            raise

        self._callback = c_callback

        # Pickle the context object and save a reference to it
        try:
            self._context = STARCommon.saveContextObject(contextObject)
        except STARAPIError:
            raise

        # Register with C API
        if deviceID is not None:

            # Set argument types and return type of the C function
            star_lib.STAR_registerDeviceListenerForDevice.argtypes = [c_uint32, type(c_callback), c_void_p]
            star_lib.STAR_registerDeviceListenerForDevice.restype = c_uint32

            status = star_lib.STAR_registerDeviceListenerForDevice(c_uint32(deviceID), c_callback, self._context)
        elif driverID is not None:

            # Set argument types and return type of the C function
            star_lib.STAR_registerDeviceListenerForDriver.argtypes = [c_uint32, type(c_callback), c_void_p, c_int32]
            star_lib.STAR_registerDeviceListenerForDriver.restype = c_uint32

            status = star_lib.STAR_registerDeviceListenerForDriver(c_uint32(driverID), c_callback, self._context,
                                                                   c_int32(notifyForCurrent))
        else:

            # Set argument types and return type of the C function
            star_lib.STAR_registerDeviceListener.argtypes = [type(c_callback), c_void_p, c_int32]
            star_lib.STAR_registerDeviceListener.restype = c_uint32

            status = star_lib.STAR_registerDeviceListener(c_callback, self._context, c_int32(notifyForCurrent))

        if status == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Failed to register call-back.")
        
        self.listenerID = status

    @staticmethod
    def getCtypesCallbackFunction(callback):
        """Creates a CFUNCTYPE object using the provided function.

        Raises:\n
            ValueError:\n
                Call-back function must have 0 or 5 arguments.\n
        """

        sig = signature(callback)

        if str(sig) == "()":    # no arguments
            return CFUNCTYPE(None)(callback)    # Create call-back function.
        
        if str(sig).count(",") != 4:
            raise ValueError("Call-back function must have 0 or 5 arguments.")

        return CFUNCTYPE(None, c_uint32, c_uint32, c_uint32, c_int32, c_void_p)(callback)

    def unregister(self):
        """Unregister the call-back function that was previously registered
        to be called whenever a device is added or removed.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Failed to unregister call-back.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_unregisterDeviceListener.argtypes = [c_uint32]
        star_lib.STAR_unregisterDeviceListener.restype = c_int32

        status = star_lib.STAR_unregisterDeviceListener(c_uint32(self.listenerID))

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Failed to unregister call-back.")