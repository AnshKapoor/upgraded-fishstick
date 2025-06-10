"""Represents a TCP device, e.g. GbE Brick.

Brief:\n
    Represents a TCP device, e.g. GbE Brick.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

import os
from ctypes import *

from gspy_egse.gui.STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.device import Device
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


class TCPDevice(Device):
    """Represents a TCP device, e.g. GbE Brick.
    
    Attributes:\n
        deviceID (int): ID of the device.

    Args:\n
        ipAddress (str): The IPv4 address of the device to open.
    """

    def __init__(self, ipAddress):
        """Constructor:\n
            Opens a TCP/IP connected device.\n

            The TCP driver will automatically be opened, if it has not already been
            opened by calling `STAR_system.tcp_driver.TCPDriver`.\n

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API failed to open the device.\n
            TypeError:\n
                ipAddress is not a str.\n
            ValueError:\n
                Invalid ipAddress.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(ipAddress) != str:
            raise TypeError("ipAddress must be str.")

        self.addressBytes = ipAddress.split(".")

        # Convert str to int
        try:
            self.addressBytes = [int(byte) for byte in self.addressBytes]
        except Exception:
            raise ValueError("ipAddress must be of format 'byte1.byte2.byte3.byte4'.")

        # Validate address
        for byte in self.addressBytes:
            if byte < 0 or byte > 255:
                raise ValueError("Each byte must be between 0 and 255 inclusive.")

        if len(self.addressBytes) != 4:
            raise ValueError("Invalid ipAddress length. \
                              ipAddress must be of format 'byte1.byte2.byte3.byte4'.")

        self.ipAddressArray = (c_char * 4)()
        for i in range(4):
            self.ipAddressArray[i] = c_char(self.addressBytes[i])

        # Set argument types and return type of the C function
        star_lib.STAR_openEthernetDevice.argtypes = [type(self.ipAddressArray)]
        star_lib.STAR_openEthernetDevice.restype = c_uint32

        deviceID = star_lib.STAR_openEthernetDevice(self.ipAddressArray)

        if deviceID == 0:
            raise STARAPIError("Failed to open TCP device.")

        self.deviceID = deviceID

    def close(self):
        """Closes an open TCP/IP device.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API was unable to successfully close the device.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_closeEthernetDevice.argtypes = [c_uint32]
        star_lib.STAR_closeEthernetDevice.restype = c_int32

        status = star_lib.STAR_closeEthernetDevice(c_uint32(self.deviceID))

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Failed to close the device.")


