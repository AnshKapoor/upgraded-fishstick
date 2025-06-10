"""Used to create a channel call-back function.

Brief:\n
    Used to create a channel call-back function.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
import types
import dill

from ctypes import *
from inspect import signature

from gspy_egse.gui.STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.common import STARCommon
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.STAR_enums import STAR_OPERATION_RESULT

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


class ChannelListener(object):
    """Used to create a channel call-back function.
    
    Attributes:\n
        _callback (function): C-formatted version of the call-back function. This is kept as
            a reference so that as long as the `STAR_system.channel_listener.ChannelListener` instance is alive,
            the call-back function will not be garbage collected.
        deviceID (int): The ID of the device for which the call-back is registered.
            If the call back is for all devices, this attribute is None.
        listenerID (int): The ID of the listener.
    """

    def __init__(self, callback, deviceID=None, driverID=None, contextObject=None, notifyForCurrent=False):
        """Constructor:\n
            Registers a call-back function that will be called whenever any channel is opened or closed.

            The user must keep a reference to the `STAR_system.channel_listener.ChannelListener` instance to avoid the
            call-back being garbage collected, which will cause the program to crash when the call-back is called.

        Args:\n
            callback (function): The call-back function can either have no arguments or the following signature\n
                callback(channelListenerIdentifier, driverIdentifier, deviceIdentifier,
                              channelIdentifier, channelOpened, channelNumber, contextObject)\n
                where\n
                channelListenerIdentifier is the channel listener that the event corresponds to.\n
                driverIdentifier is the driver of the device on which the channel was opened or closed.\n
                deviceIdentifier is the device on which the channel was opened or closed.\n
                channelIdentifier is the identifier of the channel which has been opened or closed.\n
                channelOpened is whether the channel was opened (1) or closed (0).\n
                channelNumber is the channel number on the device of the channel which was opened or closed.\n
                contextObject is user-specific data that is provided when the channel listener is registered.\n
                Every parameter of the callback function is an int.
                These are automatically passed to the callback function when it is called.\n
            deviceID (int): Optional deviceID of the device to create the listener
                for. The call-back will only
                be called when a channel on the device with the specified ID is
                opened or closed.
            driverID (int): Optional driverID of the driver to create the listener
                for. The call-back will only be called
                when a channel on a device with the specified driver is opened or
                closed.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.
            notifyForCurrent (bool): Whether the function should be called for
                all existing channels to indicate that they've been opened. Default
                value is False.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                Failed to register channel listener.\n
                Could not pickle context object.\n
            TypeError:\n
                callback is not a function.\n
                deviceID is not None or an int.\n
                driverID is not None or an int.\n
                notifyForCurrent is not a bool.\n
                contextObject is not an object that can be pickled.\n
            ValueError:\n
                Both driverID and deviceID are not None.\n
                getCtypesCallbackFunction function failed.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType) is False:
            raise TypeError("callback must be a function.")
        if isinstance(notifyForCurrent, bool) is False:
            raise TypeError("notifyForCurrent must be bool.")
        if deviceID is not None and type(deviceID) != int:
            raise TypeError("deviceID must be None or int.")
        if driverID is not None and type(driverID) != int:
            raise TypeError("driverID must be None or int.")
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

        if deviceID is not None:

            # Set argument types and return type of the C function
            star_lib.STAR_registerChannelListenerForDevice.argtypes = [c_uint32, type(c_callback), c_void_p, c_int32]
            star_lib.STAR_registerChannelListenerForDevice.restype = c_uint32

            status = star_lib.STAR_registerChannelListenerForDevice(
                c_uint32(deviceID), c_callback, self._context, c_int32(notifyForCurrent))

        elif driverID is not None:

            # Set argument types and return type of the C function
            star_lib.STAR_registerChannelListenerForDriver.argtypes = [c_uint32, type(c_callback), c_void_p, c_int32]
            star_lib.STAR_registerChannelListenerForDriver.restype = c_uint32

            status = star_lib.STAR_registerChannelListenerForDriver(
                c_uint32(driverID), c_callback, self._context, c_int32(notifyForCurrent))
            
        else:
            self.deviceID = None

            # Set argument types and return type of the C function
            star_lib.STAR_registerChannelListener.argtypes = [type(c_callback), c_void_p, c_int32]
            star_lib.STAR_registerChannelListener.restype = c_uint32

            status = star_lib.STAR_registerChannelListener(c_callback, self._context, c_int32(notifyForCurrent))

        if status == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Failed to register call-back.")
        
        self.listenerID = status

    @staticmethod
    def getCtypesCallbackFunction(callback):
        """Creates a CFUNCTYPE object using the provided function.

        Raises:\n
            ValueError:\n
                Call-back function must have 0 or 7 arguments.\n
        """
        sig = signature(callback)

        if str(sig) == "()":
            return CFUNCTYPE(None)(callback)
        
        if str(sig).count(",") != 6:
            raise ValueError("Call-back function must have 0 or 7 arguments.")

        return CFUNCTYPE(None, c_uint32, c_uint32, c_uint32, c_uint32, c_int32, c_uint8, c_void_p)(callback)

    def unregister(self):
        """Unregister the call-back function.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                Failure unregistering call-back.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_unregisterChannelListener.argtypes = [c_uint32]
        star_lib.STAR_unregisterChannelListener.restype = c_int32

        status = star_lib.STAR_unregisterChannelListener(self.listenerID)

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Failure unregistering call-back.")



