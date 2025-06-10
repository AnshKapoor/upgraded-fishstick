""" Represents an application.

Brief:\n
    Represents an application.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
from ctypes import *

from gspy_egse.gui.STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
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


class Application(object):
    """Represents an application."""

    @staticmethod
    def getApplicationID() -> int:
        """Gets and returns the application ID of the calling process."""

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getApplicationID.argtypes = []
        star_lib.STAR_getApplicationID.restype = c_uint32

        # Get the application ID
        applicationID = star_lib.STAR_getApplicationID()

        return applicationID

    def getApplicationName(self) -> str:
        """Gets and returns the name of the calling process (this process)."""

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Get the application ID
        applicationID = self.getApplicationID()

        # Set argument types and return type of the C function
        star_lib.STAR_getApplicationNameForID.argtypes = [c_uint32]
        star_lib.STAR_getApplicationNameForID.restype = c_char_p

        # Get the application name
        applicationNameBytes = star_lib.STAR_getApplicationNameForID(applicationID)
        applicationNameStr = applicationNameBytes.decode('utf-8')

        return applicationNameStr

    @staticmethod
    def setApplicationName(name):
        """Sets the name of the application using STAR-API.

        This is the name provided to other processes calling Application.getApplicationName().

        Args:\n
            name (str): The application name.

        Raises:\n
            TypeError:\n
                name was not a string.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(name) != str:
            raise TypeError("name must be str.")

        cName = name.encode('utf-8')
        cNamePtr = cast(cName, POINTER(c_char))

        # Set argument types and return type of the C function
        star_lib.STAR_setApplicationName.argtypes = [c_char_p]
        star_lib.STAR_setApplicationName.restype = c_int32

        # Call the C function from the library
        status = star_lib.STAR_setApplicationName(cNamePtr)

        # Check result
        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Failed to set application name.")

