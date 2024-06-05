"""Represents a remote device.

Brief:\n
    Represents a remote device.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
from ctypes import *

from STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from STAR_system.device import Device
from STAR_system.channel import Channel
from STAR_system.device_config import DeviceConfig
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_structures import STAR_SPACEWIRE_ADDRESS
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


class RemoteDevice(DeviceConfig):
    """Represents a remote device.
    
    Attributes:
        deviceId (int): The ID of the device.
    """

    def __init__(self, *args, **kwargs):
        """Constructor:\n
            Creates a `STAR_system.remote_device.RemoteDevice` object.\n
            Remote device identifiers are used to describe to the config API how to reach a remote device.\n

        There are 2 versions of the constructor.\n

        1) RemoteDevice(localChannel, name, pathTo, returnPath). Use this version when you want to create a new remote device.

        Args:\n
            localChannel (STAR_system.channel.Channel): The channel on which communication with the
                remote device is made. This channel cannot be used for any other
                purpose when a device configuration operation is being performed.
            name (str): The name to be used to identify the remote device.
            pathTo (list of int): Path to the remote device. This should be the
                path to the remote device's configuration port (port 0),
                including a default logical address. This means that the path
                will normally end with 0, 254.
            returnPath (list of int): Return path fom the remote device to
                reach the local channel. Configuration response packets are
                automatically sent out of the port on which the command is
                received, so this port number is not required. The path should
                also be terminated with a default logical address. This means
                that returnPath is normally one byte shorter than pathTo and
                ends with 254.

        2) RemoteDevice(deviceID). This version of the constructor is used internally when the remote device has already been created.

        Args:\n
            deviceID (int): The ID of the remote device.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                The wrong number of arguments was passed.\n
                Any argument was of the wrong type.\n
            ValueError:\n
                deviceID was negative.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if len(args) == 1:
            deviceID = args[0]

            if type(deviceID) != int:
                raise TypeError("deviceID must be int.")
            if deviceID < 0:
                raise ValueError("deviceID cannot be negative.")

            self.deviceID = deviceID
        
        elif len(args) == 4:
            localChannel = args[0]
            name = args[1]
            pathTo = args[2]
            returnPath = args[3]

            if isinstance(localChannel, Channel) is False:
                raise TypeError("localChannel must be an instance of Channel.")
            if type(name) != str:
                raise TypeError("name must be str.")
            if isinstance(pathTo, list) is False:
                raise TypeError("pathTo must be a list of ints.")
            if isinstance(returnPath, list) is False:
                raise TypeError("returnPath must be a list of ints.")
            for i in pathTo:
                if type(i) != int:
                    raise TypeError("pathTo must be a list of ints.")
            for i in returnPath:
                if type(i) != int:
                    raise TypeError("returnPath must be a list of ints.")

            localDeviceID = localChannel.owningDeviceID
            localChannelNumber = localChannel.channelNumber
            nameBytes = name.encode('utf-8')

            # Create an array that holds the path bytes
            pathToArray = (c_uint8 * len(pathTo))()

            # Assign values of the array
            for i in range(len(pathTo)):
                pathToArray[i] = pathTo[i]

            # Cast it to pointer
            pPathTo = cast(pathToArray, c_void_p)

            pathLength = c_uint16(len(pathTo))
            pathToAddress = STAR_SPACEWIRE_ADDRESS(pPathTo, pathLength)
            pPathToAddress = pointer(pathToAddress)

            # Create an array that holds the return path bytes
            returnPathArray = (c_uint8 * len(returnPath))()

            # Assign values of the array
            for i in range(len(returnPath)):
                returnPathArray[i] = returnPath[i]

            # Cast it to pointer
            pReturnPath = cast(returnPathArray, c_void_p)

            pathLength = c_uint16(len(returnPath))
            returnPathAddress = STAR_SPACEWIRE_ADDRESS(pReturnPath, pathLength)
            pReturnPathAddress = pointer(returnPathAddress)

            # Set argument types and return type of the C function
            star_lib.STAR_CFG_createRemoteDeviceIdentifier.argtypes = [c_uint32, c_uint8, c_char_p,
                                                                       POINTER(STAR_SPACEWIRE_ADDRESS),
                                                                       POINTER(STAR_SPACEWIRE_ADDRESS)]
            star_lib.STAR_CFG_createRemoteDeviceIdentifier.restype = c_uint32

            self.deviceID = star_lib.STAR_CFG_createRemoteDeviceIdentifier(c_uint32(localDeviceID),
                                                                           c_uint8(localChannelNumber),
                                                                           nameBytes, pPathToAddress,
                                                                           pReturnPathAddress)

        else:
            raise TypeError("RemoteDevice() takes either 1 or 4 arguments.")

    def __del__(self):

        # Make sure to protect against invalid STAR-API library
        if star_lib is not None:

            # Set argument types and return type of the C function
            star_lib.STAR_CFG_destroyRemoteDeviceIdentifier.argtypes = [c_uint32]
            star_lib.STAR_CFG_destroyRemoteDeviceIdentifier.restype = c_int32

            star_lib.STAR_CFG_destroyRemoteDeviceIdentifier(c_uint32(self.deviceID))

    def getDeviceType(self) -> str:
        """Gets and returns the type of the remote device.\n
        This method gets the device type using `STAR_system.device_config.DeviceConfig.getDeviceIdentificationInfo`.\n

        `STAR_system.device.Device.getDeviceType` is not compatible with remote types.\n

        This method gets the same information as `STAR_system.device.Device.getDeviceType` but in a different way,
        enabling remote devices to be used in some situations where a local device is expected.\n

        Raises:\n
            STARAPIError:\n
                Error raised by getDeviceIdentificationInfo().\n
            TypeError:\n
                Error raised by getDeviceIdentificationInfo().\n
            ValueError:\n
                Error raised by getDeviceIdentificationInfo().\n
        """

        try:
            deviceInfo = self.getDeviceIdentificationInfo()
        except (STARAPIError, TypeError, ValueError):
            raise

        return deviceInfo.deviceType

    def getRemoteDeviceName(self) -> str:
        """Gets and returns the name of the remote device.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_getRemoteDeviceDescriptionNameString.argtypes = [c_uint32]
        star_lib.STAR_CFG_getRemoteDeviceDescriptionNameString.restype = c_char_p

        name = star_lib.STAR_CFG_getRemoteDeviceDescriptionNameString(c_uint32(self.deviceID))

        return name.decode('utf-8')

    def getRemoteDeviceLocalChannel(self) -> Channel:
        """Gets and returns the local device `STAR_system.channel.Channel` used to communicate with the remote device.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Could not get remote device local channel.\n
                Could not get remote device local device.\n
            TypeError:\n
                Errors raised by Channel class.\n
            ValueError:\n
                Errors raised by Channel class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int that will be used as a parameter for the C library function call
        channelNumber = c_uint8(0)
        pChannelNumber = pointer(channelNumber)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_getRemoteDeviceLocalChannel.argtypes = [c_uint32, POINTER(c_uint8)]
        star_lib.STAR_CFG_getRemoteDeviceLocalChannel.restype = c_int32

        success = star_lib.STAR_CFG_getRemoteDeviceLocalChannel(c_uint32(self.deviceID), pChannelNumber)

        # Check success
        if success != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Could not get remote device local channel.")

        # Create pointer to int that will be used as a parameter for the C library function call
        deviceID = c_uint32(0)
        pDeviceID = pointer(deviceID)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_getRemoteDeviceLocalDevice.argtypes = [c_uint32, POINTER(c_uint32)]
        star_lib.STAR_CFG_getRemoteDeviceLocalDevice.restype = c_int32

        success = star_lib.STAR_CFG_getRemoteDeviceLocalDevice(c_uint32(self.deviceID), pDeviceID)

        if success != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Could not get remote device local device.")

        # Create the channel object
        try:
            channel = Channel(channelNumber.value, deviceID.value)
        except (STARAPIError, TypeError, ValueError):
            raise

        return channel

    def getRemoteDeviceLocalDevice(self) -> Device:
        """Gets and returns the local device used to communicate with the remote device.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Device object could not be created.\n
            TypeError:\n
                Device object could not be created.\n
            ValueError:\n
                Device object could not be created.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int that will be used as a parameter for the C library function call
        deviceID = c_uint32(0)
        pDeviceID = pointer(deviceID)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_getRemoteDeviceLocalDevice.argtypes = [c_uint32, POINTER(c_uint32)]
        star_lib.STAR_CFG_getRemoteDeviceLocalDevice.restype = c_int32

        success = star_lib.STAR_CFG_getRemoteDeviceLocalDevice(c_uint32(self.deviceID), pDeviceID)

        if success == STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            try:
                device = Device(deviceID.value)
                return device
            except (STARAPIError, TypeError, ValueError):
                raise
        else:
            raise STARAPIError("Could not create Device object.")

    def getRemoteDevicePath(self) -> int:
        """Gets and returns the path to the remote device. The path is in the form of
        a list of ints.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Could not get remote device path.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to pointer structure that will be used as a parameter for the C library function call
        addressStruct = STAR_SPACEWIRE_ADDRESS()
        pAddressStruct = pointer(addressStruct)
        ppAddressStruct = pointer(pAddressStruct)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_getRemoteDevicePath.argtypes = [c_uint32, POINTER(POINTER(STAR_SPACEWIRE_ADDRESS))]
        star_lib.STAR_CFG_getRemoteDevicePath.restype = c_int32

        success = star_lib.STAR_CFG_getRemoteDevicePath(c_uint32(self.deviceID), ppAddressStruct)

        if success == STAR_OPERATION_RESULT.STAR_SUCCESS.value:

            # Access the structure's contents (through pointer to pointer)
            addressStruct = ppAddressStruct.contents.contents

            # Cast to unsigned char pointer
            pPath = cast(addressStruct.pPath, POINTER(c_uint8))

            path = []
            for i in range(addressStruct.pathLength):
                byte = pPath[i]
                path.append(byte)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyAddress.argtypes = [POINTER(STAR_SPACEWIRE_ADDRESS)]
            star_lib.STAR_destroyAddress.restype = None
            star_lib.STAR_destroyAddress(pAddressStruct)

            return path
        else:
            raise STARAPIError("Getting remote device path failed.")

    def getRemoteDeviceReturnPath(self) -> list:
        """Gets and returns the return path from the remote device. The return path is in the form of
        a list of ints.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Could not get remote device return path.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to pointer structure that will be used as a parameter for the C library function call
        addressStruct = STAR_SPACEWIRE_ADDRESS()
        pAddressStruct = pointer(addressStruct)
        ppAddressStruct = pointer(pAddressStruct)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_getRemoteDeviceRetPath.argtypes = [c_uint32, POINTER(POINTER(STAR_SPACEWIRE_ADDRESS))]
        star_lib.STAR_CFG_getRemoteDeviceRetPath.restype = c_int32

        success = star_lib.STAR_CFG_getRemoteDeviceRetPath(c_uint32(self.deviceID), ppAddressStruct)

        if success == STAR_OPERATION_RESULT.STAR_SUCCESS.value:

            addressStruct = ppAddressStruct.contents.contents

            pPath = cast(addressStruct.pPath, POINTER(c_uint8))
            path = []
            for i in range(addressStruct.pathLength):
                byte = pPath[i]
                path.append(byte)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyAddress.argtypes = [POINTER(STAR_SPACEWIRE_ADDRESS)]
            star_lib.STAR_destroyAddress.restype = None

            star_lib.STAR_destroyAddress(pAddressStruct)

            return path
        else:
            raise STARAPIError("Could not get remote device return path.")
    


