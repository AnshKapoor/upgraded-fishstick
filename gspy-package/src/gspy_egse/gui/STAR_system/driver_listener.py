"""Manages a driver call-back function.

Brief:\n
    Manages a driver call-back function.

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


class DriverListener(object):
    """Manages a driver call-back function.
    
    Attributes:\n
        _callback (function): C-formatted version of the call-back function. This is kept as
            a reference so that as long as the `STAR_system.driver_listener.DriverListener` instance is alive,
            the call-back function will not be garbage collected.
        listenerID (int): The ID of the listener.
    """

    def __init__(self, callback, contextObject=None, notifyForCurrent=False):
        """Constructor:\n
            Registers a call-back function that will be called whenever a driver is added or removed.

        Args:\n
            callback (function): The call-back function can either have no arguments or the following signature \n
                callback(driverListenerIdentifier, driverIdentifier, driverAdded, contextObject)\n
                where \n
                driverListenerIdentifier is the driver listener that this event corresponds to.\n
                driverIdentifier is the driver which has been added or removed.\n
                driverAdded is whether the driver was added (1) or removed (0).\n
                contextObject is user-specific data that is provided when the driver listener is registered.\n
                The driverListenerIdentifier, driverIdentifier and driverAdded input parameters are ints,
                while the contextObject is an instance of any user-defined class.\n
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.\n
            notifyForCurrent (bool): Whether the function should be called for
                all existing drivers to indicate that they've been added. Default value is False.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Failed to register call-back.\n
                Could not pickle context object.\n
            TypeError:\n
                callback is not a function.\n
                contextObject is not an object that can be pickled.\n
                notifyForCurrent is not bool.\n
            ValueError:\n
                Call-back function must have 0 or 4 arguments.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType):
            raise TypeError("callback must be a function.")
        if dill.pickles(contextObject) is False:
            raise TypeError("contextObject must be an object that can be pickled.")
        if type(notifyForCurrent) != bool:
            raise TypeError("notifyForCurrent must be bool.")

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

        # Set argument types and return type of the C function
        star_lib.STAR_registerDriverListener.argtypes = [type(c_callback), c_void_p, c_int32]
        star_lib.STAR_registerDriverListener.restype = c_uint32

        status = star_lib.STAR_registerDriverListener(c_callback, self._context, c_int32(notifyForCurrent))

        if status == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Failed to register callback.")
        
        self.listenerID = status

    @staticmethod
    def getCtypesCallbackFunction(callback):
        """Creates a CFUNCTYPE object using the provided function.

        Raises:\n
            ValueError:\n
                Call-back function must have 0 or 4 arguments.\n
        """
        sig = signature(callback)

        if str(sig) == "()":    # no arguments
            return CFUNCTYPE(None)(callback)    # Create call-back function.
        
        if str(sig).count(",") != 3:
            raise ValueError("Call-back function must have 0 or 4 arguments.")

        return CFUNCTYPE(None, c_uint32, c_uint32, c_int32, c_void_p)(callback)

    def unregister(self):
        """Unregisters a driver listener.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Failed to unregister call-back.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_unregisterDriverListener.argtypes = [c_uint32]
        star_lib.STAR_unregisterDriverListener.restype = c_int32

        status = star_lib.STAR_unregisterDriverListener(c_uint32(self.listenerID))

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Failed to unregister call-back.")


