"""Represents miscellaneous STAR-system functionality.

Brief:\n
    Represents miscellaneous STAR-system functionality.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

import os
import sys

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(module_path)

from ctypes import *

from STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from STAR_system.STAR_structures import STAR_VERSION_INFO
from STAR_system.STAR_structure_classes import VersionInformation
from STAR_system.device import Device
from STAR_system.driver import Driver
from STAR_system.remote_device import RemoteDevice
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_enums import STAR_DEVICE_TYPE

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


class STARSystem(object):
    """Represents miscellaneous STAR-system functionality such as getting version information."""

    @staticmethod
    def getRemoteDeviceDescriptionList() -> list:
        """Gets a list of all remote devices that have been created by all processes.

        This method returns a snapshot of the current state of the system and is
        not automatically updated.

        Returns a list of RemoteDevice objects.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                Errors from RemoteDevice class.\n
            ValueError:\n
                Errors from RemoteDevice class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int that will be passed in as parameter into the C library function
        count = c_uint32(0)
        pCount = pointer(count)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_getRemoteDeviceDescriptionList.argtypes = [POINTER(c_uint32)]
        star_lib.STAR_CFG_getRemoteDeviceDescriptionList.restype = POINTER(c_uint32)

        remoteDevicesArray = star_lib.STAR_CFG_getRemoteDeviceDescriptionList(pCount)

        remoteDevices = []
        for i in range(count.value):
            remoteDeviceID = remoteDevicesArray[i]

            try:
                remoteDevice = RemoteDevice(remoteDeviceID)
            except (STARAPIError, TypeError, ValueError):
                raise

            remoteDevices.append(remoteDevice)

        # Set argument types and return type of the C function
        star_lib.STAR_CFG_destroyRemoteDeviceDescriptionList.argtypes = [POINTER(c_uint32)]
        star_lib.STAR_CFG_destroyRemoteDeviceDescriptionList.restype = None

        star_lib.STAR_CFG_destroyRemoteDeviceDescriptionList(remoteDevicesArray)

        return remoteDevices

    @staticmethod
    def getDeviceListForType(deviceType) -> list:
        """Gets an array of all devices present for the given device type.

        The device type may be the the type of a specific device,
        e.g. `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_BRICK_MK3`, or it may be one of the special device types,
        `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_TX_RX_SUPPORTED`, `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_TX_RX_NOT_SUPPORTED`
        or `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_ALL` to get all devices.

        This method returns a snapshot of the current state of the system and is not automatically updated.

        Returns a list of Device objects (created for devices that are present for the specified device type).

        Args:\n
            deviceType (STAR_system.STAR_enums.STAR_DEVICE_TYPE): The device type to get the list for.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                deviceType was not STAR_DEVICE_TYPE.\n
                Errors from Device class.\n
            ValueError:\n
                deviceType was not valid.\n
                Errors from Device class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(deviceType, STAR_DEVICE_TYPE) is False:
            raise TypeError("deviceType must be STAR_DEVICE_TYPE.")

        # Create pointer to int that will be passed in as parameter into the C library function
        deviceCount = c_uint32(0)
        pDeviceCount = pointer(deviceCount)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceListForType.argtypes = [c_uint32, POINTER(c_uint32)]
        star_lib.STAR_getDeviceListForType.restype = POINTER(c_uint32)

        deviceArray = star_lib.STAR_getDeviceListForType(c_uint32(deviceType.value), pDeviceCount)

        devices = []

        if deviceArray:
            for i in range(deviceCount.value):

                try:
                    newDevice = Device(deviceArray[i])
                except (STARAPIError, TypeError, ValueError):
                    raise

                devices.append(newDevice)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyDeviceList.argtypes = [POINTER(c_uint32)]
            star_lib.STAR_destroyDeviceList.restype = None

            star_lib.STAR_destroyDeviceList(deviceArray)

            return devices
        else:
            return [] 

    @staticmethod
    def getDeviceListForTypes(deviceTypes) -> list:
        """Gets a list of all devices present for the given device types in a list.

        Each device type may be the type of a specific device,
        e.g. `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_BRICK_MK3`, or it may be one of the special device types,
        `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_TX_RX_SUPPORTED`, `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_TX_RX_NOT_SUPPORTED`
        or `STAR_system.STAR_enums.STAR_DEVICE_TYPE.STAR_DEVICE_ALL` to get all devices.

        This method returns a snapshot of the current state of the system and is not automatically updated.

        Returns a list of Device objects (created for devices that are present for the specified device types).

        Args:\n
            deviceTypes (list of `STAR_system.STAR_enums.STAR_DEVICE_TYPE`): A list of device types to get the Device list for.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Errors from Device class.\n
            TypeError:\n
                deviceTypes was not list of STAR_DEVICE_TYPE.\n
                Errors from Device class.\n
            ValueError:\n
                At least one element of deviceTypes was an invalid device type.\n
                Errors from Device class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(deviceTypes, list) is False:
            raise TypeError("deviceTypes must be list.")
        for deviceType in deviceTypes:
            if isinstance(deviceType, STAR_DEVICE_TYPE) is False:
                raise TypeError("Each device type must be STAR_DEVICE_TYPE.")

        numOfDeviceTypes = len(deviceTypes)

        # Number of device types in the list
        numRequestedTypes = c_uint32(numOfDeviceTypes)

        # Create pointer to int that will be passed in as parameter into the C library function
        count = c_uint32(0)
        pCount = pointer(count)

        # Create array holding the device types
        deviceTypesArray = (c_uint32 * numOfDeviceTypes)()

        # Assign the values of the array
        for i in range(numOfDeviceTypes):
            deviceTypesArray[i] = deviceTypes[i]

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceListForTypes.argtypes = [type((c_uint32 * numOfDeviceTypes)()), c_uint32,
                                                        POINTER(c_uint32)]
        star_lib.STAR_getDeviceListForTypes.restype = POINTER(c_uint32)

        deviceArray = star_lib.STAR_getDeviceListForTypes(deviceTypesArray, numRequestedTypes, pCount)

        devices = []
        if deviceArray:
            for i in range(count.value):

                try:
                    newDevice = Device(deviceArray[i])
                except (STARAPIError, TypeError, ValueError):
                    raise

                devices.append(newDevice)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyDeviceList.argtypes = [POINTER(c_uint32)]
            star_lib.STAR_destroyDeviceList.restype = None

            star_lib.STAR_destroyDeviceList(deviceArray)

            return devices
        else:
            return []

    @staticmethod
    def getDeviceList() -> list:
        """Gets and returns a list of devices connected to the system for all drivers. If no devices are attached,
            an empty list is returned.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Errors from Device class.\n
            TypeError:\n
                Errors from Device class.\n
            ValueError:\n
                Errors from Device class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int that will be passed in as parameter into the C library function
        deviceCount = c_uint32(0)
        pDeviceCount = pointer(deviceCount)

        # Set argument types and return type of the C function
        star_lib.STAR_getDeviceList.argtypes = [POINTER(c_uint32)]
        star_lib.STAR_getDeviceList.restype = POINTER(c_uint32)

        deviceArray = star_lib.STAR_getDeviceList(pDeviceCount)

        devices = []

        # Check for null pointer
        if deviceArray:
            for i in range(deviceCount.value):

                try:
                    newDevice = Device(deviceArray[i])
                except (STARAPIError, TypeError, ValueError):
                    raise

                devices.append(newDevice)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyDeviceList.argtypes = [POINTER(c_uint32)]
            star_lib.STAR_destroyDeviceList.restype = None

            star_lib.STAR_destroyDeviceList(deviceArray)

            return devices
        else:
            return []

    @staticmethod
    def getDriverList(physicalDrivers, virtualDrivers) -> list:
        """Gets and returns a list of Drivers for all drivers of the requested type(s). If there are no drivers,
                returns an empty list.

        Args:\n
            physicalDrivers (bool): If True, physical drivers will be included
                in the returned Driver list.
            virtualDrivers (bool): If True, virtual drivers will be included
                in the returned Driver list.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                Input parameter was not bool.\n
                Errors from Driver class.\n
            ValueError:\n
                Errors from Driver class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(physicalDrivers) != bool:
            raise TypeError("physicalDrivers must be bool.")

        if type(virtualDrivers) != bool:
            raise TypeError("virtualDrivers must be bool.")

        # Create pointer to int that will be passed in as parameter into the C library function
        driverCount = c_uint32(0)
        pDriverCount = pointer(driverCount)

        # Set argument types and return type of the C function
        star_lib.STAR_getDriverList.argtypes = [c_int32, c_int32, POINTER(c_uint32)]
        star_lib.STAR_getDriverList.restype = POINTER(c_uint32)

        driverArray = star_lib.STAR_getDriverList(c_int32(physicalDrivers), c_int32(virtualDrivers),
                                                  pDriverCount)

        # Check for null pointer
        if driverArray:
            drivers = []
            for i in range(driverCount.value):

                try:
                    driver = Driver(driverArray[i])
                except (TypeError, ValueError):
                    raise

                drivers.append(driver)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyDriverList.argtypes = [POINTER(c_uint32)]
            star_lib.STAR_destroyDriverList.restype = None

            star_lib.STAR_destroyDriverList(driverArray)

            return drivers
        else:
            return []

    @staticmethod
    def getAllVersions() -> list:
        """Gets and returns a list of version information objects for all modules of STAR-System.

        This method returns a snapshot of the current state of the system and is not automatically updated.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Error getting version information.\n
            TypeError:\n
                Errors from VersionInformation class.\n
            ValueError:\n
                Errors from VersionInformation class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int that will be passed in as parameter into the C library function
        count = c_uint32(0)
        pCount = pointer(count)

        # Set argument types and return type of the C function
        star_lib.STAR_getAllVersions.argtypes = [POINTER(c_uint32)]
        star_lib.STAR_getAllVersions.restype = POINTER(STAR_VERSION_INFO)

        versionsArray = star_lib.STAR_getAllVersions(pCount)

        versionsList = []
        
        if count != 0:

            # Iterate through versionsArray
            for i in range(count.value):
                
                versionStruct = versionsArray[i]

                try:
                    versionObj = VersionInformation(versionStruct.name.decode('utf-8'),
                                                    versionStruct.author.decode('utf-8'),
                                                    versionStruct.major, versionStruct.minor,
                                                    versionStruct.edit, versionStruct.patch)

                except (TypeError, ValueError):
                    raise

                versionsList.append(versionObj)

            # Set argument types and return type of the C function
            star_lib.STAR_destroyVersionInfoList.argtypes = [POINTER(STAR_VERSION_INFO)]
            star_lib.STAR_destroyVersionInfoList.restype = None

            star_lib.STAR_destroyVersionInfoList(versionsArray)

            return versionsList

        else:
            raise STARAPIError("Error getting version information.")

    @staticmethod
    def getApiVersion() -> VersionInformation:
        """Gets and returns the version of STAR-API in the form of a `STAR_system.STAR_structure_classes.VersionInformation` object.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                C API failed to get API version information.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getApiVersion.argtypes = []
        star_lib.STAR_getApiVersion.restype = POINTER(STAR_VERSION_INFO)

        pApiVersionStruct = star_lib.STAR_getApiVersion()

        if pApiVersionStruct:
            apiVersionStruct = pApiVersionStruct.contents

            try:
                apiVersion = VersionInformation(apiVersionStruct.name.decode('utf-8'),
                                                apiVersionStruct.author.decode('utf-8'),
                                                apiVersionStruct.major, apiVersionStruct.minor,
                                                apiVersionStruct.edit, apiVersionStruct.patch)
            except (TypeError, ValueError):
                raise

            # Set argument types and return type of the C function
            star_lib.STAR_destroyVersionInfo.argtypes = [POINTER(STAR_VERSION_INFO)]
            star_lib.STAR_destroyVersionInfo.restype = None

            star_lib.STAR_destroyVersionInfo(pApiVersionStruct)

            return apiVersion

        else:
            raise STARAPIError("Could not allocate memory for api version data.")


