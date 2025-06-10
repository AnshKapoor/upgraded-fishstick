"""Represents a driver.

Brief:\n
    Represents a driver.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
import types
from ctypes import *

from gspy_egse.gui.STAR_system.channel_listener import ChannelListener
from gspy_egse.gui.STAR_system.device_listener import DeviceListener

from gspy_egse.gui.STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.STAR_structures import STAR_VERSION_INFO
from gspy_egse.gui.STAR_system.STAR_structure_classes import VersionInformation
from gspy_egse.gui.STAR_system.STAR_enums import STAR_DRIVER_TYPE

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


class Driver(object):
    """Represents a device driver.

    Attributes:\n
        driverID (int): The ID of this driver.
    """

    def __init__(self, driverID):
        """Constructor:\n
            Initialises a `STAR_system.driver.Driver` object.

        Args:\n
            driverID (int): The ID of the driver.

        Raises:\n
            TypeError:\n
                driverID is not an int.\n
            ValueError:\n
                driverID is negative.\n
        """

        if type(driverID) != int:
            raise TypeError("driverID must be int.")
        if driverID < 0:
            raise ValueError("driverID cannot be negative.")

        self.driverID = driverID

        self._channelListener = None
        self._deviceListener = None

    def registerChannelListener(self, callback, contextObject=None, notifyForCurrent=False):
        """Registers a call-back function that will be called whenever a channel is opened or closed on a device which has this driver.\n

        The channel listener instance is saved within this class (as class member/field).\n

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
                contextInfo is optional context information that can be passed to the function.\n
                All of these arguments are ints which are automatically passed to the function when it is called.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.\n
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
            channelListener = ChannelListener(callback=callback, driverID=self.driverID,
                                              contextObject=contextObject, notifyForCurrent=notifyForCurrent)
        except (STARAPIError, TypeError, ValueError):
            raise

        self._channelListener = channelListener

    def unregisterChannelListener(self):
        """Unregisters a call-back function that will be called whenever a channel
        is opened or closed in a device related to this driver.

        Raises:\n
            STARAPIError:\n
                Channel listener could not be unregistered.\n
        """

        if self._channelListener is not None and isinstance(self._channelListener, ChannelListener) is True:

            # Call unregister method on the driver
            try:
                self._channelListener.unregister()
            except STARAPIError:
                raise

            # Set the device listener instance is None
            self._channelListener = None

    def registerDeviceListener(self, callback, contextObject=None, notifyForCurrent=False):
        """Registers a call-back function that will be called when a device with this driver is added or removed.\n

        The device listener instance is saved within this class (as class member/field).\n

        Args:
            callback (function): The call-back function can have no arguments or the following signature\n
                callback(deviceListenerIdentifier, driverIdentifier, deviceIdentifier, deviceAdded, contextInfo)\n
                where\n
                deviceListenerIdentifier is the device listener that this event corresponds to.\n
                driverIdentifier is the driver on which the device was added or removed.\n
                deviceIdentifier is the device which was added or removed.\n
                deviceAdded is whether the device has been added (1) or removed (0).\n
                contextObject is context information that can be passed to the function.\n
                All of these arguments are ints which are automatically passed to the function when it is called.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.\n
            notifyForCurrent (bool): Whether the function should be called for
                all existing devices to indicate that they've been added. Default value is False.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Failed to register call-back function.\n
            TypeError:\n
                callback is not a function.\n
                notifyForCurrent is not bool.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType) is False:
            raise TypeError("callback must be a function.")
        if type(notifyForCurrent) != bool:
            raise TypeError("notifyForCurrent must be bool.")

        try:
            deviceListener = DeviceListener(callback=callback, driverID=self.driverID, contextObject=contextObject)
        except (STARAPIError, TypeError, ValueError):
            raise

        self._deviceListener = deviceListener

    def unregisterDeviceListener(self):
        """Unregisters a call-back function that will be called whenever a device with this driver is added or removed.\n

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

    def getDeviceIDListForDriver(self) -> list:
        """Gets and returns a list of device IDs for the driver.

        Returns an empty list if no devices are present.

        This method returns a snapshot of the current state of the system
        and it is not automatically updated.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to be used in the C function call as parameter
        deviceCount = c_uint32(0)
        pDeviceCount = pointer(deviceCount)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceListForDriver.argtypes = [c_uint32, POINTER(c_uint32)]
        star_lib.STAR_getDeviceListForDriver.restype = POINTER(c_uint32)

        deviceIDArray = star_lib.STAR_getDeviceListForDriver(c_uint32(self.driverID), pDeviceCount)

        # Check for null pointer
        if deviceIDArray:
            deviceIDs = []

            for i in range(deviceCount.value):
                deviceIDs.append(deviceIDArray[i])

            # Set argument types and return type of the C function
            star_lib.STAR_destroyDeviceList.argtypes = [POINTER(c_uint32)]
            star_lib.STAR_destroyDeviceList.restype = None

            star_lib.STAR_destroyDeviceList(deviceIDArray)

            return deviceIDs
        else:
            return []

    def getDriverType(self) -> STAR_DRIVER_TYPE:
        """Gets and returns the driver's type.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDriverType.argtypes = [c_uint32]
        star_lib.STAR_getDriverType.restype = STAR_DRIVER_TYPE

        driverType = star_lib.STAR_getDriverType(c_uint32(self.driverID))

        return driverType

    def getDriverVersion(self) -> VersionInformation:
        """Gets and returns the version of the driver. The version is returned in the form of
        a `STAR_system.STAR_structure_classes.VersionInformation` object.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The C API returned a null pointer to version information.\n
            TypeError:\n
                Errors from VersionInformation class.\n
            ValueError:\n
                Errors from VersionInformation class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getDriverVersion.argtypes = [c_uint32]
        star_lib.STAR_getDriverVersion.restype = POINTER(STAR_VERSION_INFO)

        pVersionStruct = star_lib.STAR_getDriverVersion(c_uint32(self.driverID))

        # Check for null pointer
        if pVersionStruct:
            versionStruct = pVersionStruct.contents

            try:
                versionObj = VersionInformation(versionStruct.name.decode('utf-8'), versionStruct.author.decode('utf-8'),
                                                versionStruct.major, versionStruct.minor, versionStruct.edit,
                                                versionStruct.patch)
            except (TypeError, ValueError):
                raise

            # Set argument types and return type of the C function
            star_lib.STAR_destroyVersionInfo.argtypes = [POINTER(STAR_VERSION_INFO)]
            star_lib.STAR_destroyVersionInfo.restype = None

            star_lib.STAR_destroyVersionInfo(pVersionStruct)

            return versionObj
        else:
            raise STARAPIError("Error getting driver version information.")

    def isVirtualDriver(self):
        """Gets whether or not this Driver is virtual.
        Returns True if this Driver is virtual, False otherwise.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_isDriverVirtual.argtypes = [c_uint32]
        star_lib.STAR_isDriverVirtual.restype = c_int32

        isVirtual = star_lib.STAR_isDriverVirtual(c_uint32(self.driverID))
        return bool(isVirtual)

