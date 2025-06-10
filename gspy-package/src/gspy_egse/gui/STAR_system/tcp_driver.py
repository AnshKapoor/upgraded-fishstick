"""Represents a TCP driver for use with GbE devices.

Brief:\n
    Represents a TCP driver for use with GbE devices.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
import numpy as np
from ctypes import *

from gspy_egse.gui.STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.driver import Driver
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.STAR_enums import STAR_OPERATION_RESULT
from gspy_egse.gui.STAR_system.STAR_structures import STAR_IP_ADDRESS_TYPE
from gspy_egse.gui.STAR_system.STAR_structure_classes import StarIpAddressType

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


class TCPDriver(Driver):
    """Represents a TCP driver for use with GbE devices.

    Attributes:\n
        driverID (int): ID of the Driver.
    """

    def __init__(self):
        """Constructor:\n
            Opens the TCP/IP driver.\n

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API failed to open the driver.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_openEthernetDriver.argtypes = []
        star_lib.STAR_openEthernetDriver.restype = c_uint32

        driverID = star_lib.STAR_openEthernetDriver()

        if driverID == 0:
            raise STARAPIError("Failed to open driver.")

        self.driverID = driverID

    def close(self):
        """Closes the TCP/IP driver.

        Closing the driver will automatically close any open TCP devices, and may
        result in data loss if transmits of receives are in progress.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The driver was not successfully closed.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_closeEthernetDriver.argtypes = [c_uint32]
        star_lib.STAR_closeEthernetDriver.restype = c_int32

        status = star_lib.STAR_closeEthernetDriver(c_uint32(self.driverID))

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Driver was not successfully closed.")

    def getIPAddresses(self) -> list:
        """Scans all attached Ethernet devices and stores their IP version number and IP addresses.\n
        Returns a list of `STAR_system.STAR_structure_classes.StarIpAddressType` objects.

            Raises:\n
                STARAPIError:\n
                    The STAR-API library could not be loaded.\n
                    Could not get list containing the resulting `STAR_system.STAR_structure_classes.StarIpAddressType` objects.
                    Could not destroy 'STAR_system.STAR_structures.STAR_IP_ADDRESS_TYPE' objects.
                TypeError:\n
                    Could not IP address bytes.\n
                    Could not create `STAR_system.STAR_structure_classes.StarIpAddressType` object.
                ValueError:\n
                    Could not create `STAR_system.STAR_structure_classes.StarIpAddressType` object.
            """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create list that will hold the StarIpAddressType objects
        StarIPAddressTypesList = []

        # Create input parameters to STAR_getIPAddresses C function call
        numberOfDevices = c_int32(0)
        pNumberOfDevices = pointer(numberOfDevices)

        # Set argument types and return type of the C function
        star_lib.STAR_getIPAddresses.argtypes = [c_uint32, POINTER(c_int32)]
        star_lib.STAR_getIPAddresses.restype = POINTER(POINTER(STAR_IP_ADDRESS_TYPE))

        ppStarIPAddressTypes = star_lib.STAR_getIPAddresses(c_uint32(self.driverID), pNumberOfDevices)

        # Check that the function succeeded
        if numberOfDevices.value < 0:
            raise STARAPIError("STAR_getIPAddresses failed to allocate required memory.")

        # For each device that was found, retrieve the IP version and IP address values
        for i in range(0, numberOfDevices.value):

            pStarIPAddressTypesContents = ppStarIPAddressTypes.contents
            StarIPAddressTypesContents = pStarIPAddressTypesContents.contents

            # Get raw packet bytes (void) pointer and cast it to byte ptr
            IPVersion = int(StarIPAddressTypesContents.IPVersion)
            IPAddressBytesPtr = cast(StarIPAddressTypesContents.IPAddress, POINTER(c_uint8))

            # Get the values as list
            try:
                IPAddressBytesList = list(np.ctypeslib.as_array(IPAddressBytesPtr, (IPVersion,)).tobytes())
            except TypeError:
                raise

            # Create StarIpAddressType object
            try:
                starIPAddressObject = StarIpAddressType(IPVersion, IPAddressBytesList)
            except (TypeError, ValueError):
                raise

            # Add this StarIpAddressType object to the list
            StarIPAddressTypesList.append(starIPAddressObject)

        # In case there is at least one object containing IP address
        if numberOfDevices.value > 0:

            # Free IP addresses (they are now represented as StarIpAddressType objects).
            # Set argument types and return type of the C function
            star_lib.STAR_destroyIPAddresses.argtypes = [POINTER(POINTER(STAR_IP_ADDRESS_TYPE)), c_uint8]
            star_lib.STAR_destroyIPAddresses.restype = c_int32

            success = star_lib.STAR_destroyIPAddresses(ppStarIPAddressTypes, c_uint8(numberOfDevices.value))

            if success != STAR_OPERATION_RESULT.STAR_SUCCESS:
                raise STARAPIError("Could not destroy IP addresses.")

        return StarIPAddressTypesList
