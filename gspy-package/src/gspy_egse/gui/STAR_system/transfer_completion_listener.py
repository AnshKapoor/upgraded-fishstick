"""Used to create a transfer operation completion call-back function.

Brief:\n
    Used to create a transfer operation completion call-back function.

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


class TransferCompletionListener(object):
    """Creates a transfer operation completion call-back function.
    
    Attributes:\n
        _callback: (CFUNCTYPE) C-formatted version of the call-back function. This is kept as
            a reference so that as long as the TransferCompletionListener instance 
            is alive, the call-back function will not be garbage collected.
        _transferOperation: (int) Pointer to the transferOperation that the listener is registered for.
    """

    def __init__(self, callback, transferOperation, contextObject=None):
        """Constructor:\n
            Registers a call-back function that will be called when an operation completes.

            A reference to this the TransferCompletionListener instance will be saved in the TransferOperation object
            that the listener is registered to. The user does not need to save this returned object anywhere else.\n

        Args:\n
            callback (function): The call-back function can either have no arguments or the following signature \n
                callback(transferOperationAddress, status, contextObject)\n
                where \n
                transferOperationAddress is the address of the transfer operation within the C API -
                this value should be ignored.\n
                status is the status of the transfer operation which has completed. See `STAR_system.STAR_enums.STAR_TRANSFER_STATUS`
                for valid values.\n
                contextObject is user-specific data that is provided when the completion listener is registered.\n
                The transferOperationAddress and status input parameters are ints, while the contextObject is an instance
                of any user-defined class.\n
            transferOperation (STAR_system.transfer_operations.TransferOperation): The operation to add a listener for.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.
                
        Raises:\n
        
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The call-back was not successfully registered.\n
                Could not pickle context object.\n
                
            TypeError:\n
                callback is not a function.\n
                transferOperation is not a TransferOperation.\n
                contextObject is not an object that can be pickled.\n

            ValueError:\n
                Raised by getCtypesCallbackFunction.
        """

        from gspy_egse.gui.STAR_system.transfer_operations import TransferOperation

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType) is False:
            raise TypeError("callback must be a function/method.")
        if dill.pickles(contextObject) is False:
            raise TypeError("contextObject must be an object that can be pickled.")
        if isinstance(transferOperation, TransferOperation) is False:
            raise TypeError("transferOperation must be an instance of TransferOperation.")

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

        # Cast the transfer operation object to void pointer
        pTransferOperation = cast(transferOperation._structAddress, c_void_p)
        self._transferOperation = transferOperation._structAddress

        # Set argument types and return type of the C function
        star_lib.STAR_registerTransferCompletionListener.argtypes = [c_void_p, type(c_callback), c_void_p]
        star_lib.STAR_registerTransferCompletionListener.restype = c_int32

        status = star_lib.STAR_registerTransferCompletionListener(pTransferOperation,
                                                                  c_callback, self._context)

        if status == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Failed to register call-back.")

    @staticmethod
    def getCtypesCallbackFunction(callback):
        """Creates a CFUNCTYPE object using the provided function.

        Raises:\n
            ValueError:\n
                Call-back function must have 0 or 3 arguments.\n
        """

        sig = signature(callback)

        if str(sig) == "()":    # no arguments
            return CFUNCTYPE(None)(callback)    # Create call-back function.
        
        if str(sig).count(",") != 2:
            raise ValueError("Call-back function must have 0 or 3 arguments.")

        return CFUNCTYPE(None, c_void_p, c_int32, c_void_p)(callback)

    def unregister(self):
        """Unregisters a call-back function that will be called when an operation completes.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Failed to unregister call-back.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        pTransferOperation = cast(self._transferOperation, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_unregisterTransferCompletionListener.argtypes = [c_void_p, type(self._callback)]
        star_lib.STAR_unregisterTransferCompletionListener.restype = c_int32

        status = star_lib.STAR_unregisterTransferCompletionListener(pTransferOperation, self._callback)

        if status == STAR_OPERATION_RESULT.STAR_ERROR.value:
            raise STARAPIError("Failed to unregister call-back.")
