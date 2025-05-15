"""Represents a locally connected device (e.g. via USB or PCI).

Brief:\n
    Represents a locally connected device (e.g. via USB or PCI).

Copyright:\n
    2022 STAR-Dundee Ltd
"""
import os
import types

from ctypes import *

from STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from STAR_system.channel import Channel
from STAR_system.driver import Driver
from STAR_system.channel_listener import ChannelListener
from STAR_system.device_config import DeviceConfig
from STAR_system.device_listener import DeviceListener
from STAR_system.STAR_enums import STAR_OPERATION_RESULT, STAR_BUS_TYPE, STAR_DEVICE_TYPE
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_structures import STAR_VERSION_INFO
from STAR_system.STAR_structure_classes import VersionInformation

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


class Device(DeviceConfig):
    """Represents a locally connected device (e.g. via USB or PCI).

    Attributes:\n
        deviceID (int): The ID of the device.
    """

    def __init__(self, deviceID):
        super().__init__(deviceID)

        self._channelListener = None
        self._deviceListener = None

    def resetName(self):
        """Resets the device's name to its default value.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                The device's name was not successfully reset.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_resetDeviceName.argtypes = [c_uint32]
        star_lib.STAR_resetDeviceName.restype = c_int32

        status = star_lib.STAR_resetDeviceName(c_uint32(self.deviceID))

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Unable to reset device's name.")

    def getDeviceTxRxCapabilities(self) -> bool:
        """Determine whether the device is capable of transmitting and receiving
        packets on channels.

        Returns True if the device can transmit and receive packets, False otherwise.

        This method can be used to determine whether a device can be used to route
        packets over channels and in and out of the device's SpaceWire links, or
        whether it is a special device such as a Link Analyser or Conformance
        Tester which cannot route packets.

        Note that some devices, such as the EGSE may be capable of transmitting and
        receiving packets, but a value of False will be returned, as these devices
        do not simple route any packets transmitted or received on channels, and
        must be specially configured to transmit or receive packets.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API failed to get transmit/receive capabilities.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceTxRxCapabilities.argtypes = [c_uint32]
        star_lib.STAR_getDeviceTxRxCapabilities.restype = c_uint32

        txRxCapabilities = star_lib.STAR_getDeviceTxRxCapabilities(c_uint32(self.deviceID))

        if txRxCapabilities == STAR_DEVICE_TYPE.STAR_DEVICE_TX_RX_SUPPORTED:
            return True
        elif txRxCapabilities == STAR_DEVICE_TYPE.STAR_DEVICE_TX_RX_NOT_SUPPORTED:
            return False
        else:
            raise STARAPIError("Failed to get transmit/receive capabilities.")
        
    def getDeviceConfigCapabilities(self) -> bool:
        """Determine whether the device is capable of being configured.

        Returns True if the device is capable of being configured, False otherwise.

        This method can be used to determine whether a device can be configured using the 
        Configuration APIs, or whether it is a special device such as a Link Analyser or a
        Conformance Tester which does not have a router with a configuration port.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API was unable to determine the device configuration capabilities.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceConfigCapabilities.argtypes = [c_uint32]
        star_lib.STAR_getDeviceConfigCapabilities.restype = c_uint32

        configSupported = star_lib.STAR_getDeviceConfigCapabilities(c_uint32(self.deviceID))

        if configSupported == STAR_DEVICE_TYPE.STAR_DEVICE_CONFIG_SUPPORTED:
            return True
        elif configSupported == STAR_DEVICE_TYPE.STAR_DEVICE_CONFIG_NOT_SUPPORTED:
            return False
        else:
            raise STARAPIError("C API failed to get device config capabilities.")

    def registerChannelListener(self, callback, contextObject=None, notifyForCurrent=False):
        """Registers a call-back function that will be called whenever a channel
        on the device is opened or closed.\n

        A reference to the created ChannelListener object is saved in this class (the Device instance).\n

        Args:\n
            callback (function): The call-back function can either have no arguments or the following signature\n
                callback_name(channelListenerIdentifier, driverIdentifier, deviceIdentifier, channelIdentifier,
                              channelOpened, channelNumber, contextObject)\n
                where \n
                channelListenerIdentifier is the channel listener that the event corresponds to.\n
                driverIdentifier is the driver of the device on which the channel was opened or closed.\n
                deviceIdentifier is the device on which the channel was opened or closed.\n
                channelIdentifier is the identifier of the channel which has been opened or closed.\n
                channelOpened is whether the channel was opened (1) or closed (0).\n
                channelNumber is the channel number on the device of the channel which was opened or closed.\n
                contextObject is optional context information that can be passed to the function.\n
                All of these arguments are ints which are automatically passed to the function when it is called.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.
            notifyForCurrent (bool): Whether the function should be called for
                all existing channels to indicate that they've been opened. Default value is False.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Failed to register callback.\n
            TypeError:\n
                callback is not a function.\n
                notifyForCurrent is not bool.\n
                Errors from ChannelListener class.\n
            ValueError:\n
                Errors from ChannelListener class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType) is False:
            raise TypeError("callback must be a function.")
        if type(notifyForCurrent) != bool:
            raise TypeError("notifyForCurrent must be bool.")

        try:
            channelListener = ChannelListener(callback=callback, deviceID=self.deviceID,
                                            contextObject=contextObject, notifyForCurrent=notifyForCurrent)
        except (STARAPIError, TypeError, ValueError):
            raise

        self._channelListener = channelListener

    def unregisterChannelListener(self):
        """Unregisters a call-back function that will be called whenever a channel
        on the device is opened or closed.

        Raises:\n
            STARAPIError:\n
                Channel listener could not be unregistered.\n
        """

        if self._channelListener is not None and isinstance(self._channelListener, ChannelListener) is True:

            # Call unregister method on the device listener object
            try:
                self._channelListener.unregister()
            except STARAPIError:
                raise

            # Set the device listener instance is None
            self._channelListener = None

    def registerDeviceListener(self, callback, contextObject=None):
        """Registers a call-back function that will be called whenever the device is removed.

        Args:\n
            callback (function): The call-back function can have no arguments or the following signature\n
                callback(deviceListenerIdentifier, driverIdentifier, deviceIdentifier, deviceAdded, contextObject)\n
                where\n
                deviceListenerIdentifier is the device listener that this event corresponds to.\n
                driverIdentifier is the driver on which the device was added or removed.\n
                deviceIdentifier is the device which was added or removed.\n
                deviceAdded is whether the device has been added (1) or removed (0).\n
                contextObject is context information that can be passed to the function.\n
                All of these arguments are ints  which are automatically passed to the function when it is called.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                Failed to register call-back function.\n
                Failed to create device listener object.
            TypeError:\n
                callback is not a function.\n
                Errors from DeviceListener class.\n
            ValueError:\n
                Errors from DeviceListener class.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType) is False:
            raise TypeError("callback must be a function.")

        try:
            deviceListener = DeviceListener(callback=callback, deviceID=self.deviceID, contextObject=contextObject)
        except (STARAPIError, TypeError, ValueError):
            raise

        # Save the transfer completion listener
        self._deviceListener = deviceListener

    def unregisterDeviceListener(self):
        """Unregisters a call-back function that will be called whenever the device is removed.

        Raises:\n
            STARAPIError:\n
                Device listener could not be unregistered.\n
        """

        if self._deviceListener is not None and isinstance(self._deviceListener, DeviceListener) is True:

            # Call unregister method on the device listener object
            try:
                self._deviceListener.unregister()
            except STARAPIError:
                raise

            # Set the device listener instance is None
            self._deviceListener = None

    def getBusType(self) -> STAR_BUS_TYPE:
        """Gets and returns the bus type for the device.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceBusType.argtypes = [c_uint32]
        star_lib.STAR_getDeviceBusType.restype = STAR_BUS_TYPE

        bus_type = star_lib.STAR_getDeviceBusType(c_uint32(self.deviceID))

        return bus_type

    def getChannels(self) -> list:
        """Gets and returns a list of channels present on the device.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceChannels.argtypes = [c_uint32]
        star_lib.STAR_getDeviceChannels.restype = c_uint32

        channelsMask = star_lib.STAR_getDeviceChannels(c_uint32(self.deviceID))

        # The first 2 chars are 0b, so they are removed.
        binaryString = bin(channelsMask)[2:]

        channels = []
        for channelNumber in range(len(binaryString)):
            bit = binaryString[channelNumber]

            if int(bit):

                # Create the channel object
                try:
                    channel = Channel(channelNumber, self.deviceID)
                except (STARAPIError, TypeError, ValueError):
                    channel = None

                # Add this channel to the list of channels
                if channel is not None:
                    channels.append(channel)

        return channels

    def getDeviceDriver(self) -> Driver:
        """Gets the device's driver.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                There is no device attached.\n
            TypeError:\n
                Errors from Driver class.\n
            ValueError:\n
                Errors from Driver class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceDriver.argtypes = [c_uint32]
        star_lib.STAR_getDeviceDriver.restype = c_uint32

        driverID = star_lib.STAR_getDeviceDriver(c_uint32(self.deviceID))

        if driverID == 0:
            raise STARAPIError("Error getting device driver.")
        else:
            try:
                driver = Driver(driverID)
                return driver
            except (TypeError, ValueError):
                raise

    def getFirmwareVersion(self) -> VersionInformation:
        """Gets and returns the version of the device's firmware.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API returned a null pointer to the version information struct, or no device is attached.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceFirmwareVersion.argtypes = [c_uint32]
        star_lib.STAR_getDeviceFirmwareVersion.restype = POINTER(STAR_VERSION_INFO)

        pVersionInfoStruct = star_lib.STAR_getDeviceFirmwareVersion(c_uint32(self.deviceID))

        if pVersionInfoStruct:
            versionInfoStruct = pVersionInfoStruct.contents
            versionInfo = VersionInformation(versionInfoStruct.name.decode('utf-8'),
                                             versionInfoStruct.author.decode('utf-8'),
                                             versionInfoStruct.major, versionInfoStruct.minor,
                                             versionInfoStruct.edit, versionInfoStruct.patch)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyVersionInfo.argtypes = [POINTER(STAR_VERSION_INFO)]
            star_lib.STAR_destroyVersionInfo.restype = None

            star_lib.STAR_destroyVersionInfo(pVersionInfoStruct)

            return versionInfo
        else:
            raise STARAPIError("Unable to allocate memory for firmware version data.")

    def getDeviceIndex(self) -> int:
        """Gets and returns the index number of the device.

        This method is provided for backwards compatibility reasons and is not for typical usage.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API function call was unsuccessful.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceIndex.argtypes = [c_uint32]
        star_lib.STAR_getDeviceIndex.restype = c_int32

        index = star_lib.STAR_getDeviceIndex(c_uint32(self.deviceID))

        if index < 0:
            raise STARAPIError("The C API was unable to get the device index.")
        else:
            return index

    def getDeviceName(self) -> str:
        """Gets and returns the name of the device.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API returned a null pointer to the device's name.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceName.argtypes = [c_uint32]
        star_lib.STAR_getDeviceName.restype = c_char_p

        name = star_lib.STAR_getDeviceName(c_uint32(self.deviceID))

        if name:
            nameStr = name.decode('utf-8')
            return nameStr
        else:
            raise STARAPIError("C API failed to retrieve device name.")

    def getSerialNumber(self) -> str:
        """Gets and returns the serial number of the device.

        The serial number of a device is a unique alphanumeric identifier.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API returned a null pointer to the device serial number.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceSerialNumber.argtypes = [c_uint32]
        star_lib.STAR_getDeviceSerialNumber.restype = c_char_p

        serialNumber = star_lib.STAR_getDeviceSerialNumber(c_uint32(self.deviceID))

        if serialNumber:
            serialNumberStr = serialNumber.decode('utf-8')
            return serialNumberStr
        else:
            raise STARAPIError("C API failed to retrieve device serial number.")

    def getDeviceType(self) -> STAR_DEVICE_TYPE:
        """Gets and returns the device type.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceType.argtypes = [c_uint32]
        star_lib.STAR_getDeviceType.restype = STAR_DEVICE_TYPE

        device_type = star_lib.STAR_getDeviceType(c_uint32(self.deviceID))
        
        return device_type

    def resetDevice(self):
        """Resets the device.

        This method will raise an error if called with a virtual device's identifier.

        Calling this method while packets are being transmitted and/or received
        can cause the device to get in to a bad state.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API returned an error code.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_resetDevice.argtypes = [c_uint32]
        star_lib.STAR_resetDevice.restype = c_int32

        status = star_lib.STAR_resetDevice(c_uint32(self.deviceID))

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("C API encountered an error resetting the device.")

        self._deviceListener = None
        self._channelListener = None

    def setDeviceName(self, name):
        """Sets the device's name.

        Args:\n
            name (str): The new name for the device. name must be less than 256
                characters. If name is an empty string then the device name is 
                reset to its default value.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                The C API returned an error code.\n
            ValueError:\n
                name was too long.\n
            TypeError:\n
                name was not a string.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(name) != str:
            raise TypeError("name must be str.")

        if len(name) >= 256:
            raise ValueError("name parameter must be less than 256 characters.")

        if name == "":
            name = None
        else:
            name = name.encode('utf-8')

        # Set argument types and return type of the C function
        star_lib.STAR_setDeviceName.argtypes = [c_uint32, c_char_p]
        star_lib.STAR_setDeviceName.restype = c_int32

        status = star_lib.STAR_setDeviceName(c_uint32(self.deviceID), name)

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Failed to set device name.")

    def isVirtualDevice(self) -> bool:
        """Gets whether or not the device is a virtual device.\n

        Returns True if the device is virtual, False otherwise. False will be returned if no device is connected.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_isDeviceVirtual.argtypes = [c_uint32]
        star_lib.STAR_isDeviceVirtual.restype = c_int32

        virtual = star_lib.STAR_isDeviceVirtual(c_uint32(self.deviceID))
        return bool(virtual)
