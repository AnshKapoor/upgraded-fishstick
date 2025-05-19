"""Contains methods for configuring a device.

Brief:\n
    Methods for configuring a device.

Copyright:\n
    2022 STAR-Dundee Ltd
"""
import os
from ctypes import *
from typing import Tuple

from STAR_system import CONFIG_LIB, STAR_CONFIG_API_LIB_LOAD_ERROR_STR
from STAR_system.port import Port
from STAR_system.STAR_exceptions import STARAPIError, StatusCode
from STAR_system.STAR_structure_classes import HardwareInfo, DeviceIdentifierInformation, NetworkDiscoveryInformation,\
                                               RoutingTableEntry, RouterGlobalState
from STAR_system.STAR_structures import STAR_CFG_FPGA_INFO, STAR_CFG_DEVICE_IDENTIFIER_INFO, STAR_CFG_NETWORK_DISCOVERY_INFO,\
                                        STAR_CFG_GAR_ENTRY, STAR_CFG_ROUTER_GLOBAL_STATE
from STAR_system.STAR_enums import STAR_CONFIG_OP_RESULT, STAR_CFG_DEVICE_TYPE, STAR_CFG_TIMEOUT_MODE, STAR_CFG_PORT_TIMEOUT,\
                                   STAR_OPERATION_RESULT, STAR_CFG_BRICK_MK3_PULSE_FREQ, STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD

# Load C API
systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    try:
        config_lib = windll.LoadLibrary(CONFIG_LIB)
    except Exception:
        config_lib = None
        print(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

elif systemType == "posix":
    try:
        config_lib = cdll.LoadLibrary(CONFIG_LIB)
    except Exception:
        config_lib = None
        print(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

StatusCodes = StatusCode()

class DeviceConfig(object):
    """Methods for configuring a device.
    
    These methods are used by the `STAR_system.device.Device` subclass.\n
    Instances of `STAR_system.device_config.DeviceConfig` should not need to be created in normal use.
    """

    def __init__(self, deviceID):
        """Constructor:\n
            Initialises the `STAR_system.device.Device`.

        Args:\n
            deviceID (int): The ID of the device. 

        Raises:\n
            TypeError:\n
                deviceID was not int.
            ValueError:\n
                deviceID was negative.
        """
        if type(deviceID) != int:
            raise TypeError("deviceID must be int.")
        if deviceID < 0:
            raise ValueError("deviceID cannot be negative.")

        self.deviceID = deviceID

    def getFPGAInfo(self) -> HardwareInfo:
        """Reads and returns information about the hardware version of a device.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get FPGA info.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to be used in the C function call as parameter
        pInformationStruct = pointer(STAR_CFG_FPGA_INFO())

        # Set argument types and return type of the C function
        config_lib.CFG_getFPGAInfo.argtypes = [c_uint32, POINTER(STAR_CFG_FPGA_INFO)]
        config_lib.CFG_getFPGAInfo.restype = c_int32

        status = config_lib.CFG_getFPGAInfo(c_uint32(self.deviceID), pInformationStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        
        informationStruct = pInformationStruct.contents
        information = HardwareInfo(informationStruct.major, informationStruct.minor,
                                   informationStruct.edit, informationStruct.patch,
                                   informationStruct.year, informationStruct.month,
                                   informationStruct.day, informationStruct.hour,
                                   informationStruct.minute)
        return information
    
    def getFPGAInfoAsString(self) -> Tuple[str, str]:
        """Creates a string representation of the version and build date for the device.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get FPGA info.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to be used in the C function call as parameter
        pInformationStruct = pointer(STAR_CFG_FPGA_INFO())

        # Set argument types and return type of the C function
        config_lib.CFG_getFPGAInfo.argtypes = [c_uint32, POINTER(STAR_CFG_FPGA_INFO)]
        config_lib.CFG_getFPGAInfo.restype = c_int32

        status = config_lib.CFG_getFPGAInfo(c_uint32(self.deviceID), pInformationStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        # Create pointers that will be passed to the C library call function
        version = create_string_buffer(256)
        buildDate = create_string_buffer(256)

        # Set argument types and return type of the C function
        config_lib.CFG_FPGAInfoToString.argtypes = [c_uint32, POINTER(STAR_CFG_FPGA_INFO), c_char_p, c_char_p]
        config_lib.CFG_FPGAInfoToString.restype = None

        config_lib.CFG_FPGAInfoToString(c_uint32(self.deviceID), pInformationStruct, version, buildDate)

        versionAndBuildDate = (version.value.decode('utf-8'), buildDate.value.decode('utf-8'))

        return versionAndBuildDate

    def disableExternalTimeCodeSelection(self):
        """Disables external time-code selection for the device.

        When external time-code selection is disabled and a time-code is
        transmitted from an application, the value specified for the time-code is
        ignored, and the next valid time-code is transmitted by the device.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable external time-code selection.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableExternalTimeCodeSelection.argtypes = [c_uint32]
        config_lib.CFG_disableExternalTimeCodeSelection.restype = c_int32

        status = config_lib.CFG_disableExternalTimeCodeSelection(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableTimeCodeMaster(self):
        """Disables the device as a time-code master.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable the device as a time-code master.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableTimeCodeMaster.argtypes = [c_uint32]
        config_lib.CFG_disableTimeCodeMaster.restype = c_int32

        status = config_lib.CFG_disableTimeCodeMaster(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableExternalTimeCodeSelection(self):
        """Enables external time-code selection for the device.

        When external time-code selection is enabled and a time-code is
        transmitted from an application, the value specified for the time-code
        is used. Note that the time-code will only be transmitted by the device
        if it is the next valid time-code.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable external time-code selection.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableExternalTimeCodeSelection.argtypes = [c_uint32]
        config_lib.CFG_enableExternalTimeCodeSelection.restype = c_int32

        status = config_lib.CFG_enableExternalTimeCodeSelection(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableTimeCodeMaster(self):
        """Enables the device as a time-code master.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable the device as a time-code master.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableTimeCodeMaster.argtypes = [c_uint32]
        config_lib.CFG_enableTimeCodeMaster.restype = c_int32

        status = config_lib.CFG_enableTimeCodeMaster(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getExternalTimeCodeSelectionEnabled(self) -> bool:
        """Gets whether external time-code selection has been enabled for the device.
        Returns True if external time-code selection is enabled, False otherwise.

        When external time-code selection is disabled and a time-code is transmitted
        from an application, the value specified for the time-code is ignored,
        and the next valid time-code is transmitted by the device. When external
        time-code selection is enabled and a time-code is transmitted from an
        application, the value specified for the time-code is used.\n
        Note that the time-code will only be transmitted by the device if it is the next valid time-code.

        This method is compatible with all device types.
        
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether external time-code selection is enabled or not for the device.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int that will be used in the C function call
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getExternalTimeCodeSelectionEnabled.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getExternalTimeCodeSelectionEnabled.restype = c_int32

        status = config_lib.CFG_getExternalTimeCodeSelectionEnabled(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return bool(enabled.value)

    def getTimeCodeMasterEnabled(self) -> bool:
        """Gets whether the device has been enabled as a time-code master.
        Returns True of the device is configured as a time-code master, False otherwise.

        This method is compatible with all device types.
        
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether the device is enabled as a time-code master or not.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int that will be used in the C function call
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimeCodeMasterEnabled.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getTimeCodeMasterEnabled.restype = c_int32

        status = config_lib.CFG_getTimeCodeMasterEnabled(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return bool(enabled.value)

    def getTimeCodePeriod(self) -> int:
        """Gets the period between the time-code master ticks.
        Returns the period in microseconds. It represents the period between time-codes.

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the time-code period.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to unsigned int that will be used in the C function call
        period = c_uint32(0)
        pPeriod = pointer(period)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimeCodePeriod.argtypes = [c_uint32, POINTER(c_uint32)]
        config_lib.CFG_getTimeCodePeriod.restype = c_int32

        status = config_lib.CFG_getTimeCodePeriod(c_uint32(self.deviceID), pPeriod)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return period.value

    def setTimeCodePeriod(self, period):
        """Sets the period between time-code master ticks.

        This method is compatible with all device types.

        Args:\n
            period (int): The period to be set in microseconds.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the time-code period.\n
            TypeError:\n
                period was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(period) != int:
            raise TypeError("Time-code period must be int.")

        # Set argument types and return type of the C function
        config_lib.CFG_setTimeCodePeriod.argtypes = [c_uint32, c_uint32]
        config_lib.CFG_setTimeCodePeriod.restype = c_int32

        status = config_lib.CFG_setTimeCodePeriod(c_uint32(self.deviceID), c_uint32(period))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def identify(self):
        """Flashes the front panel LEDs.

        This can be used to identify the physical device to which a Device object refers to.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to identify the device.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_identify.argtypes = [c_uint32]
        config_lib.CFG_identify.restype = c_int32

        status = config_lib.CFG_identify(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableIdentifySource(self):
        """Disables identification of source ports for interface mode globally.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable the identification of source ports.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableIdentifySource.argtypes = [c_uint32]
        config_lib.CFG_disableIdentifySource.restype = c_int32

        status = config_lib.CFG_disableIdentifySource(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableInterfaceMode(self):
        """Disables interface mode on the device.

        When interface mode is disabled, the device operates in routing mode.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable interface mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableInterfaceMode.argtypes = [c_uint32]
        config_lib.CFG_disableInterfaceMode.restype = c_int32

        status = config_lib.CFG_disableInterfaceMode(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableIdentifySource(self):
        """When identify source is enabled on a port, this function globally enables the
        addition of a leading byte to each received packet indicating which port the
        packet was received on.

        For each source port on which this behaviour is desired, a call to
        `STAR_system.port.Port.enableIdentifySourceOnPort` must be made.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable source port identification.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableIdentifySource.argtypes = [c_uint32]
        config_lib.CFG_enableIdentifySource.restype = c_int32

        status = config_lib.CFG_enableIdentifySource(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableInterfaceMode(self):
        """In interface mode a packet which is received on an external port, from a SpaceWire
        link or from the configuration port will be routed to the port specified by the
        port routing register of the port (set by `STAR_system.port.Port.setPortRoutingAddress`).

        This method is compatible with all device types.

        Note that if you enable interface mode for a remote device, it will no
        longer be able to communicate with its local device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable interface mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableInterfaceMode.argtypes = [c_uint32]
        config_lib.CFG_enableInterfaceMode.restype = c_int32

        status = config_lib.CFG_enableInterfaceMode(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getIdentifySourceEnabled(self) -> bool:
        """Gets whether identify source is enabled.
        Returns True if identify source is enabled on the device, False otherwise.

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether source identification is enabled or not.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create a pointer that will be passed in as a function parameter to the C library function
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getIdentifySourceEnabled.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getIdentifySourceEnabled.restype = c_int32

        status = config_lib.CFG_getIdentifySourceEnabled(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return bool(enabled.value)

    def getInterfaceModeEnabled(self) -> bool:
        """Gets whether interface mode has been enabled on the device.
        Returns True if interface mode is enabled on the device, False otherwise.

        This method is compatible with all device types.
            
        Raises:
            STARAPIError: The STAR-Config API library could not be loaded.
                          The C API failed to determine whether or not interface mode is enabled.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create a pointer that will be passed in as a function parameter to the C library function
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getInterfaceModeEnabled.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getInterfaceModeEnabled.restype = c_int32

        status = config_lib.CFG_getInterfaceModeEnabled(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return bool(enabled.value)

    def _getDeviceIdentificationInfoPointer(self):
        """Helper method which returns a pointer to device identifier information
            for use in DeviceConfig.getDeviceIdentificationInfo() and
            DeviceConfig.getDeviceManufacturerAsString().

            Returns:
                pInformationStruct (ctypes.pointer): object pointing to a 
                    STAR_CFG_DEVICE_IDENTIFIER_INFO structure object containing the requested 
                    data.

            Raises:
                STARAPIError: The STAR-Config API library could not be loaded.
                              The C API failed to get device identification info.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to structure used as input parameter to the C library function
        pInformationStruct = pointer(STAR_CFG_DEVICE_IDENTIFIER_INFO())

        # Set argument types and return type of the C function
        config_lib.CFG_getDeviceIdentificationInfo.argtypes = [c_uint32, POINTER(STAR_CFG_DEVICE_IDENTIFIER_INFO)]
        config_lib.CFG_getDeviceIdentificationInfo.restype = c_int32

        status = config_lib.CFG_getDeviceIdentificationInfo(c_uint32(self.deviceID), pInformationStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return pInformationStruct

    def getDeviceIdentificationInfo(self) -> DeviceIdentifierInformation:
        """Reads and returns the device identifier information of a device.
        
        The device identifier information consists of device type, manufacturer ID,
        manufacturer name, chip type and version number.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                getDeviceManufacturerAsString function failed.
                getDeviceTypeAsString function failed.
                _getDeviceIdentificationInfoPointer function failed.
            TypeError:\n
                Errors from DeviceIdentifierInformation class.\n
            ValueError:\n
                Errors from DeviceIdentifierInformation class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Get device type and manufacturer name
        try:
            manufacturerName = self.getDeviceManufacturerAsString()
        except STARAPIError:
            raise

        # Get device type as string
        try:
            deviceType = self.getDeviceTypeAsString()
        except STARAPIError:
            raise

        # Get other device information
        try:
            pInformationStruct = self._getDeviceIdentificationInfoPointer()
        except STARAPIError:
            raise

        informationStruct = pInformationStruct.contents

        try:
            information = DeviceIdentifierInformation(deviceType, informationStruct.manufacturerID, manufacturerName,
                                                    informationStruct.chipType, informationStruct.versionNum)
        except (TypeError, ValueError):
            raise

        return information

    def getDeviceManufacturerAsString(self) -> str:
        """ If the manufacturer is known, this method returns a string representation of the manufacturer's name.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                _getDeviceIdentificationInfoPointer function failed.\n
                The C API failed to get device manufacturer info.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            deviceIdentifierInfo = self._getDeviceIdentificationInfoPointer()
        except STARAPIError:
            raise

        # Create char *
        manufacturer = create_string_buffer(256)

        # Set argument types and return type of the C function
        config_lib.CFG_getDeviceManufacturerAsString.argtypes = [POINTER(STAR_CFG_DEVICE_IDENTIFIER_INFO), c_char_p]
        config_lib.CFG_getDeviceManufacturerAsString.restype = None

        config_lib.CFG_getDeviceManufacturerAsString(deviceIdentifierInfo, manufacturer)

        return manufacturer.value.decode('utf-8')

    def getDeviceTypeAsString(self) -> str:
        """If the manufacturer and device type is known, this method returns a string
        representation of the device's type.

        This method is compatible with all device types.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                _getDeviceIdentificationInfoPointer function failed.\n
                The C API failed to get device type info.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            pDeviceIdentifierInfo = self._getDeviceIdentificationInfoPointer()
        except STARAPIError:
            raise

        # Create char *
        deviceType = create_string_buffer(256)

        # Set argument types and return type of the C function
        config_lib.CFG_getDeviceTypeAsString.argtypes = [POINTER(STAR_CFG_DEVICE_IDENTIFIER_INFO), c_char_p]
        config_lib.CFG_getDeviceTypeAsString.restype = None

        config_lib.CFG_getDeviceTypeAsString(pDeviceIdentifierInfo, deviceType)

        return deviceType.value.decode('utf-8')

    def getNetworkDiscoveryInfo(self) -> NetworkDiscoveryInformation:
        """Reads the network discovery information of a device.
        Returns a NetworkDiscoveryInformation object.

        This information can be used by a network manager to determine the layout of the network.

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get network discovery info.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to the Structure to be passed into the C library function
        pInformationStruct = pointer(STAR_CFG_NETWORK_DISCOVERY_INFO())

        # Set argument types and return type of the C function
        config_lib.CFG_getNetworkDiscoveryInfo.argtypes = [c_uint32, POINTER(STAR_CFG_NETWORK_DISCOVERY_INFO)]
        config_lib.CFG_getNetworkDiscoveryInfo.restype = c_int32

        status = config_lib.CFG_getNetworkDiscoveryInfo(c_uint32(self.deviceID), pInformationStruct)

        # Check that the C library function call succeeded
        if status < 0:
            raise STARAPIError(StatusCodes.getMessage(status))

        informationStruct = pInformationStruct.contents

        cfgDeviceType = STAR_CFG_DEVICE_TYPE(informationStruct.deviceType)

        information = NetworkDiscoveryInformation(cfgDeviceType,
                                                  informationStruct.returnPort,
                                                  informationStruct.runningPortsMask,
                                                  informationStruct.runningPortsCount,
                                                  informationStruct.portCount)

        return information

    def getRoutingTableEntry(self, logicalAddress) -> RoutingTableEntry:
        """Gets a routing table entry for a given logical address.
        Returns a `STAR_system.STAR_structure_classes.RoutingTableEntry` object.

        This method is compatible with all device types.

        Args:\n
            logicalAddress (int): Logical address to get the routing table entry for.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the routing table entry.\n
            TypeError:\n
                logicalAddress was not an int.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(logicalAddress) != int:
            raise TypeError("logicalAddress must be int.")

        # Create pointer to structure that will be passed into the C library function
        pRoutingTableEntryStruct = pointer(STAR_CFG_GAR_ENTRY())

        # Set argument types and return type of the C function
        config_lib.CFG_getRoutingTableEntry.argtypes = [c_uint32, c_uint8, POINTER(STAR_CFG_GAR_ENTRY)]
        config_lib.CFG_getRoutingTableEntry.restype = c_int32

        status = config_lib.CFG_getRoutingTableEntry(c_uint32(self.deviceID), logicalAddress, pRoutingTableEntryStruct)

        if status < 0:
            raise STARAPIError(StatusCodes.getMessage(status))

        routingTableEntryStruct = pRoutingTableEntryStruct.contents
        routingTableEntry = RoutingTableEntry(routingTableEntryStruct.portMask,
                                              routingTableEntryStruct.priority,
                                              routingTableEntryStruct.deleteHeader,
                                              routingTableEntryStruct.invalidAddress)

        return routingTableEntry

    def setRoutingTableEntry(self, logicalAddress, entry):
        """Sets a routing table entry for a given logical address.

        This method is compatible with all device types.

        Args:\n
            logicalAddress (int): The logical address value of the routing table entry to be updated.
            entry (STAR_system.STAR_structures.STAR_CFG_GAR_ENTRY): The routing table entry to be set.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the routing table entry.\n
            TypeError:\n
                logicalAddress was not an int.\n
                entry was not a STAR_CFG_GAR_ENTRY.\n

        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(logicalAddress) != int:
            raise TypeError("currentLogicalAddress must be int.")
        if isinstance(entry, STAR_CFG_GAR_ENTRY) is False:
            raise TypeError("entry must be STAR_CFG_GAR_ENTRY.")

        # Get pointer to entry
        pRoutingTableEntryStruct = pointer(entry)

        # Set argument types and return type of the C function
        config_lib.CFG_setRoutingTableEntry.argtypes = [c_uint32, c_uint8, POINTER(STAR_CFG_GAR_ENTRY)]
        config_lib.CFG_setRoutingTableEntry.restype = c_int32

        # Update entry
        status = config_lib.CFG_setRoutingTableEntry(c_uint32(self.deviceID), logicalAddress,
                                                     pRoutingTableEntryStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getGeneralPurpose(self) -> int:
        """Gets and returns the value of the general purpose register.

        This is a user-defined 32-bit value that can be set by the user as required for their
        purposes. This value has no effect on the operation of the router.

        This method is compatible with all device types.
        
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the value of the general purpose register.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        genPurpose = c_uint32(0)
        pGenPurpose = pointer(genPurpose)

        # Set argument types and return type of the C function
        config_lib.CFG_getGeneralPurpose.argtypes = [c_uint32, POINTER(c_uint32)]
        config_lib.CFG_getGeneralPurpose.restype = c_int32

        status = config_lib.CFG_getGeneralPurpose(c_uint32(self.deviceID), pGenPurpose)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return genPurpose.value

    def setGeneralPurpose(self, value):
        """Sets the value of the general purpose register.

        This is a user-defined 32-bit value that can be set by the user as required for their
        purposes. This value has no effect on the operation of the router.

        This method is compatible with all device types.

        Args:\n
            value (int): Value to set the general purpose register to.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the value of the general purpose register.\n
            TypeError:\n
                value was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(value) != int:
            raise TypeError("value must be int.")

        # Set argument types and return type of the C function
        config_lib.CFG_setGeneralPurpose.argtypes = [c_uint32, c_uint32]
        config_lib.CFG_setGeneralPurpose.restype = c_int32

        status = config_lib.CFG_setGeneralPurpose(c_uint32(self.deviceID), c_uint32(value))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getNetworkIdentity(self) -> int:
        """Gets and returns the value of the network identity register.

        This is a 32-bit value that can be used to identify the device, typically set by a 
        network manager. It may also be used for any other purpose. This value has no effect
        on the operation of the router.

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the network identity.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be passed into the C library function
        networkID = c_uint32(0)
        pNetworkID = pointer(networkID)

        # Set argument types and return type of the C function
        config_lib.CFG_getNetworkIdentity.argtypes = [c_uint32, POINTER(c_uint32)]
        config_lib.CFG_getNetworkIdentity.restype = c_int32

        status = config_lib.CFG_getNetworkIdentity(c_uint32(self.deviceID), pNetworkID)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return networkID.value

    def getTimeCodeDistributionPorts(self) -> list:
        """This method is used to obtain which output ports time-codes are forwarded on.
        Returns a list of `STAR_system.port.Port` objects on which time-code distribution is enabled.

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get time-code distribution ports info.\n
            TypeError:\n
                Errors from Port class.\n
            ValueError:\n
                Errors from Port class.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be passed into the C library function
        portMask = c_uint32(0)
        pPortMask = pointer(portMask)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimeCodeDistributionPorts.argtypes = [c_uint32, POINTER(c_uint32)]
        config_lib.CFG_getTimeCodeDistributionPorts.restype = c_int32

        status = config_lib.CFG_getTimeCodeDistributionPorts(c_uint32(self.deviceID), pPortMask)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        # First two characters are 0b
        portMaskStr = bin(portMask.value)[2:]

        ports = []
        for i in range(len(portMaskStr) - 1, -1, -1):
            bit = portMaskStr[i]
            portNumber = len(portMaskStr) - i - 1

            if bool(int(bit)):
                try:
                    port = Port(self.deviceID, portNumber)
                except (TypeError, ValueError):
                    raise

                ports.append(port)  # bit 0 corresponds to port 1

        return ports

    def setNetworkIdentity(self, value):
        """Sets the value of the network identity register.

        This is a 32-bit value that can be used to identify the device, typically set by a
        network manager. It may also be used for any other purpose. This value has no effect on
        the operation of the router.

        This method is compatible with all device types.

        Args:\n
            value (int): Value to set the network identity for.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the network identify.\n
            TypeError:\n
                value was not an int.\n
            ValueError:\n
                value was negative.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(value) != int:
            raise TypeError("value must be int.")
        if value < 0:
            raise ValueError("Network identity value cannot be negative.")

        # Set argument types and return type of the C function
        config_lib.CFG_setNetworkIdentity.argtypes = [c_uint32, c_uint32]
        config_lib.CFG_setNetworkIdentity.restype = c_int32

        status = config_lib.CFG_setNetworkIdentity(c_uint32(self.deviceID), c_uint32(value))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def setTimeCodeDistributionPorts(self, ports):
        """This method is used to specify which output ports time-codes are forwarded on.

        This method is compatible with all device types.

        Args:\n
            ports (list of Port objects): The port numbers of the ports that time-code distribution
                should be enabled on. Valid port numbers to forward time-codes on are 1 through 11.
                Not all external ports allow time-code forwarding. Check your device's user manual for more details.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API returned an error code.\n
            TypeError:\n
                portNumbers was not a list of ints.\n
            ValueError:\n
                One or more of the port numbers was not in the range 1 to 11 inclusive,
                or one or more of the ports was not associated with this device.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if isinstance(ports, list) is False:
            raise TypeError("Ports parameter must be of type list.")
        for port in ports:
            if isinstance(port, Port) is False:
                raise TypeError("All items in ports list must be an instance of Port.")
            if port.owningDeviceID != self.deviceID:
                raise ValueError("Input ports must be associated with this device, ID " + str(self.deviceID) + ".")
            if port.portNumber < 1 or port.portNumber > 11:
                raise ValueError("Valid port numbers are 1 to 11 inclusive.")
            
        portMaskList = ["0"] * 11
        for port in ports:
            # Bit 1 corresponds to port 1.
            portMaskList[-port.portNumber-1] = "1"

        portMaskStr = ""
        for port in portMaskList:
            portMaskStr += port

        portMaskInt = int(portMaskStr, 2)

        # Set argument types and return type of the C function
        config_lib.CFG_setTimeCodeDistributionPorts.argtypes = [c_uint32, c_uint32]
        config_lib.CFG_setTimeCodeDistributionPorts.restype = c_int32

        status = config_lib.CFG_setTimeCodeDistributionPorts(c_uint32(self.deviceID), c_uint32(portMaskInt))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getRouterGlobalSettings(self) -> RouterGlobalState:
        """Gets and returns the router's global settings.
        Returns a `STAR_system.STAR_structure_classes.RouterGlobalState` object.

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the router's global settings.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be passed into the C library function
        pStateStruct = pointer(STAR_CFG_ROUTER_GLOBAL_STATE())

        # Set argument types and return type of the C function
        config_lib.CFG_getRouterGlobalSettings.argtypes = [c_uint32, POINTER(STAR_CFG_ROUTER_GLOBAL_STATE)]
        config_lib.CFG_getRouterGlobalSettings.restype = c_int32

        status = config_lib.CFG_getRouterGlobalSettings(c_uint32(self.deviceID), pStateStruct)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        
        stateStruct = pStateStruct.contents

        timeoutMode = STAR_CFG_TIMEOUT_MODE(stateStruct.timeoutMode)

        timeoutPeriod = STAR_CFG_PORT_TIMEOUT(stateStruct.timeoutPeriod)

        # Convert bytes object to boolean value
        if len(stateStruct.startOnRequest) != 1:
            raise STARAPIError("Could not retrieve startOnRequest (Global Router) setting.")
        else:
            startOnRequest = bool(stateStruct.startOnRequest[0])

        # Convert bytes object to boolean value
        if len(stateStruct.disableOnSilence) != 1:
            raise STARAPIError("Could not retrieve disableOnSilence (Global Router) setting.")
        else:
            disableOnSilence = bool(stateStruct.disableOnSilence[0])

        # Convert bytes object to boolean value
        if len(stateStruct.enableSelfAddressing) != 1:
            raise STARAPIError("Could not retrieve enableSelfAddressing (Global Router) setting.")
        else:
            enableSelfAddressing = bool(stateStruct.enableSelfAddressing[0])

        state = RouterGlobalState(timeoutMode, timeoutPeriod, startOnRequest, disableOnSilence, enableSelfAddressing)

        return state

    def getTimeCodeFlagMode(self) -> int:
        """Obtains the time-code flag interpretation mode:

        Returns:
            0 - Time-code control bit flags are distributed with valid time-code values regardless
        of the value of the time-code control flags.\n

        1 - When the time-code control bit flags are "00" then valid time-codes are distributed.
        When the time-code control flags are not "00" then the time-code is discarded and the
        internal time-code register is not updated.\n

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get time-code flag mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be used as an input parameter for the C library function call
        mode = c_uint8(0)
        pMode = pointer(mode)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimeCodeFlagMode.argtypes = [c_uint32, POINTER(c_uint8)]
        config_lib.CFG_getTimeCodeFlagMode.restype = c_int32

        status = config_lib.CFG_getTimeCodeFlagMode(c_uint32(self.deviceID), pMode)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return mode.value

    def getTimeCodeValue(self):
        """Obtains and returns the current value of the router's internal time-code counter.

        This method is compatible with all device types.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the time-code value.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be used as an input parameter for the C library function call
        val = c_uint8(0)
        pValue = pointer(val)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimeCodeValue.argtypes = [c_uint32, POINTER(c_uint8)]
        config_lib.CFG_getTimeCodeValue.restype = c_int32

        status = config_lib.CFG_getTimeCodeValue(c_uint32(self.deviceID), pValue)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return val.value

    def setRouterGlobalSettings(self, state):
        """ Sets the router's global settings.

        This method is compatible with all device types.

        Args:\n
            state (RouterGlobalState): Global settings for the router.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API returned an error code.\n
            TypeError:\n
                state was not an instance of RouterGlobalState.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if isinstance(state, RouterGlobalState) is False:
            raise TypeError("state must be a RouterGlobalState.")

        stateStruct = STAR_CFG_ROUTER_GLOBAL_STATE(state.timeoutMode.value,
                                                   state.timeoutPeriod.value,
                                                   c_char(state.disableOnSilence),
                                                   c_char(state.startOnRequest),
                                                   c_char(state.enableSelfAddressing))
        pStateStruct = pointer(stateStruct)

        # Set argument types and return type of the C function
        config_lib.CFG_setRouterGlobalSettings.argtypes = [c_uint32, POINTER(STAR_CFG_ROUTER_GLOBAL_STATE)]
        config_lib.CFG_setRouterGlobalSettings.restype = c_int32

        status = config_lib.CFG_setRouterGlobalSettings(c_uint32(self.deviceID), pStateStruct)
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def setTimeCodeFlagMode(self, mode):
        """Sets the time-code flag interpretation mode:

        This method is compatible with all device types.

        Args:\n
            mode (int): Mode to set the time code flag mode to.

            0 - Time-code control bit flags are distributed with valid time-code values regardless
            of the value of the time-code control flags.

            1 - When the time-code control bit flags are "00" then the valid time-code are
            distributed. When the time-code control flags are not "00" then the time-code is
            discarded and the internal time-code register is not updated.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the time-code flag mode.\n
            TypeError:\n
                mode argument was not an int.\n
            ValueError:\n
                mode was not 0 or 1.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(mode) != int:
            raise TypeError("mode must be int.")
        if mode not in [0, 1]:
            raise ValueError("mode must be 0 or 1.")

        # Set argument types and return type of the C function
        config_lib.CFG_setTimeCodeFlagMode.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_setTimeCodeFlagMode.restype = c_int32

        status = config_lib.CFG_setTimeCodeFlagMode(c_uint32(self.deviceID), c_uint8(mode))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disablePrecisionTransmitRate(self):
        """Disables precision transmit rate on a Router Mk2S device.

        Precision transmit rate allows the transmit rate of the device to be 
        expressed accurately in Mbit/s as a floating point number using the method
        `STAR_system.device_config.DeviceConfig.setPrecisionTransmitRate`.\n
        Note that after being disabled there may be a short delay (less than 250 microseconds) before precision
        transmit rate is actually disabled.\n
        Call `STAR_system.device_config.DeviceConfig.getPrecisionTransmitRateInUse` to determine if precision transmit
        rate is no longer in use.

        This method is only compatible with the Router Mk2S.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable precision transmit rate.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disablePrecisionTransmitRate.argtypes = [c_uint32]
        config_lib.CFG_disablePrecisionTransmitRate.restype = c_int32

        status = config_lib.CFG_disablePrecisionTransmitRate(c_uint32(self.deviceID))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enablePrecisionTransmitRate(self):
        """Enables precision transmit rate on a Router Mk2S device.

        Precision transmit rate allows the transmit rate of the device to be expressed
        accurately in Mbit/s as a floating point number using the method
        `STAR_system.device_config.DeviceConfig.setPrecisionTransmitRate()`.\n
        Note that after being enabled it can take up to 250 microseconds before precision transmit rate is actually used.\n
        Call `STAR_system.device_config.DeviceConfig.getPrecisionTransmitRateInUse()` to determine if precision transmit rate is
        actually in use.

        This method is only compatible with the Router Mk2S.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable precision transmit rate.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enablePrecisionTransmitRate.argtypes = [c_uint32]
        config_lib.CFG_enablePrecisionTransmitRate.restype = c_int32

        status = config_lib.CFG_enablePrecisionTransmitRate(c_uint32(self.deviceID))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getPrecisionTransmitRate(self) -> float:
        """Gets and returns the current precision transmit rate on a Router Mk2S device in Mbit/s.

        Precision transmit rate allows the transmit rate of the device to be expressed
        accurately in Mbit/s as a floating point number using the method
        `STAR_system.device.Device.setPrecisionTransmitRate()`.

        This method is only compatible with the Router Mk2S.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the precision transmit rate.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        precisionTransmitRate = c_double(0)
        pPrecisionTransmitRate = pointer(precisionTransmitRate)

        # Set argument types and return type of the C function
        config_lib.CFG_getPrecisionTransmitRate.argtypes = [c_uint32, POINTER(c_double)]
        config_lib.CFG_getPrecisionTransmitRate.restype = c_int32

        status = config_lib.CFG_getPrecisionTransmitRate(c_uint32(self.deviceID), pPrecisionTransmitRate)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return precisionTransmitRate.value

    def getPrecisionTransmitRateEnabled(self) -> bool:
        """Determines if precision transmit rate is enabled on a Router Mk2S device.
        Returns True if precision transmit rate is enabled, False otherwise.

        Precision transmit rate allows the transmit rate of the device to be expressed
        accurately in Mbit/s as a floating point number using the method 
        `STAR_system.device.Device.setPrecisionTransmitRate()`.\n
        Note that although precision transmit rate may be enabled, it may not yet be in use.
        It can take up to 250 microseconds before precision transmit rate is actually used.

        Call `STAR_system.device.Device.getPrecisionTransmitRateInUse()` to determine if precision transmit rate is actually in use.

        This method is only compatible with the Router Mk2S.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether precision transmit rate is enabled or not.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be used as an input parameter for the C library function call
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getPrecisionTransmitRateEnabled.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getPrecisionTransmitRateEnabled.restype = c_int32

        status = config_lib.CFG_getPrecisionTransmitRateEnabled(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return bool(enabled.value)

    def getPrecisionTransmitRateInUse(self) -> bool:
        """Determines whether precision transmit rate is in use on a Router Mk2S device.
        Returns True if precision transmit rate is in use, False otherwise.
        
        After being enabled or disabled, it can take up o 250 microseconds before precision
        transmit is actually used or not used. This function determines whether precision
        transmit rate is currently in use and can be used to determine if an enable or disable
        operation has completed.

        This method is only compatible with the Router Mk2S.
            
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether precision transmit rate is in use or not.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be used as an input parameter for the C library function call
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getPrecisionTransmitRateInUse.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getPrecisionTransmitRateInUse.restype = c_int32

        status = config_lib.CFG_getPrecisionTransmitRateInUse(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))
        else:
            return bool(enabled.value)

    def setPrecisionTransmitRate(self, transmitRate):
        """Set the current precision transmit rate on a Router Mk2S device in Mbit/s.

        Precision transmit rate allows the transmit rate of the device to be expressed accurately
        in Mbit/s as a floating point number.

        This method is only compatible with the Router Mk2S.

        Args:\n
            transmitRate (int or float): Valid values are between 2 and 200 (inclusive).

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set precision transmit rate.\n
            TypeError:\n
                transmitRate was not a number (int or float).
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(transmitRate) not in [int, float]:
            raise TypeError("transmitRate must be a number (int or float).")

        # Create input variable
        cTransmitRate = c_double(transmitRate)

        # Set argument types and return type of the C function
        config_lib.CFG_setPrecisionTransmitRate.argtypes = [c_uint32, c_double]
        config_lib.CFG_setPrecisionTransmitRate.restype = c_int32

        status = config_lib.CFG_setPrecisionTransmitRate(c_uint32(self.deviceID), cTransmitRate)
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def updateDeviceInfo(self):
        """This method is used to update the device's information held in the shared memory.

        This is only required for remote devices if they have been removed and replaced.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to update device info.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_updateDeviceInfo.argtypes = [c_uint32]
        config_lib.CFG_updateDeviceInfo.restype = c_int32

        status = config_lib.CFG_updateDeviceInfo(c_uint32(self.deviceID))
        
        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Unable to update the device's information in shared memory.")

    def getPulseGeneratorFrequency(self) -> STAR_CFG_BRICK_MK3_PULSE_FREQ:
        """Gets and returns the frequency of each generated pulse.

        This method is compatible with the Brick Mk3/Mk4, GbE brick and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the pulse generator frequency.\n
            ValueError:\n
                The returned value could not be converted into an enum.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be used as an input parameter for the C library function call
        pulseFrequency = c_int32(0)
        pPulseFrequency = pointer(pulseFrequency)

        # Set argument types and return type of the C function
        config_lib.CFG_getPulseGeneratorFrequency.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getPulseGeneratorFrequency.restype = c_int32

        status = config_lib.CFG_getPulseGeneratorFrequency(c_uint32(self.deviceID), pPulseFrequency)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        # Try to create enum from the returned value
        try:
            pulseFrequencyStateEnum = STAR_CFG_BRICK_MK3_PULSE_FREQ(pulseFrequency.value)
        except ValueError:
            raise STARAPIError("Returned pulse frequency value was invalid.")

        return pulseFrequencyStateEnum

    def setPulseGeneratorFrequency(self, frequency):
        """Sets the frequency of each generated pulse.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick and PXI devices.

        Args:\n
            frequency (STAR_system.STAR_enums.STAR_CFG_BRICK_MK3_PULSE_FREQ): The frequency value to set.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API could not successfully set the pulse generator frequency.\n
            TypeError:\n
                frequency was not a STAR_CFG_BRICK_MK3_PULSE_FREQ.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if isinstance(frequency, STAR_CFG_BRICK_MK3_PULSE_FREQ) is False:
            raise TypeError("frequency must be STAR_CFG_BRICK_MK3_PULSE_FREQ.")

        # Set argument types and return type of the C function
        config_lib.CFG_setPulseGeneratorFrequency.argtypes = [c_uint32, STAR_CFG_BRICK_MK3_PULSE_FREQ]
        config_lib.CFG_setPulseGeneratorFrequency.restype = c_int32

        status = config_lib.CFG_setPulseGeneratorFrequency(c_uint32(self.deviceID), frequency)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getTimestampMethod(self) -> STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD:
        """Gets and returns the timestamping method that is currently in use for the device.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick, and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the timestamp method.\n
            ValueError:\n
                The returned value could not be converted into an enum.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be used as an input parameter for the C library function call
        methodInt = c_int32(0)
        pMethodInt = pointer(methodInt)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimestampMethod.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getTimestampMethod.restype = c_int32

        status = config_lib.CFG_getTimestampMethod(c_uint32(self.deviceID), pMethodInt)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        # Try to create enum from the returned value
        try:
            timestampMethodEnum = STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD(methodInt.value)
        except ValueError:
            raise STARAPIError("Returned timestamp method was invalid.")

        return timestampMethodEnum

    def setTimestampMethod(self, timestampMethod):
        """Sets the timestamping method to use for this device.

        The Brick Mk3/Mk4 will trigger on the rising edge of the external pulse but the
        Triggering API can be used to change it to trigger on the falling edge using
        `STAR_system.triggering_conf.TriggeringConfiguration.enableExtTriggerEdgeDetectMode()` and
        `STAR_system.triggering_conf.TriggeringConfiguration.enableExtTriggerInvert()`.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick and PXI devices.

        Args:\n
            timestampMethod (STAR_system.STAR_enums.STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD): The timestamp method to enable for this device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the timestamp method.\n
            TypeError:\n
                timestampMethod was not a STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if isinstance(timestampMethod, STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD) is False:
            raise TypeError("timestampMethod must be STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD.")

        # Set argument types and return type of the C function
        config_lib.CFG_setTimestampMethod.argtypes = [c_uint32, STAR_CFG_BRICK_MK3_TIMESTAMP_METHOD]
        config_lib.CFG_setTimestampMethod.restype = c_int32

        status = config_lib.CFG_setTimestampMethod(c_uint32(self.deviceID), timestampMethod)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getTimestampValue(self) -> int:
        """Gets and returns the current timestamp value.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick and PXI devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the timestamp value.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer that will be used as an input parameter for the C library function call
        timestampValue = c_uint32(0)
        pTimestampValue = pointer(timestampValue)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimestampValue.argtypes = [c_uint32, POINTER(c_uint32)]
        config_lib.CFG_getTimestampValue.restype = c_int32

        status = config_lib.CFG_getTimestampValue(c_uint32(self.deviceID), pTimestampValue)
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return timestampValue.value

    def setTimestampValue(self, value):
        """Sets the current timestamp value for the device.

        This value will be incremented on the next synchronisation pulse.

        This method is compatible with the Brick Mk3/Mk4, GbE Brick, and PXI devices.

        Args:\n
            value (int): Timestamp value to set for device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the timestamp value.\n
            TypeError:\n
                value was not an int.
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(value) != int:
            raise TypeError("value must be int.")

        # Set argument types and return type of the C function
        config_lib.CFG_setTimestampValue.argtypes = [c_uint32, c_uint32]
        config_lib.CFG_setTimestampValue.restype = c_int32

        status = config_lib.CFG_setTimestampValue(c_uint32(self.deviceID), c_uint32(value))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getDeviceClockRate(self) -> int:
        """Gets the device's internal clock rate.
        The returned clock rate is in Hz.

        This method is only compatible with PCI Mk2 devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The device does not support periodic actions.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_getDeviceClockRate.argtypes = [c_uint32]
        config_lib.CFG_getDeviceClockRate.restype = c_int32

        clockRate = config_lib.CFG_getDeviceClockRate(c_uint32(self.deviceID))

        if clockRate <= 0:
            raise STARAPIError("The device does not support this functionality or an error occurred.")
        else:
            return clockRate

    def disableTimeCodeCounterBypassMode(self):
        """Disables time-code counter bypass mode for this device.

        When time-code counter bypass mode is disabled, any time-code which is received
        will be checked against the current value of the counter for validity before
        being forwarded.

        This method is only compatible with PCIe devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable time-code counter bypass mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableTimeCodeCounterBypassMode.argtypes = [c_uint32]
        config_lib.CFG_disableTimeCodeCounterBypassMode.restype = c_int32

        status = config_lib.CFG_disableTimeCodeCounterBypassMode(c_uint32(self.deviceID))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableTimeCodeCounterBypassMode(self):
        """Enables time-code counter bypass mode for this device.

        When time-code counter bypass mode is enabled, any time-code which is received will
        be forwarded out of the other ports on the router, without checking against the
        current value of the counter. The time-code register will be updated on each received
        time-code.

        This method is only compatible with PCIe devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable time-code counter bypass mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableTimeCodeCounterBypassMode.argtypes = [c_uint32]
        config_lib.CFG_enableTimeCodeCounterBypassMode.restype = c_int32

        status = config_lib.CFG_enableTimeCodeCounterBypassMode(c_uint32(self.deviceID))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getTimeCodeCounterBypassModeEnabled(self) -> bool:
        """Gets whether time-code counter bypass mode has been enabled for this device.
        Returns True if time-code counter bypass mode is enabled, False otherwise.

        When time-code counter bypass mode is disabled, any time-code which is 
        received will be check against the current value of the counter for 
        validity before being forwarded. When time-code counter bypass mode is 
        enabled, any time-code which is received will be forwarded out of the 
        other ports on the router, without checking against the current value of 
        the counter. The time-code register will be updated on each received 
        time-code.

        This method is only compatible with PCIe devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether time-code counter bypass mode is enabled or not.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getTimeCodeCounterBypassModeEnabled.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getTimeCodeCounterBypassModeEnabled.restype = c_int32

        # Create pointer that will be used as an input parameter for the C library function call
        status = config_lib.CFG_getTimeCodeCounterBypassModeEnabled(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def enableBroadcastControllerLegacyMode(self):
        """Enables broadcast controller legacy mode. When enabled, all broadcast codes
        are interpreted as time-codes. Codes which do not have flags field set
        to 0b00 (time-code) will be forwarded according to the time-code flag mode.

        This method is only compatible with PCIe Mk2 device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable broadcast controller legacy mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableBroadcastControllerLegacyMode.argtypes = [c_uint32]
        config_lib.CFG_enableBroadcastControllerLegacyMode.restype = c_int32

        # Create pointer that will be used as an input parameter for the C library function call
        status = config_lib.CFG_enableBroadcastControllerLegacyMode(c_uint32(self.deviceID))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableBroadcastControllerLegacyMode(self):
        """Disables broadcast controller legacy mode. When disabled, interrupt
        codes are supported. A broadcast code with type field 0b00 is
        interpreted as a time-code. A broadcast code with type field 0b10 is
        interpreted as a distributed interrupt. Broadcasts with type fields
        equal to 0b01 or 0b11 are discarded.

        This method is only compatible with PCIe Mk2 device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable broadcast controller legacy mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableBroadcastControllerLegacyMode.argtypes = [c_uint32]
        config_lib.CFG_disableBroadcastControllerLegacyMode.restype = c_int32

        # Create pointer that will be used as an input parameter for the C library function call
        status = config_lib.CFG_disableBroadcastControllerLegacyMode(c_uint32(self.deviceID))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getBroadcastControllerLegacyModeEnabled(self) -> bool:
        """Gets whether broadcast legacy mode has been enabled for the device.
        When broadcast legacy mode is disabled, interrupt codes are supported.
        A broadcast code with type field 0b00 is interpreted as a time-code.
        A broadcast code with type field 0b10 is interpreted as a distributed
        interrupt. Broadcasts with type fields equal to 0b01 or 0b11 are discarded.
        When broadcast legacy mode is enabled, all broadcast codes are interpreted
        as time-codes. Codes which do not have flags field set to 0b00 (time-code)
        will be forwarded according to the time-code flag mode.

        This method is only compatible with PCIe Mk2 device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get broadcast controller legacy mode flag value.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getBroadcastControllerLegacyModeEnabled.argtypes = [c_uint32, POINTER(c_int32)]
        config_lib.CFG_getBroadcastControllerLegacyModeEnabled.restype = c_int32

        # Create pointer that will be used as an input parameter for the C library function call
        status = config_lib.CFG_getBroadcastControllerLegacyModeEnabled(c_uint32(self.deviceID), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def setInterruptCodeDistributionPorts(self, portMask):
        """This function is used to specify which output ports interrupt codes are
        forwarded on.

        This method is only compatible with PCIe Mk2 device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set interrupt code distribution ports.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(portMask) != int:
            raise TypeError("portMask must be int.")

        # Set argument types and return type of the C function
        config_lib.CFG_setInterruptCodeDistributionPorts.argtypes = [c_uint32, c_uint32]
        config_lib.CFG_setInterruptCodeDistributionPorts.restype = c_int32

        # Create pointer that will be used as an input parameter for the C library function call
        status = config_lib.CFG_setInterruptCodeDistributionPorts(c_uint32(self.deviceID), c_uint32(portMask))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getInterruptCodeDistributionPorts(self) -> int:
        """This function is used to obtain which output ports interrupt codes are forwarded on.

        This method is only compatible with PCIe Mk2 device.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get interrupt code distribution ports.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        portMask = c_uint32(0)
        pPortMask = pointer(portMask)

        # Set argument types and return type of the C function
        config_lib.CFG_getInterruptCodeDistributionPorts.argtypes = [c_uint32, POINTER(c_uint32)]
        config_lib.CFG_getInterruptCodeDistributionPorts.restype = c_int32

        # Create pointer that will be used as an input parameter for the C library function call
        status = config_lib.CFG_getInterruptCodeDistributionPorts(c_uint32(self.deviceID), pPortMask)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return int(portMask.value)
